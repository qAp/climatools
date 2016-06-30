import os

import xarray as xr



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


