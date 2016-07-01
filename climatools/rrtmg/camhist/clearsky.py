import os

import numpy as np
import xarray as xr

import climatools.units as climaunits


'''
Preparation of variables needed for clear sky radiation calculation.
'''


OZONE_DATA_DIRECTORY = '/nuwa_data/data/cesm1/inputdata/atm/cam/ozone'
OZONE_FILENAME = 'ozone_1.9x2.5_L26_1850clim_c090420.nc'

with xr.open_dataset(os.path.join(OZONE_DATA_DIRECTORY, OZONE_FILENAME),
                     decode_cf=False) as ds:
    OZONE_DATASET = ds.copy(deep=True)



def steal_hybrid_level_coefficients(ds):
    '''
    Takes and adds fields necessary in order to convert
    hybrid levels to milibars.  This function is created
    because some ozone data files do not have the
    coefficients necessary to convert surface and reference
    pressure to level/layer pressures in milibars.  These
    coefficients will be taken from other .nc files with
    26 levels.  It is assumed that these are the same 26 levels.
    INPUT:
    ds --- xarray.Dataset
    OUTPUT:
    ds --- xarray.Dataset with additional fields:
           hyam --- coefficient A for mid-points
           hybm --- coefficient B for mid-points
           PS --- surface pressure
           P0 --- reference pressure
    '''
    filegood = 'ozone_1.9x2.5_L26_1850clim_c091112.nc'
    with xr.open_dataset(os.path.join(OZONE_DATA_DIRECTORY, filegood),
                         decode_cf=False) as dsgood:
        
        for var in ['hyam', 'hybm', 'P0', 'PS']:
            newvar = dsgood[var]
            ds[var] = (newvar.dims, newvar, newvar.attrs)
            
    return ds


OZONE_DATASET = steal_hybrid_level_coefficients(OZONE_DATASET)



def get_pressure_difference(ds=None):
    '''
    Get layer pressure difference
    Args:
        ds: xarray.Dataset containing level pressure (`level_pressure`)
    Returns:
        ds: xarray.Dataset with
            layer pressure difference (`dpressure`) added as a field
    Raises:
        KeyError: when there is no `level_pressure` field
    '''
    if 'level_pressure' not in ds:
        raise KeyError('No level pressures in input dataset.')

    upper_levels = range(0, ds.dims['ilev'] - 1)
    lower_levels = range(1, ds.dims['ilev'])

    upper_pres = ds.coords['level_pressure']\
                 .isel(ilev=upper_levels).values
    lower_pres = ds.coords['level_pressure']\
                 .isel(ilev=lower_levels).values
    
    ds['dpressure'] = (ds.coords['layer_pressure'].dims,
                       lower_pres - upper_pres,
                       ds.coords['layer_pressure'].attrs)
    ds['dpressure'].attrs['long_name'] = 'layer pressure difference'
    return ds



def get_o3_concentration(ds=None, interpfunc=None):
    '''
    Get o3 concentration by interpolating the time dimension
    of pre-loaded dataset of ozone concentrations.
    This pre-loaded dataset is defined in aerosol.aerosol_constants
    module.
    INPUT:
    ds --- xarray.Dataset
    OUTPUT:
    ds --- xarray.Dataset, with additional data variable O3
           obtained from pre-loaded dataset. 
    '''
    da = interpfunc(coords=ds.coords['time'])
    ds['O3'] = (da.dims, da, da.attrs)
    return ds



def get_o2_concentration(ds=None):
    '''
    Add data variable for O2 concentration.
    Value found in physics/cam/chem_surfvals.f90
    '''
    name = 'o2mmr'
    long_name = 'o2 mass mixing ratio'
    ds[name] = 0.23143
    ds[name].attrs['long_name'] = long_name
    return ds



def set_co_concentration(ds=None):
    '''
    Add data variable for CO concentration.
    Value set to 0.
    '''
    name = 'covmr'
    long_name = 'co volume mixing ratio'
    ds[name] = 0.
    ds[name].attrs['long_name'] = long_name
    return ds
    


