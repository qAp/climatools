import os

import numpy as np
import pandas as pd
import xarray as xr

import climatools.rrtmg as rrtmg



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

MODES_FILENAME = 'modal_optics_3mode_c100507.nc'

WATER_FILENAME = 'water_refindex_rrtmg_c080910.nc'


SPECIES_DATASETS = {}
for species, filename in SPECIES_FILENAMES.items():
    with xr.open_dataset(os.path.join(AEROSOL_DATA_DIRECTORY, filename),
                         decode_cf=False) as ds:
        SPECIES_DATASETS[species] = ds.copy(deep=True)


MODES_DATASET = {}
with xr.open_dataset(os.path.join(AEROSOL_DATA_DIRECTORY, MODES_FILENAME),
                     decode_cf=False) as ds:
    MODES_DATASET = ds.copy(deep=True)


WATER_DATASET = {}
with xr.open_dataset(os.path.join(AEROSOL_DATA_DIRECTORY, WATER_FILENAME),
                     decode_cf=False) as ds:
    WATER_DATASET = ds.copy(deep=True)


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


def get_physprop(mode=1, species=None, property='opticsmethod'):
    '''
    Returns the property PROPERTY of species SPECIES of mode MODE in MAM3.
    '''
    if species == None:
        da = MODES_DATASET[property].sel(mode=mode - 1)
    else:
        species_name = get_species_name(mode=mode, species=species)
        da = SPECIES_DATASETS[species_name][property]
    return da


def get_specdens():
    '''
    Returns aerosol density of all species of all modes in MAM3.
    This is compatible with modal_aero_sw() in CESM 1.0.3.
    OUTPUT:
    da --- xarray.DataArray. aerosol material densities for all modes and species.
    '''
    ntot_amode = len(MAM3_SPECIES.keys())
    max_nspec_amode = max(len(dict_mode.keys())
                          for mode, dict_mode in MAM3_SPECIES.items())

    modes = range(1, ntot_amode + 1)
    species = range(1, max_nspec_amode + 1)

    da = xr.DataArray(np.full((ntot_amode, max_nspec_amode), np.nan),
                      dims = ['mode', 'species'],
                      coords = [modes, species])

    da.attrs['units'] = 'kg m^-3'
    da.attrs['long_name'] = 'aerosol material density'

    for mode, dict_mode in MAM3_SPECIES.items():
        for species in dict_mode.keys():
            density = get_physprop(mode=mode, species=species, property='density')
            da.loc[dict(mode=mode, species=species)] = density

    da = da.transpose('species', 'mode')
    return da


def get_specrefindex():
    '''
    Get the refractive index of all modes in MAM3.
    OUTPUT:
    da --- xarray.DataArray; dims = (species, mode, nswbands)
    '''
    ntot_amode = len(MAM3_SPECIES.keys())
    max_nspec_amode = max(len(dict_mode.keys())
                          for mode, dict_mode in MAM3_SPECIES.items())
    nbands = rrtmg.nbands(region='sw')

    modes = range(1, ntot_amode + 1)
    species = range(1, max_nspec_amode + 1)
    bands = range(1, nbands + 1)

    da = xr.DataArray(np.full((ntot_amode, max_nspec_amode, nbands), np.nan, dtype='complex'),
                      dims = ['mode', 'species', 'sw_band'],
                      coords = [modes, species, bands])

    for mode, dict_mode in MAM3_SPECIES.items():
        for species in dict_mode.keys():
            ref_real = get_physprop(mode=mode, species=species, property='refindex_real_aer_sw')
            ref_imag = get_physprop(mode=mode, species=species, property='refindex_im_aer_sw')
            da.loc[dict(mode=mode, species=species)] = ref_real + 1j * np.abs(ref_imag)
            
    da = da.transpose('species', 'mode', 'sw_band')
    return da


def get_extpsw():
    return MODES_DATASET['extpsw'].transpose('coef_number',
                                             'refindex_real', 'refindex_im',
                                             'mode',
                                             'sw_band')


def get_abspsw():
    return MODES_DATASET['abspsw'].transpose('coef_number',
                                             'refindex_real', 'refindex_im',
                                             'mode',
                                             'sw_band')


def get_asmpsw():
    return MODES_DATASET['asmpsw'].transpose('coef_number',
                                             'refindex_real', 'refindex_im',
                                             'mode',
                                             'sw_band')


def get_refrtabsw():
    return MODES_DATASET['refindex_real_sw'].transpose('refindex_real', 'sw_band')


def get_refitabsw():
    return MODES_DATASET['refindex_im_sw'].transpose('refindex_im', 'sw_band')


def get_crefwsw():
    crefwsw_real = WATER_DATASET['refindex_real_water_sw']
    crefwsw_imag = WATER_DATASET['refindex_im_water_sw']
    crefwsw = crefwsw_real + 1j * np.abs(crefwsw_imag)
    return crefwsw



if __name__ == '__main__':
    print('Aeosol density')
    for mode, speciess in MAM3_SPECIES.items():
        print('mode {:f}'.format(mode))
        print([float(get_physprop(mode=mode, species=species, property='density').values)
               for species in sorted(speciess.keys())])

    print()

    print('Aeosol hygroscopicity')
    for mode, speciess in MAM3_SPECIES.items():
        print('mode {}'.format(mode))
        print([float(get_physprop(mode=mode, species=species, property='hygroscopicity').values)
               for species in sorted(speciess.keys())])

