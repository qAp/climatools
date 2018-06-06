


import os
import pprint
import subprocess
import collections
import shutil
import time
import itertools
import re

import climatools.clirad.info as cliradinfo



CLIRADLW_BANDS = cliradinfo.wavenumber_bands(region='lw')

# Specify the directory in which 'lblnew.f' is kept.
DIR_SRC = os.path.join('/chia_cluster/home/jackyu/radiation/crd',
                       'LW/src',
                       'lblnew_-_overlap')

FNAME_CODE = 'lblnew-overlap.f'

FNAME_IPYNB = 'results_overlap.ipynb'

# Path for the template analysis notebook.
PATH_IPYNB = os.path.join('/chia_cluster/home/jackyu',
                         'climatools/climatools/lblnew',
                          FNAME_IPYNB)



def get_dir_from_param(param):
    '''
    Returns the directory path that describes the case 
    specified by the input parameters.  

    Parameters
    ----------
    param: dict
           Dictionary containing the keys and values of input parameters.
    '''
    molecules = ('h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2')

    template = os.path.join( 
        'h2o_{h2o}_co2_{co2}_o3_{o3}_n2o_{n2o}_ch4_{ch4}_o2_{o2}',
        'band0{band}_wn_{vmin:d}_{vmax:d}',
        'nv_{nv:d}',
        'dv_{dv}',
        'crd_{commitnumber}',
        'atmpro_{atmpro}')

    molecule_concs = {}
    for m in molecules:
        if m in param['molecule']:
            molecule_concs[m] = str(param['molecule'][m])
        else:
            molecule_concs[m] = '0'    

    vmin, vmax = CLIRADLW_BANDS[param['band']][0]

    return template.format(band=param['band'], vmin=vmin, vmax=vmax,
                           nv=param['nv'],
                           dv=param['dv'],
                           commitnumber=param['commitnumber'],
                           atmpro=param['atmpro'],
                           **molecule_concs)



def pattern_assign(name):
    '''
    Returns regular expression for a Fortran 
    parameter variable assignment.
    '''
    return ''' 
    (parameter .* :: \s* &? \s* {} \s* = )(.*)
    '''.format(name)



def pattern_data(name):
    '''
    Returns regular expression for a Fortran
    'data' variable assignment
    '''
    return '''
    (data [^/{name}]+ {name}[^,] [^/{name}]+ / )([^/]+)
    '''.format(name=name)



def pattern_atmpro():
    '''
    Returns regular expression that matches
    the assignment of the atmosphere profile
    used in lblnew.f.
    '''
    return '''
    (atmosphere_profiles/)([a-z]{3,3})
    '''



def pattern_molecule():
    '''
    Returns regular expression that matches 
    the assignment of molecule flags in lblnew.f.
    '''
    return '''
    (
    data \s+  
    flgh2o \s*,\s* flgco2 \s*,\s* flgo3 \s*,\s* flgn2o \s*,\s*
    flgch4 \s*,\s* flgo2
    \n 
    \s* \* \s* / \s* 
    )
    (
    [01] \s* , \s* [01] \s* , \s*  [01] \s* , \s* [01] \s* , \s* [01] 
    \s* , \s* [01]
    )
    '''



def pattern_conc(name):
    '''
    Returns regular expression that matches where
    the assignment of the concentration of a molecule
    can be inserted such that it will override anything
    else provided.
    '''
    d = {'h2o': {'gasid': 1, 'concname': 'wlayer'},
         'co2': {'gasid': 2, 'concname': 'clayer'}, 
         'o3' : {'gasid': 3, 'concname': 'olayer'},
         'n2o': {'gasid': 4, 'concname': 'qlayer'},
         'ch4': {'gasid': 5, 'concname': 'rlayer'}}

    assert name in d

    return '''
      (if \s+ \(flag\( {gasid} \)\) \s+ then \s+        
      {concname} \s+ = \s+ ) (.*) 
    '''.format(gasid=d[name]['gasid'], 
               concname=d[name]['concname'])



