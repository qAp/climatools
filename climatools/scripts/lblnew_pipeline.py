
import os
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

# Specify the directory in which 'results.ipynb' is kept.
DIR_IPYNB = os.path.join(
    '/chia_cluster/home/jackyu/radiation',
    'offline_radiation_notebooks',
    'longwave',
    'lblnew_20160916',
    'study__g1_threshold')




def get_dir_case(params):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `params`
    '''   
    template = os.path.join(
        '/chia_cluster/home/jackyu/radiation/crd',
        'LW/examples',
        'separate_g_groups',
        'study__lblnew_g1_threshold',
        '{molecule}',
        'band{band:02d}_wn_{vmin:d}_{vmax:d}',
        'ng_{ng:d}',
        'g_ascending_k_descending',
        'refPTs_{refPTs}',
        'ng_refs_{ng_refs}',
        'getabsth_{getabsth}',
        'absth_{absth}',
        'wgt_{wgt}',
        'wgt_flux_{option_wgt_flux}',
        'wgt_k_{option_wgt_k}',
        'klin_{klin}',
        'crd_{commitnumber}',
        'atmpro_{atmpro}')
    
    nref = len(params['ng_refs'])
    vmin, vmax = CLIRADLW_BANDS[params['band']][0]
    ng = sum(params['ng_refs'])
    refPTs = '__'.join(['P_{}_T_{}'.format(*pt) 
                        for pt in params['ref_pts']])
    ng_refs = '__'.join([str(n) for n in params['ng_refs']])
    getabsth = '__'.join(['auto' for _ in range(nref)])
    absth = '__'.join(['dlogN_uniform' for _ in range(nref)])
    wgt = '__'.join(['_'.join([str(w) for w in wgt_ref]) 
                     for wgt_ref in params['wgt']])
    klin = 'none' if params['klin'] == 0 else params['klin']
    
    return template.format(molecule=params['molecule'],
                    band=params['band'], vmin=vmin, vmax=vmax,
                    ng=ng,
                    refPTs=refPTs,
                    ng_refs=ng_refs,
                    getabsth=getabsth,
                    absth=absth,
                    wgt=wgt,
                    option_wgt_flux=params['option_wgt_flux'],
                    option_wgt_k=params['option_wgt_k'],
                    klin=klin,
                    commitnumber=params['commitnumber'],
                    atmpro=params['atmpro'])



def run_cases(cases_params=None):
    '''
    Run lblnew.f for one or more sets of its
    input parameters.

    Parameters
    ----------
    cases_params: list-like
        List of dictionaries.  One dictionary for each set
        of lblnew input values.
    '''
    procs = []
    for params in cases_params:
        dir_case = get_dir_case(params)
        
        print(dir_case)
        
        try:
            os.makedirs(dir_case)
        except FileExistsError:
            print(params, 'This case already exists.')
            print()
            procs.append(None)
            continue
            
        try:
            os.chdir(dir_case)
            assert os.system('cp {}/*.f .'.format(DIR_SRC)) == 0
        except AssertionError:
            print('Problem copying source code to case directory for '
                  'case',
                  dir_case)
            print()
            procs.append(None)
            continue
            
        
        fname_code = 'lblnew.f'
        
        os.chdir(dir_case)
        enter_input_params(fname_code, params=params)
        
        try:
            os.chdir(dir_case)
            os.system('ifort -g -traceback -fpe0 {} -o lblnew.exe'.format(fname_code))
            assert os.path.exists('lblnew.exe') == True
        except AssertionError:
            print('Problem compiling source code for case',
                  params)
            print()
            procs.append(None)
            continue
        
        proc = subprocess.Popen(['./lblnew.exe'], stdout=subprocess.PIPE)
        
        procs.append(proc)
    
    print()
        
    return procs


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
    
    molecule_flags = [1 if m==params['molecule'] else 0 
                      for m in molecules]
    input_value = '   ,   '.join([str(flg) for flg in molecule_flags])
    d_in['molecule']['regex'] = pattern_molecule()
    d_in['molecule']['input_value'] = input_value
    
    vmin, vmax = CLIRADLW_BANDS[params['band']][0]
    vstar = vmin
    nband = vmax - vmin # keeping nv * dv = 1
    d_in['vstar']['regex'] = pattern_assign(name='vstar')
    d_in['vstar']['input_value'] = ' ' + str(vstar) + '_r8'
    d_in['nband']['regex'] = pattern_assign(name='nband')
    d_in['nband']['input_value'] = ' ' + str(nband)
    
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

    
    
def get_analysis_dir(params):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `params`
    '''   
    template = os.path.join(
        '/chia_cluster/home/jackyu/radiation',
        'offline_radiation_notebooks',
        'longwave',
        'lblnew_20160916',
        'study__g1_threshold',
        '{molecule}',
        'band{band:02d}_wn_{vmin:d}_{vmax:d}',
        'ng_{ng:d}',
        'g_ascending_k_descending',
        'refPTs_{refPTs}',
        'ng_refs_{ng_refs}',
        'getabsth_{getabsth}',
        'absth_{absth}',
        'wgt_{wgt}',
        'wgt_flux_{option_wgt_flux}',
        'wgt_k_{option_wgt_k}',
        'klin_{klin}',
        'crd_{commitnumber}',
        'atmpro_{atmpro}')
    
    nref = len(params['ng_refs'])
    vmin, vmax = CLIRADLW_BANDS[params['band']][0]
    ng = sum(params['ng_refs'])
    refPTs = '__'.join(['P_{}_T_{}'.format(*pt) 
                        for pt in params['ref_pts']])
    ng_refs = '__'.join([str(n) for n in params['ng_refs']])
    getabsth = '__'.join(['auto' for _ in range(nref)])
    absth = '__'.join(['dlogN_uniform' for _ in range(nref)])
    wgt = '__'.join(['_'.join([str(w) for w in wgt_ref]) 
                     for wgt_ref in params['wgt']])
    klin = 'none' if params['klin'] == 0 else params['klin']
    
    return template.format(molecule=params['molecule'],
                    band=params['band'], vmin=vmin, vmax=vmax,
                    ng=ng,
                    refPTs=refPTs,
                    ng_refs=ng_refs,
                    getabsth=getabsth,
                    absth=absth,
                    wgt=wgt,
                    option_wgt_flux=params['option_wgt_flux'],
                    option_wgt_k=params['option_wgt_k'],
                    klin=klin,
                    commitnumber=params['commitnumber'],
                    atmpro=params['atmpro'])    



