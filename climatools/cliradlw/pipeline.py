
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
        os.system('ifort -g -traceback -fpe0 {} -o cliradlw.exe'.format(fname_code))
        assert os.path.exists('cliradlw.exe') == True
    except AssertionError:
        pprint.pprint(param)
        print('Problem compiling source code for this case.')
        print()
        return None
        
    proc = subprocess.Popen(['./cliradlw.exe'], stdout=subprocess.PIPE)
    pprint.pprint(param)
    return proc



def run_analysis(param, dir_fortran_lblnew=None, setup=None):
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
    lines.append("DIR_FORTRAN = '{}'".format(dir_fortran))
    lines.append("PARAM = {}".format(param))
    lines.append("DIR_FORTRAN_LBLNEW = '{}'".format(dir_fortran_lblnew))
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
