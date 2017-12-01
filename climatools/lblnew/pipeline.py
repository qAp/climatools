
import os
import pprint
import subprocess
import time





def get_dir_case(param, setup=None):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `param`
    '''   
    dir_case = os.path.join(
        '/chia_cluster/home/jackyu/radiation/crd',
        'LW/examples',
        'separate_g_groups',
        'study__lblnew_g1_threshold',
        setup.get_dir_from_param(param))
    return dir_case



def get_analysis_dir(param, setup=None):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `params`
    '''   
    dir_case =  os.path.join(
        '/chia_cluster/home/jackyu/radiation',
        'offline_radiation_notebooks',
        'longwave',
        'lblnew_20160916',
        'study__g1_threshold',
        setup.get_dir_from_param(param))
    return dir_case



def run_fortran(param=None, setup=None):
    '''
    Run lblnew.f for a single case.

    Parameters
    ----------
    param: dict
    setup: module
           lblnew.setuprun
    '''
    dir_case = get_dir_case(param, setup=setup)
        
    try:
        os.makedirs(dir_case)
    except FileExistsError:
        pprint.pprint(param)
        print('This case already exists.')
        print()
        return None
            
    try:
        os.chdir(dir_case)
        assert os.system('cp {}/*.f .'.format(setup.DIR_SRC)) == 0
    except AssertionError:
        pprint.pprint(param)
        print('Problem copying source code to case directory for this case.')
        print()
        return None
        
    fname_code = 'lblnew.f'
        
    os.chdir(dir_case)
    setup.enter_input_params(fname_code, params=param)
    
    try:
        os.chdir(dir_case)
        os.system('ifort -g -traceback -fpe0 {} -o lblnew.exe'.format(fname_code))
        assert os.path.exists('lblnew.exe') == True
    except AssertionError:
        pprint.pprint(param)
        print('Problem compiling source code for this case.')
        print()
        return None
        
    proc = subprocess.Popen(['./lblnew.exe'], stdout=subprocess.PIPE)
    pprint.pprint(param)
    return proc



def analyse_case(param, setup=None):
    '''
    Execute the analysis notebook (i.e. plot
    and tabulate results) for a case.

    Paramaters
    -----------
    param: dict
        Dictionary of input values.  The keys and values                 
          are the names and values of the input parameters.
    '''
    dir_case = get_analysis_dir(param, setup=setup)
    
    try:
        os.makedirs(dir_case)
    except FileExistsError:
        pprint.pprint(param)
        print('This case already exists.')
        raise
        
    try:
        os.chdir(dir_case)
        assert os.system('cp {} .'.format(setup.PATH_IPYNB)) == 0
    except AssertionError:
        pprint.pprint(param)
        print('Problem copying Notebook template to analysis '
              'directory for this case.')
        raise

    # Write .py file, used as input for analysis notebook
    dir_crd = get_dir_case(param, setup=setup)
    lines=[]
    lines.append("DIR_FORTRAN = '{}'".format(dir_crd))
    lines.append("PARAM = {}".format(param))
    os.chdir(dir_case)
    with open('param.py', encoding='utf-8', mode='w') as f:
        f.write('\n'.join(lines))
        
    pprint.pprint(param)
        
    return subprocess.Popen(['jupyter', 'nbconvert', 
                             '--execute',
                             '--ExecutePreprocessor.timeout=None',
                             '--to', 'notebook',
                             '--inplace',
                             setup.FNAME_IPYNB], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)



def git_addcommit(param, setup=None):
    '''
    Git-add and commit a lblnew case.
    
    Parameters
    ----------
    param: dict
        Dictionary of input values.  The keys and values                       
        are the names and values of the input parameters.        
    '''
    fpath_results = os.path.join(
        get_analysis_dir(param, setup=setup), setup.FNAME_IPYNB)
    fpath_parampy = os.path.join(
        get_analysis_dir(param, setup=setup), 'param.py')
    
    proc_gitadd = subprocess.Popen(['git', 'add', 
                                    fpath_results, fpath_parampy],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    
    out, err = proc_gitadd.communicate()
    
    cmd = ['git', 'commit'] + setup.commit_msg(param)
    proc_gitcommit = subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    pprint.pprint(param)
    return proc_gitcommit



def pipeline_fortran2ipynb2git(params=None, setup=None):
    '''
    Run Fortran code, followed by analysis notebook, then
    commit the analysis notebook to Git depository for 
    a given list of cases.

    Parameters
    ----------
    params: list-like
        List of dictionaries.  One dictionary for each set
        of lblnew input values.    
    overlap: boolean.  (Default: False)
             True for the overlap calculation.
             False for the best-fitting calculation for a single gas.
    gprocs: list
            List of subprocesses for the Git commit of each given case.
    '''

    print('Submitting radiation calculation for cases')
    procs = [run_fortran(param, setup=setup) for param in params]
    print()

    print('Submitting analysis for cases')
    aprocs = {}
    all_being_analysed = False
    while not all_being_analysed:
        
        for proc, param in zip(procs, params):
            if proc.poll() is None:
                continue
            else:
                if proc.pid in aprocs:
                    continue
                else:
                    aproc = analyse_case(param, setup=setup)
                    aprocs[proc.pid] = (aproc, param)
                
        if len(aprocs) == len(procs):
            all_being_analysed = True   
            [proc.kill() for proc in procs]
            break
            
        time.sleep(5)
    print()

    print('Committing analysis to Git repository for cases')
    gprocs = {}
    all_been_committed = False
    while not all_been_committed:
        
        for _, (aproc, param) in aprocs.items():
            if aproc.poll() is None:
                continue
            else:
                if aproc.pid in gprocs:
                    continue
                else:
                    gproc = git_addcommit(param, setup=setup)
                    out, err = gproc.communicate()
                    gprocs[aproc.pid] = (gproc, param)
                
        if len(gprocs) == len(aprocs):
            all_been_committed = True
            for _, (aproc, param) in aprocs.items():
                out, err = aproc.communicate()
            break
            
        time.sleep(10)
    print()

    return gprocs





def test_lblnew_bestfit():
    import climatools.lblnew.setup_bestfit as setup
    params = [{}, {}, ...]
    git_procs3 = pipeline_fortran2ipynb2git(params, setup=setup)
#    git_procs2 = pipeline_ipynb2git(params)
#    git_procs1 = pipeline_fortran2ipynb(params)
    


def test_lblnewoverlap():
    import climatools.lblnew.setup_overlap as setup
    params = [{}, {}, ...]
    git_procs3 = pipeline_fortran2ipynb2git(params, setup=setup)



if __name__ == '__main__':
    pass




    
    
    
