import os

import xray


AEROSOL_DATA_DIRECTORY = '/nuwa_data/data/cesm1/inputdata/atm/cam/physprops'

MAM3_SPECIES = {1: {1: 'sulfate',
                    2: 'p-organic',
                    3: 's-organic',
                    4: 'black-c',
                    5: 'dust',
                    6: 'seasalt'},
                2: {1: 'sulfate',
                    2: 's-organic',
                    3: 'seasalt'},
                3: {1: 'dust',
                    2: 'seasalt',
                    3: 'sulfate'}}

SPECIES_FILE_PREFIX = {'sulfate': 'sulfate',
                       'p-organic': 'ocpho',
                       's-organic': 'ocphi',
                       'black-c': 'bcpho',
                       'seasalt': 'ssam',
                       'dust': 'dust4'}

SPECIES_MMR = {'sulfate': 'so4',
               'p-organic': 'pom',
               's-organic': 'soa',
               'black-c': 'bc',
               'seasalt': 'ncl',
               'dust': 'dst'}

SPECIES_FILENAMES = {'sulfate': 'sulfate_rrtmg_c080918.nc',
                     'p-organic': 'ocpho_rrtmg_c101112.nc',
                     's-organic': 'ocphi_rrtmg_c100508.nc',
                     'black-c': 'bcpho_rrtmg_c100508.nc',
                     'seasalt': 'ssam_rrtmg_c100508.nc',
                     'dust': 'dust4_rrtmg_c090521.nc'}

SPECIES_DATASETS = {}
for species, filename in SPECIES_FILENAMES.items():
    with xray.open_dataset(os.path.join(AEROSOL_DATA_DIRECTORY, filename)) as ds:
        SPECIES_DATASETS[species] = ds.copy(deep = True)


def get_species_name(mode=1, species=1):
    '''
    Return species name for MODEth mode and SPECIESth species
    of MAM3.
    INPUT:
    mode --- 1, 2, or 3
    species --- species number for the mode
    OUTPUT:
    species_name --- \'sulfate\', \'p-organic\', ..., etc.
    '''
    return MAM3_SPECIES[mode][species]


def get_physprop(mode=1, species=1, property='density'):
    '''
    Returns the property PROPERTY of species SPECIES of mode MODE in MAM3.
    '''
    species_name = get_species_name(mode=mode, species=species)
    ds = SPECIES_DATASETS[species_name]
    da = ds[property]
    return da




if __name__ == '__main__':
    da = get_physprop(mode=1, species=6, property='density')
    print(da)
