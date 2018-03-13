import os
import re
import collections


# Specify the directory in which CLIRAD-LW source code is kept.
DIR_SRC = os.path.join('/chia_cluster/home/jackyu/radiation',
                       'clirad-lw/LW/lee_hitran2012_update')

FNAME_CLIRADLW = 'CLIRAD_new_25cm_re.f'

# Path for the template analysis notebook.
PATH_IPYNB = os.path.join('/chia_cluster/home/jackyu',
                          'climatools/climatools/cliradlw',
                          'results_cliradlw.ipynb')


def get_dir_from_param(param):
    '''
    Returns the directory path that describes the case 
    specified by the input parameters.  

    Parameters
    ----------
    param: dict
           Dictionary containing the keys and values of input parameters.
    '''
    molecule_names = ('h2o', 'co2', 'o3', 'n2o', 'ch4',)

    molecule = {}
    for name, conc in param['molecule'].items():
        
        if conc == 'atmpro':
            molecule[name] = param['atmpro']
        else:
            try:
                float(conc)
            except (ValueError, TypeError) as e:
                print('`conc` has to be either atmpro or a number.')
                raise
            molecule[name] = conc

    band = sorted(list(set(param['band'])))

    s_molecule = []
    for n in molecule_names:
        if n in molecule:
            s_molecule.append('{}_{}'.format(n, molecule[n]))
    s_molecule = '_'.join(s_molecule)

    s_band = ['{:d}'.format(b) for b in band]
    s_band = 'band_' + '_'.join(s_band)

    s_commit = 'cliradlw_{}'.format(param['commitnumber'])

    s_atmpro = 'atmpro_{}'.format(param['atmpro'])

    return os.path.join(s_molecule, s_band, s_atmpro, s_commit)
    


def pattern_atmpro():
    '''
    Returns regular expression that matches
    the assignment of the atmosphere profile
    used in lblnew.f.
    '''
    return '''
    (atmosphere_profiles/(.*)75.pro)
    '''


def pattern_conc(name=None):
    '''
    Returns regular expression that matches where
    the assignment of the concentration of a molecule
    can be inserted such that it will override anything
    else provided.
    '''
    if name == 'h2o':
        pattern = r'(\n \s+ wa\(i,k\) \s* = \s* (.*))'
    elif name == 'o3':
        pattern = r'(\n \s+ oa\(i,k\) \s* = \s* (.*))'
    elif name in ('co2', 'n2o', 'ch4',):
        pattern = r'(\n \s+ {name} \s* = \s* (.*))'.format(name=name)
    return pattern



def pattern_assign(name=None):
    '''
    Returns regular expression for a Fortran 
    variable assignment.
    '''
    pattern=r'(\n \s* {} \s* = \s* (.*) \s* \n)'.format(name)
    return pattern


def enter_input_params(path_cliradlw, param=None):
    '''
    Insert input values into CLIRAD-LW.

    Parameters
    ----------
    path_cliradlw: string
        Path to the cliradlw.f file to be edited.
    param: dict
        Dictionary of input values.  The keys and values
        are the names and values of the input parameters.
    '''
    d_in = collections.defaultdict(dict)

    # Molecule concentration
    molecule_names = ('h2o', 'co2', 'o3', 'n2o', 'ch4', )
    molecule = {}
    for name in molecule_names:
        if name in param['molecule']:
            if param['molecule'][name] == 'atmpro' and name in ('h2o', 'o3'):
                if name == 'h2o':
                    molecule[name] = 'wa(i,k)'
                else:
                    molecule[name] = 'oa(i,k)'
            elif param['molecule'][name] == 'atmpro':
                molecule[name] = 0
            else:
                molecule[name] = float(param['molecule'][name])
        else:
            molecule[name] = 0

    for name, conc in molecule.items():
        d_in[name]['regex'] = pattern_conc(name=name)
        if conc in ('wa(i,k)', 'oa(i,k)'):
            d_in[name]['input_value'] = conc
        else:
            d_in[name]['input_value'] = str(float(conc))

    # Spectral bands to compute
    bands = [1 if b in set(param['band']) else 0 for b in range(1, 11 + 1)]
    bands = [str(b) for b in bands]
    bands = '(/' + ', '.join(bands) +'/)'
    d_in['band']['regex'] = pattern_assign(name=r'bands\(1:nband\)')
    d_in['band']['input_value'] = bands

    # Atmosphere profile
    d_in['atmpro']['regex'] = pattern_atmpro()
    d_in['atmpro']['input_value'] = param['atmpro']

    # Surface temperature
    d_in['tsfc']['regex'] = pattern_assign(name='tb\(1\)')
    d_in['tsfc']['input_value'] = str(param['tsfc'])


    with open(path_cliradlw, mode='r', encoding='utf-8') as f:
        code = f.read()

    for name, d in d_in.items():
        regex = re.compile(d['regex'], re.VERBOSE)
        statement, value = regex.findall(code)[0]
        print(statement)
        print(value)
        input_statement = statement.replace(value, d['input_value'])
        code = code.replace(statement, input_statement)

    return code
        
