
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



