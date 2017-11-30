


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
                       'lblnew_-_nref_-_autoabsth_klin_-_gasc_kdesc')

# Path for the template analysis notebook.
PATH_IPYNB = os.path.join('/chia_cluster/home/jackyu',
                         'climatools/climatools/lblnew',
                          'results_overlap.ipynb')



def get_dir_from_param(param):
    '''
    Returns the directory path that describes the case 
    specified by the input parameters.  

    Parameters
    ----------
    param: dict
           Dictionary containing the keys and values of input parameters.
    '''
    molecules = ['h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2']

    template = os.path.join( 
        'h2o_{h2o}_co2_{co2}_o3_{o3}_n2o_{n2o}_ch4_{ch4}_o2_{o2}',
        'band0{band}_wn_{vmin:d}_{vmax:d}',
        'nv_{nv:d}',
        'dv_{dv}',
        'crd_{commitnumber}',
        'atmpro_{atmpro}')

    molecules = {m: 1 if m in param['molecule'] else 0 for m in molecules}

    vmin, vmax = CLIRADLW_BANDS[param['band']][0]

    return template.format(band=param['band'], vmin=vmin, vmax=vmax,
                           nv=param['nv'],
                           dv=param['dv'],
                           commitnumber=param['commitnumber'],
                           atmpro=param['atmpro'],
                           **molecules)



def pattern_assign(name):
    '''
    Returns regular expression for a Fortran 
    parameter variable assignment.
    '''
    return ''' 
    parameter .* :: \s* &? \s* ({} \s* = (.*) \n)
    '''.format(name)



def pattern_data(name):
    '''
    Returns regular expression for a Fortran
    'data' variable assignment
    '''
    return '''
    (data [^/{name}]+ {name}[^,] [^/{name}]+ / ([^/]+) /)
    '''.format(name=name)



def pattern_atmpro():
    '''
    Returns regular expression that matches
    the assignment of the atmosphere profile
    used in lblnew.f.
    '''
    return '''
    (atmosphere_profiles/(.*)75_r8.pro)
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
    (
    [01] \s* , \s* [01] \s* , \s*  [01] \s* , \s* [01] \s* , \s* [01] 
    \s* , \s* [01]
    )
    \s* / 
     )
    '''



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
        statement, value = regex.findall(code)[0]
        input_statement = statement.replace(value, d['input_value'])
        code = code.replace(statement, input_statement)

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








def test_get_fortran_dir():
    param = {'molecule': ['h2o', 'co2'],
             'band': '3c',
             'nv': 200, 'dv': .005,
             'atmpro': 'mls',
             'commitnumber': '11111'}
    print(get_fortran_dir(param))




if __name__ == '__main__':
    test_get_fortran_dir()
