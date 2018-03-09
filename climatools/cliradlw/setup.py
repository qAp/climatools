



# Specify the directory in which CLIRAD-LW source code is kept.
DIR_SRC = os.path.join('/chia_cluster/home/jackyu/radiation',
                       'clirad-lw/LW/lee_hitran2012_update')

FNAME_IPYNB = 'results_cliradlw.ipynb'

# Path for the template analysis notebook.
PATH_IPYNB = os.path.join()



def get_dir_from_param(param):
    '''
    Returns the directory path that describes the case 
    specified by the input parameters.  

    Parameters
    ----------
    param: dict
           Dictionary containing the keys and values of input parameters.
    '''
    molecule_names = ['h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2']
    molecule = 'h2o_{h2o}_co2_{co2}_o3_{o3}_n2o_{n2o}_ch4_{ch4}_o2_{o2}'

    for name, conc in param['molecule']:
        molecule = molecule.format(name=str(conc))
        molecule_names.remove(name)

    for name in molecule_names:
        molecule = molecule.format(name=str(0))

    band = [1 if b + 1 in param['band'] else 0 for b in range(11)]
    band = ['{:d}'.format(b) for b in band]
    band = 'band_' + '_'.join(band)

    commit = 'cliradlw_{}'.format(param['commitnumber'])

    atmpro = 'atmpro_{}'.format(param['atmpro'])

    return os.path.join(molecule, band, commit, atmpro)
    
