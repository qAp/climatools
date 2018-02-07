


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
                       'LW/src', 'lblnew_-_bestfit',
                       'lblnew_-_nref_-_autoabsth_klin_-_gasc_kdesc')

FNAME_IPYNB = 'results.ipynb'

# Path for the template analysis notebook.
PATH_IPYNB = os.path.join('/chia_cluster/home/jackyu',
                          'climatools/climatools/lblnew',
                          FNAME_IPYNB)



def get_dir_from_param(param):
    template = os.path.join( 
        '{molecule}',
        'conc_{conc}',
        'band0{band}_wn_{vmin:d}_{vmax:d}',
        'nv_{nv:d}',
        'dv_{dv}',
        'ng_{ng:d}',
        'g_ascending_k_descending',
        'refPTs_{refPTs}',
        'ng_refs_{ng_refs}',
        'ng_adju_{ng_adju}',
        'getabsth_{getabsth}',
        'absth_{absth}',
        'klin_{klin}',
        'atmpro_{atmpro}',
        'wgt_k_{option_wgt_k}',
        'wgt_{wgt}',
        'wgt_flux_{option_wgt_flux}',
        'w_diffuse_{w_diffuse}',
        'option_compute_ktable_{option_compute_ktable}',
        'option_compute_btable_{option_compute_btable}',
        'crd_{commitnumber}')
    
    nref = len(param['ng_refs'])

    if param['molecule'] == 'h2o' and param['band'] == '1':
        vmin, vmax = 20, 340
    elif param['molecule'] == 'h2o' and param['band'] == '2':
        vmin, vmax = 340, 540
    else:
        vmin, vmax = CLIRADLW_BANDS[param['band']][0]

    ng = sum(param['ng_refs'])
    refPTs = '__'.join(['P_{}_T_{}'.format(*pt) 
                        for pt in param['ref_pts']])
    ng_refs = '__'.join([str(n) for n in param['ng_refs']])
    ng_adju = '__'.join([str(n) for n in param['ng_adju']])
    getabsth = '__'.join(['auto' for _ in range(nref)])
    absth = '__'.join(['dlogN_uniform' for _ in range(nref)])
    wgt = '__'.join(['_'.join([str(w) for w in wgt_ref]) 
                     for wgt_ref in param['wgt']])
    klin = 'none' if param['klin'] == 0 else param['klin']
    w_diffuse = '__'.join(['_'.join([str(w) for w in w_diffuse_ref]) 
                           for w_diffuse_ref in param['w_diffuse']])

    return template.format(molecule=param['molecule'],
                           conc=param['conc'],
                           band=param['band'], vmin=vmin, vmax=vmax,
                           nv=param['nv'],
                           dv=param['dv'],
                           ng=ng,
                           refPTs=refPTs,
                           ng_refs=ng_refs,
                           ng_adju=ng_adju,
                           getabsth=getabsth,
                           absth=absth,
                           wgt=wgt,
                           option_wgt_flux=param['option_wgt_flux'],
                           option_wgt_k=param['option_wgt_k'],
                           klin=klin,
                           w_diffuse=w_diffuse,
                           commitnumber=param['commitnumber'],
                           atmpro=param['atmpro'],
                           option_compute_ktable=param['option_compute_ktable'],
                           option_compute_btable=param['option_compute_btable'])



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

