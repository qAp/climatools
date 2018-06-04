
import os
import pprint
import subprocess
import time
import shutil





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
        
    fname_code = setup.FNAME_CODE 
        
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

    # Print the following to screen in the process
    print('Run {} for:'.format(setup.FNAME_CODE))
    pprint.pprint(param)
    print()

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
    print()
        
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
    gprocs = []
    for param in params:
        gproc = git_addcommit(param=param, setup=setup)
        out, err = gproc.communicate()
        gprocs.append((gproc, param))
    return gprocs




def run_fortran_bsub(param=None, setup=None):
    '''
    (1) Sets up directory to run a case.
    (2) Copy needed file to that directory.
    (3) Compile the fortran.
    (4) Write a submit file and submits a job.
    '''
    dir_fortran = get_dir_case(param, setup=setup)
    
    try:
        os.makedirs(dir_fortran)
    except FileExistsError:
        pprint.pprint(param)
        print('This case already exists.')
        print()
        raise
    
    try:
        os.chdir(dir_fortran)
        assert os.system('cp {}/*.f .'.format(setup.DIR_SRC)) == 0
    except AssertionError:
        pprint.pprint(param)
        print('Problem copying source to case directory in this case.')
        print()
        raise

    fname_code = setup.FNAME_CODE
    os.chdir(dir_fortran)
    setup.enter_input_params(fname_code, params=param)

    try:
        os.chdir(dir_fortran)
        os.system('ifort -g -traceback -fpe0 {} -o lblnew.exe'.format(fname_code))
        assert os.path.exists('lblnew.exe') == True
    except AssertionError:
        pprint.pprint(param)
        print('Problem compiling source code for this case.')
        print()
        raise

    jobname = 'lblnew-bestfit_{}_{}'.format(param['molecule'], param['band'])
    lines = ['#!/bin/bash',
             '#BSUB -J {}'.format(jobname),
             '#BSUB -n 1',
             '#BSUB -o out_%J',
             '#BSUB -e err_%J',
             '',
             './lblnew.exe',
             '',
             'sleep 10']

    with open('lblnew-bestfit.sub', mode='w', encoding='utf-8') as f:
        s = '\n'.join(lines)
        f.write(s)

    try:
        assert os.system('bsub < lblnew-bestfit.sub') == 0
    except AssertionError:
        print('Problem submitting job for this case')
        raise
    

    
def pipeline_fortran_bsub(params=None, setup=None):
    '''
    Submit jobs to run the Fortran code for a list of 
    specified cases.
    '''
    for param in params:

        dir_fortran = get_dir_case(param, setup=setup)        
        try:
            shutil.rmtree(dir_fortran)
        except FileNotFoundError:
            pass

        run_fortran_bsub(param=param, setup=setup)


    

    



def pipeline_ipynb2git(params=None, setup=None):

    for param in params:
        try:
            shutil.rmtree(
                get_analysis_dir(param, setup=setup))
        except FileNotFoundError:
            continue

    aprocs = []
    for param in params:
        aproc = analyse_case(param, setup=setup)
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

    for param in params:
        try:
            shutil.rmtree(
                get_dir_case(param, setup=setup))
        except FileNotFoundError:
            continue
        
    for param in params:
        try:
            shutil.rmtree(
                get_analysis_dir(param, setup=setup))
        except FileNotFoundError:
            continue

    print('Running Fortran for cases')
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
                    out, err = proc.communicate()
                    if err:
                        print('Warning: The following Fortran run finished with errors.')
                        pprint.pprint(param)
                        print(err.decode('utf-8'))

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




def pipeline_fortran_ipynb_git(param=None, setup=None):
    '''
    Run Fortran code, followed by analysis notebook, then
    commit the analysis notebook to Git depository for 
    a case.

    Parameters
    ----------
    param: dict
        A set of lblnew input values.
    setup: python module
        `setup_overlap` for the overlap calculation.
        `setup_bestfit` for the best-fitting calculation for a single gas.
    gprocs: subprocess.Subprocess
        Subprocess for the Git commit of the input case.
    '''
    try:
        shutil.rmtree(get_dir_case(param, setup=setup))
    except FileNotFoundError:
        pass
        
    try:
        shutil.rmtree(get_analysis_dir(param, setup=setup))
    except FileNotFoundError:
        pass

    print('Running Fortran for case')
    proc = run_fortran(param, setup=setup)
    print()

    print('Submitting analysis for case')
    being_analysed = False
    while not being_analysed:
        if proc.poll() is None:
            continue
        else:
            out, err = proc.communicate()
            if err:
                print('Warning: The following Fortran'
                      ' run finished with errors.')
                pprint.pprint(param)
                print(err.decode('utf-8'))
            
            aproc = analyse_case(param, setup=setup)
            being_analysed = True
            proc.kill()
            break 
        time.sleep(5)
    print()

    print('Committing analysis to Git repository for cases')
    been_committed = False
    while not been_committed:
        if aproc.poll() is None:
            continue
        else:
            gproc = git_addcommit(param, setup=setup)
            out, err = gproc.communicate()
            been_committed = True
            out, err = aproc.communicate()
            break
        time.sleep(10)
    print()

    return gproc




def nbviewer_url(param=None, setup=None):
    '''
    Returns the url for the notebook on nbviewer.jupyter.org
    '''
    return os.path.join(
        'http://nbviewer.jupyter.org/github',
        'qap/offline_radiation_notebooks/blob/master',
        'longwave/lblnew_20160916/study__g1_threshold',
        setup.get_dir_from_param(param),
        setup.FNAME_IPYNB)




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




    
    
    
