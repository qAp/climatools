


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



def get_fortran_dir(param):
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





def run_fortran():
    pass



def analyse_case():
    pass



def git_addcommit():
    pass






def test_get_fortran_dir():
    param = {'molecule': ['h2o', 'co2'],
             'band': '3c',
             'nv': 200, 'dv': .005,
             'atmpro': 'mls',
             'commitnumber': '11111'}
    print(get_fortran_dir(param))



if __name__ == '__main__':
    test_get_fortran_dir()