def pattern_conc(name):
    '''
    Returns regular expression that matches where
    the assignment of the concentration of a molecule
    can be inserted such that it will override anything
    else provided.
    '''
    d = {'co2': {'gasid': 2, 'concname': 'clayer'}, 
         'n2o': {'gasid': 4, 'concname': 'qlayer'},
         'ch4': {'gasid': 5, 'concname': 'rlayer'}}

    assert name in d

    return '''
      if \s+ \(flag\( {gasid} \)\) \s+ then \s+        
      ({concname} \s+ = \s+ (.*) \s+ ! .* \n)
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
    
    molecule_flags = [1 if m==params['molecule'] else 0 
                      for m in molecules]
    input_value = '   ,   '.join([str(flg) for flg in molecule_flags])
    d_in['molecule']['regex'] = pattern_molecule()
    d_in['molecule']['input_value'] = input_value

    'Gas concentration'
    if params['molecule'] in ['co2', 'n2o', 'ch4']:
        d_in['conc']['regex'] = pattern_conc(name=params['molecule'])
        d_in['conc']['input_value'] = ' ' + str(params['conc']) + '_r8'
    
    if params['molecule'] == 'h2o' and params['band'] == '1':
        vmin, vmax = 20, 340
    elif params['molecule'] == 'h2o' and params['band'] == '2':
        vmin, vmax = 340, 540
    else:
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
    
    
    p_refs, t_refs = zip(*params['ref_pts'])
    d_in['p_refs']['regex'] = pattern_assign(name='p_refs')
    d_in['t_refs']['regex'] = pattern_assign(name='t_refs')
    d_in['p_refs']['input_value'] = (
        ' (/ ' + 
        ' , '.join([str(p) + '_r8' for p in p_refs]) +
        ' /) ')
    d_in['t_refs']['input_value'] = (
        ' (/ ' + 
        ' , '.join([str(p) + '_r8' for p in t_refs]) +
        ' /) ')
    
    wgt = [w for wgt_ref in params['wgt'] for w in wgt_ref]
    wgt = list(itertools.zip_longest(*(4 * [iter(wgt)])))
    wgt = [[str(v) + '_r8' for v in row if v != None] for row in wgt]
    wgt = [' , '.join(row) for row in wgt]
    input_value = ',\n     &     '.join(wgt)
    d_in['wgt']['regex'] = pattern_data(name='wgt')
    d_in['wgt']['input_value'] = input_value
    
    'nref'
    nref = len(params['ng_refs'])
    d_in['nref']['regex'] = pattern_assign(name='nref')
    d_in['nref']['input_value'] = str(nref) 
    
    'ng'
    ng = sum(params['ng_refs'])
    d_in['ng']['regex'] = pattern_assign(name='ng')
    d_in['ng']['input_value'] = str(ng)
    
    'ng_refs'
    d_in['ng_refs']['regex'] = pattern_assign(name='ng_refs')
    d_in['ng_refs']['input_value'] = (
        ' (/ ' + 
        ' , '.join([str(n) for n in params['ng_refs']]) +
        ' /) ')    

    'ng_adju'
    d_in['ng_adju']['regex'] = pattern_assign(name='ng_adju')
    d_in['ng_adju']['input_value'] = (
        ' (/ ' + 
        ' , '.join([str(n) for n in params['ng_adju']]) +
        ' /) ')
    
    'option_wgt_flux'
    d_in['option_wgt_flux']['regex'] = pattern_assign(name='option_wgt_flux')
    d_in['option_wgt_flux']['input_value'] = str(params['option_wgt_flux'])
    
    'option_wgt_k'
    d_in['option_wgt_k']['regex'] = pattern_assign(name='option_wgt_k')
    d_in['option_wgt_k']['input_value'] = str(params['option_wgt_k'])
    
    'klin'
    d_in['option_klin']['regex'] = pattern_assign(name='option_klin')
    d_in['option_klin']['input_value'] = str(1) if params['klin'] else str(0)
    
    d_in['klin']['regex'] = pattern_assign(name='klin')
    d_in['klin']['input_value'] = str(params['klin']) + '_r8'
    
    w_diffuse = [w for w_diffuse_ref in params['w_diffuse'] for w in w_diffuse_ref]
    w_diffuse = list(itertools.zip_longest(*(4 * [iter(w_diffuse)])))
    w_diffuse = [[str(v) + '_r8' for v in row if v != None] for row in w_diffuse]
    w_diffuse = [' , '.join(row) for row in w_diffuse]
    input_value = ',\n     &     '.join(w_diffuse)
    d_in['w_diffuse']['regex'] = pattern_data(name='w_diffuse')
    d_in['w_diffuse']['input_value'] = input_value

    'atmpro'
    d_in['atmpro']['regex'] = pattern_atmpro()
    d_in['atmpro']['input_value'] = params['atmpro']
    
    d_in['tsfc']['regex'] = pattern_assign(name='tsfc')
    d_in['tsfc']['input_value'] = str(params['tsfc']) + '_r8'

    'option_compute_ktable'
    d_in['option_compute_ktable']['regex'] = pattern_assign(
        name='option_compute_ktable')
    d_in['option_compute_ktable']['input_value'] = str(params['option_compute_ktable'])

    'option_compute_btable'
    d_in['option_compute_btable']['regex'] = pattern_assign(
        name='option_compute_btable')
    d_in['option_compute_btable']['input_value'] = str(params['option_compute_btable'])
    
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

    title = '{molecule} band{band} {atmpro} ng_refs{ng_refs}'
    title = title.format(
        **{n: param[n] for n in ['molecule', 
                                 'band', 
                                 'atmpro', 
                                 'ng_refs']})
    
    content = ['{}: {}'.format(parameter, value)
               for parameter, value in param.items()]
    
    msg = [title] + content
    msg = [['-m', m] for m in msg]
    return [a for m in msg for a in m]