def get_required_variables():
    '''
    The CAM history dataset contains many variables.
    This is the subset of it that is required to run RRTMG
    column model.
    '''
    variables = ['ilev', 'lev',
                 'level_pressure', 'layer_pressure', 'dpressure',
                 'iT', 'T',
                 'Q', 'co2vmr', 'O3',
                 'n2ovmr', 'covmr', 'ch4vmr', 'o2mmr']
    return variables



def gasunits_to_pppv(ds=None):
    '''
    Regardless of what units gas concentrations are given in in
    the original CAM history, convert them to [l/l].
    Where the concentration is constant with layers, broadcast
    the value to all layers.
    '''
    # H2O: convert [kg/kg] to [l/l]
    layer_vmr = climaunits.mixingratio_mass2volume(substance_name='H2O',
                                                   mass_mix=ds['Q'])
    ds['layer_vmr_h2o'] = (('lev',),
                           layer_vmr,
                           {'units': 'l/l',
                            'long_name': 'h2o vmr'})

    # CO2: broadcast co2vmr, in [l/l], to all layers
    layer_vmr = ds['co2vmr'].values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_co2'] = (('lev',),
                           layer_vmr,
                           {'units': 'l/l',
                            'long_name': 'co2 vmr'})

    # O3: broadcast O3, in [l/l], to all layers
    layer_vmr = ds['O3'].values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_o3'] = (('lev',),
                          layer_vmr,
                          {'units': 'l/l',
                           'long_name': 'o3 vmr'})

    # N2O: broadcast n2ovmr, in [l/l], to all layers
    layer_vmr = ds['n2ovmr'].values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_n2o'] = (('lev',),
                           layer_vmr,
                           {'units': 'l/l',
                            'long_name': 'n2o vmr'})

    # CO: broadcast covmr, in [l/l], to all layers
    layer_vmr = ds['covmr'].values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_co'] = (('lev',),
                          layer_vmr,
                          {'units': 'l/l',
                           'long_name': 'co vmr'})

    # CH4: broadcast ch4vmr, in [l/l], to all layers
    layer_vmr = ds['ch4vmr'].values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_ch4'] = (('lev',),
                           layer_vmr,
                           {'units': 'l/l',
                            'long_name': 'ch4 vmr'})

    # O2: convert o2mmr ([kg/kg]) to [l/l], and broadcast to all layers
    layer_vmr = climaunits.mixingratio_mass2volume(substance_name='O2',
                                                   mass_mix=ds['o2mmr'])
    layer_vmr = layer_vmr.values * np.ones((ds.dims['lev'],))
    ds['layer_vmr_o2'] = (('lev',),
                          layer_vmr,
                          {'units': 'l/l',
                           'long_name': 'o2 vmr'})

    return ds



def add_extra_layer_above(ds=None):
    # reset layer and level index to integer values starting from 1
    ds.coords['lev'] = range(1, ds.dims['lev'] + 1)
    ds.coords['ilev'] = range(1, ds.dims['ilev'] + 1)

    # reindex layer and leverl with an additional index number
    ds = ds.reindex(lev=range(ds.dims['lev'] + 1))
    ds = ds.reindex(ilev=range(ds.dims['ilev'] + 1))

    # assign top layer and level pressures
    ds['layer_pressure'][dict(lev=0)] = (.5 * ds['level_pressure']
                                         .isel(ilev=1))
    ds['level_pressure'][dict(ilev=0)] = 1e-4

    # assign top layer and level temperatures
    ds['layer_temperature'][dict(lev=0)] = (ds['layer_temperature']
                                            [dict(lev=1)])
    ds['level_temperature'][dict(ilev=1)] = (.5 *
                                             sum(ds['layer_temperature']
                                                 [dict(lev=[0,1])]))
    ds['level_temperature'][dict(ilev=0)] = (ds['level_temperature']
                                             [dict(ilev=1)])

    # assign top layer molecule densities
    names_molecules = ['h2o', 'co2', 'o3', 'n2o', 'co', 'ch4', 'o2']
    for molecule in names_molecules:
        name_var = 'layer_vmr_' + molecule
        ds[name_var][dict(lev=0)] = ds[name_var][dict(lev=1)]

    return ds






    
    
    

    