def enter_input_params(path_lblnew, params=None):
    '''
    Insert input values into lblnew.f

    Parameters
    ----------
    path_lblnew: string
        Path to the lblnew.f file to be edited.
    params: dict
        Dictionary of input values.  The keys and values
        are the names and values of the input parameters.
    '''
    molecules = ('h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2')
    
    with open(path_lblnew, mode='r', encoding='utf-8') as f:
        code = f.read()
    
    d_in = collections.defaultdict(dict)
    
    molecule_flags = [1 if m in params['molecule'] else 0 
                      for m in molecules]
    input_value = '   ,   '.join([str(flg) for flg in molecule_flags])
    d_in['molecule']['regex'] = pattern_molecule()
    d_in['molecule']['input_value'] = input_value

    'Gas concentration. We leave out o2 for now.'
    molecule_conc = {}
    for name in molecules[:-1]:
        if name in params['molecule']:
            if  name == 'h2o' and params['molecule'][name] == 'atmpro':
                molecule_conc[name] = 'wlayer'
            elif name == 'o3' and params['molecule'][name] == 'atmpro':
                molecule_conc[name] = 'olayer'
            elif params['molecule'][name] == 'atmpro':
                # If 'atmpro' is specified for molecules other than h2o and o3,
                # the concentration is set to 0.
                molecule_conc[name] = '0._r8'
            else:
                molecule_conc[name] = (str(float(params['molecule'][name])) 
                                       + '_r8')
        else:
            molecule_conc[name] = '0._r8'
              
    for name, conc in molecule_conc.items():
        d_in[name]['regex'] = pattern_conc(name=name)
        d_in[name]['input_value'] = str(conc)


    vmin, vmax = CLIRADLW_BANDS[params['band']][0]

    vstar = vmin
    nband = int((vmax - vstar) / (params['nv'] * params['dv']))
    d_in['vstar']['regex'] = pattern_assign(name='vstar')
    d_in['vstar']['input_value'] = ' ' + str(vstar) + '_r8'
    d_in['nband']['regex'] = pattern_assign(name='nband')
    d_in['nband']['input_value'] = ' ' + str(nband)
    d_in['nv']['regex'] = pattern_assign(name='nv')
    d_in['nv']['input_value'] = ' ' + str(params['nv'])
    d_in['dv']['regex'] = pattern_assign(name='dv')
    d_in['dv']['input_value'] = ' ' + str(params['dv']) + '_r8'

    'atmpro'
    d_in['atmpro']['regex'] = pattern_atmpro()
    d_in['atmpro']['input_value'] = params['atmpro']
    
    d_in['tsfc']['regex'] = pattern_assign(name='tsfc')
    d_in['tsfc']['input_value'] = str(params['tsfc']) + '_r8'
    

    for name, d in d_in.items():
        regex = re.compile(d['regex'], re.VERBOSE)
        code = regex.sub(r'\g<1>' + d['input_value'], code)

    with open(path_lblnew, mode='w', encoding='utf-8') as f:
        f.write(code)    



def commit_msg(param):
    '''
    Compose git-commit message for a lblnew case.

    Parameters
    ----------
    param: dict
        Dictionary of input values.  The keys and values                      
        are the names and values of the input parameters.        
    '''

    title = '{molecule} band{band} {atmpro}'
    title = title.format(
        **{n: param[n] for n in ['molecule', 'band', 'atmpro']})
    
    content = ['{}: {}'.format(parameter, value)
               for parameter, value in param.items()]
    
    msg = [title] + content
    msg = [['-m', m] for m in msg]
    return [a for m in msg for a in m]




def test_cases():
    return [{'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6, 'n2o': 3.2e-7},
             'band': '3a',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6},
             'band': '3b',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6},
             'band': '3c',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6},
             'band': '4',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6, 'o3': 'atmpro'},
             'band': '5',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'o3': 'atmpro'},
             'band': '5',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'n2o': 3.2e-7},
             'band': '7',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'n2o': 3.2e-7, 'ch4': 1.8e-6},
             'band': '7',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294},
            {'commitnumber': '5014a19',
             'molecule': {'h2o': 'atmpro', 'co2': 400e-6},
             'band': '9',
             'nv': 1000,
             'dv': .001,
             'atmpro': 'mls',
             'tsfc': 294}]





def test_get_fortran_dir():
    param = {'molecule': ['h2o', 'co2'],
             'band': '3c',
             'nv': 200, 'dv': .005,
             'atmpro': 'mls',
             'commitnumber': '11111'}
    print(get_fortran_dir(param))




if __name__ == '__main__':
    test_get_fortran_dir()