def analyse_case(params):
    '''
    Execute the analysis notebook (i.e. plot
    and tabulate results) for a case.

    Paramaters
    -----------
    params: dict
        Dictionary of input values.  The keys and values                        
        are the names and values of the input parameters.
    '''
    dir_case = get_analysis_dir(params)
    
    print(dir_case)
    
    try:
        os.makedirs(dir_case)
    except FileExistsError:
        print(params, 'This case already exists.')
        raise
        
    try:
        os.chdir(dir_case)
        assert os.system('cp {}/results.ipynb .'.format(DIR_IPYNB)) == 0
    except AssertionError:
        print('Problem copying Notebook template to analysis '
              'directory for the case:',
              dir_case)
        raise
    
    dir_crd = get_dir_case(params)
    dir_xcrd = get_dir_case(params)
    ng_refs = params['ng_refs']
    p_refs = [p for p, t in params['ref_pts']]    
    
    lines = ["DIR_CRD = '{}'".format(dir_crd),
             "DIR_XCRD = '{}'".format(dir_xcrd),
             "NG_REFS = {}".format(ng_refs),
             "P_REFS = {}".format(p_refs)]
    
    os.chdir(dir_case)
    with open('params.py', encoding='utf-8', mode='w') as f:
        f.write('\n'.join(lines))
        
        
    return subprocess.Popen(['jupyter', 'nbconvert', 
                             '--execute',
                             '--to', 'notebook',
                             '--inplace',
                             'results.ipynb'], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


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



def git_addcommit(param):
    '''
    Git-add and commit a lblnew case.
    
    Parameters
    ----------
    param: dict
        Dictionary of input values.  The keys and values                        
        are the names and values of the input parameters.        
    '''

    print(get_analysis_dir(param))
    fpath_results = os.path.join(
        get_analysis_dir(param), 'results.ipynb')
    fpath_parampy = os.path.join(
        get_analysis_dir(param), 'params.py')
    
    proc_gitadd = subprocess.Popen(['git', 'add', 
                                    fpath_results, fpath_parampy],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    
    our, err = proc_gitadd.communicate()
    
    cmd = ['git', 'commit'] + commit_msg(param)
    proc_gitcommit = subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    return proc_gitcommit


def run_pipieline(params):
    '''
    Runs lblnew pipeline for one or more sets
    of input values.

    Parameters
    ----------
    params: list-like
        List of dictionaries.  One dictionary for each set
        of lblnew input values.
    '''
    procs = run_cases(params)

    print()

    aprocs = []
    all_being_analysed = False
    while not all_being_analysed:
        
        for proc, param in zip(procs, params):
            if proc.poll() is None:
                continue
            else:
                proc.kill()
                aproc = analyse_case(param)
                aprocs.append((aproc, param))
                
        if len(aprocs) == len(procs):
            all_being_analysed = True   
            break
            
        time.sleep(5)
        
    
    print()
        
    gprocs = []
    all_been_committed = False
    while not all_been_committed:
        
        for aproc, param in aprocs:
            if aproc.poll() is None:
                continue
            else:
                aproc.kill()
                gproc = git_addcommit(param)
                out, err = gproc.communicate()
                gprocs.append((gproc, param))
                
        if len(gprocs) == len(aprocs):
            all_been_committed = True
            break
            
        time.sleep(10)

    return gprocs



if __name__ == '__main__':
    # The following is an example of how to run the pipeline

    # We want to run lblnew.f for 3 cases: h2o band07 at
    # atmosphere profiles mls, saw and trp.
    h2o_band07_ng7 = {
        'molecule': 'h2o',
        'band': 7,
        'ref_pts': [(600, 250)],
        'ng_refs': [7],
        'wgt': [(.5, .5, .5, .5, .5, .5, .9,)],
        'w_diffuse': [(1.9, 1.66, 1.66, 1.66, 1.66, 1.66, 1.9)],
        'option_wgt_flux': 2,
        'option_wgt_k': 1,
        'klin': 0,
        'commitnumber': 'bd5b4a5',
        }
    
    atmpro_tsfc = [('saw', 257), ('trp', 300), ('mls', 294), ]
    params_h2o_band07_ng7 = []
    
    for atmpro, tsfc in atmpro_tsfc:
        param = h2o_band07_ng7.copy()
        param['atmpro'] = atmpro
        param['tsfc'] = tsfc
        params_h2o_band07_ng7.append(param)
        
    params = []
    params.extend(params_h2o_band07_ng7)
    
    # params is a list of 3 dictionaries, corresponding to
    # mls, saw and trp.

    # Optional: delete any previous run directories for
    # these 3 cases.
    for param in params:
        try:
            shutil.rmtree(get_dir_case(param))
        except FileNotFoundError:
            continue

    # Optional: delete any previous analysis directories for
    # these 3 cases.
    for param in params:
        try:
            shutil.rmtree(get_analysis_dir(param))
        except FileNotFoundError:
            continue

    # Pass the list of dictionaries to the function 
    # 'run_pipeline()' and computation starts
    gprocs = lblnew.run_pipieline(params)

    # `gprocs` is a list of (subprocess, param) pairs
    # for the Git-add-and-submit step.

