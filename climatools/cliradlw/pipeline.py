
import os
import pprint
import subprocess
import time
import shutil



def get_fortran_dir(param, setup=None):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `param`
    '''   
    dir_case = os.path.join(
        '/chia_cluster/home/jackyu/radiation/clirad-lw',
        'LW/examples/lblnew/',
        setup.get_dir_from_param(param))
    return dir_case



def get_analysis_dir(param, setup=None):
    '''
    Returns the absolute path of the directory in which 
    to run the case with input parameters `params`
    '''   
    dir_case =  os.path.join(
        '/chia_cluster/home/jackyu/radiation',
        'offline_radiation_notebooks/longwave', 
        'lblnew_20160916/clirad',
        setup.get_dir_from_param(param))
    return dir_case



def run_fortran(param=None, setup=None):
    '''
    Run clirad-lw for a single case.

    Parameters
    ----------
    param: dict
    setup: module
           lblnew.setuprun
    '''
    dir_case = get_fortran_dir(param, setup=setup)
        
    try:
        os.makedirs(dir_case)
    except FileExistsError:
        pprint.pprint(param)
        print('This case already exists.')
        print()
        return None
            
    try:
        os.chdir(dir_case)
        path_cliradlw = os.path.join(setup.DIR_SRC, setup.FNAME_CLIRADLW)
        assert os.system('cp {} .'.format(path_cliradlw)) == 0
    except AssertionError:
        pprint.pprint(param)
        print('Problem copying source code to case directory for this case.')
        print()
        return None
        
    fname_code = setup.FNAME_CLIRADLW
        
    os.chdir(dir_case)
    setup.enter_input_params(fname_code, param=param)
    
    try:
        os.chdir(dir_case)
        os.system('ifort -g -traceback -fpe0 -r8 {} -o cliradlw.exe'.format(fname_code))
        assert os.path.exists('cliradlw.exe') == True
    except AssertionError:
        pprint.pprint(param)
        print('Problem compiling source code for this case.')
        print()
        return None
        
    proc = subprocess.Popen(['./cliradlw.exe'], stdout=subprocess.PIPE)
    pprint.pprint(param)
    return proc



def run_analysis(param, param_lblnew=None, setup=None):
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
        path_ipynb = setup.PATH_IPYNB
        print(path_ipynb)
        assert os.system('cp {} .'.format(path_ipynb)) == 0
    except AssertionError:
        pprint.pprint(param)
        print('Problem copying Notebook template to analysis '
              'directory for this case.')
        raise

    # Write .py file, used as input for analysis notebook
    dir_fortran = get_fortran_dir(param, setup=setup)
    print(dir_fortran)
    lines=[]
    lines.append("PARAM = {}".format(param))
    lines.append("PARAM_LBLNEW = {}".format(param_lblnew))
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
    Git-add and commit the analysis of a run.
    
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
    
    os.chdir(get_analysis_dir(param, setup=setup)) 

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



def pipeline_git(params=None, setup=None):
    '''
    Git-add and commit the analysis of a 
    list of runs.
    '''
    gprocs = []
    for param in params:
        gproc = git_addcommit(param=param, setup=setup)
        out, err = gproc.communicate()
        gprocs.append((gproc, param))
    return gprocs



def pipeline_ipynb2git(parampairs=None, setup=None):
    '''
    Pipeline to:
    (1) run analysis notebook
    (2) Git-add and commit analysis 
    for a list of runs.
    '''
    aprocs = []
    for param, param_lblnew in parampairs:
        try:
            shutil.rmtree(
                get_analysis_dir(param, setup=setup))
        except FileNotFoundError:
            continue

        aproc = run_analysis(param, 
                             param_lblnew=param_lblnew, 
                             setup=setup)
        aprocs.append((aproc, param))

    # Wait for analysis to finish, then git-commit
    gprocs = {}
    all_been_committed = False
    while not all_been_committed:
        for aproc, param in aprocs:
            if aproc.poll() is None:
                continue
            else:
                gproc = git_addcommit(param, setup=setup)
                out, err = gproc.communicate()
                gprocs[aproc.pid] = (gproc, param)

        if len(gprocs) == len(aprocs):
            all_been_committed = True
            for aproc, param in aprocs:
                out, err = aproc.communicate()
            break

        time.sleep(10)

    print()
    return gprocs





def pipeline_fortran2ipynb2git(parampairs=None, setup=None):
    '''
    Pipeline to:
    (1) Run clirad-lw
    (2) Run analysis notebook
    (3) Git-add and commit analysis
    for a list of clirad-lw input parameters.

    Parameters
    ----------
    params: list-like
        List of dictionaries.  One dictionary for each set
        of clirad-lw input values.    
    setup: module
        climatools.cliradlw.setup
    gprocs: list
        List of subprocesses for the Git commit of each given case.
    '''
    for param, _ in parampairs:
        try:
            shutil.rmtree(
                get_fortran_dir(param, setup=setup))
        except FileNotFoundError:
            continue
        
    for param, _ in parampairs:
        try:
            shutil.rmtree(
                get_analysis_dir(param, setup=setup))
        except FileNotFoundError:
            continue

    print('Submitting radiation calculation for cases')
    procs = [run_fortran(param, setup=setup) for param, _ in parampairs]
    print()

    print('Submitting analysis for cases')
    aprocs = {}
    all_being_analysed = False
    while not all_being_analysed:
        
        for proc, (param, param_lblnew) in zip(procs, parampairs):
            if proc.poll() is None:
                continue
            else:
                if proc.pid in aprocs:
                    continue
                else:
                    aproc = run_analysis(param, 
                                         param_lblnew=param_lblnew, 
                                         setup=setup)
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



def nbviewer_url(param=None, setup=None):
    '''
    Returns the url for the notebook on nbviewer.jupyter.org
    '''
    return os.path.join(
        'http://nbviewer.jupyter.org/github',
        'qap/offline_radiation_notebooks/blob/master',
        'longwave/lblnew_20160916/clirad',
        setup.get_dir_from_param(param),
        setup.FNAME_IPYNB)
