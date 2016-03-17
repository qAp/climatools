import os
import sys

import numpy as np
import scipy.interpolate as interpolate
import pandas as pd
import xarray as xr



import climatools.aerosol.aerosol_constants as aeroconst

#f2py3-compiled modules
import climatools.aerosol.aerowateruptake as aerowateruptake
import climatools.aerosol.modal_aero_sw as f2py3_modal_aero_sw




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


def get_interpfunc(da=None, dim='time',
                   bounds_error=False, fill_value='extrapolate'):
    '''
    Linearly interpolates `da` along dimension `dim`.  This function
    returns a function that evaluates `da` at a set of values along
    dimension `dim`.

    Parameters
    ----------
    da : xarray.DataArray
    dim : string
          name of dimension to interpolate along
    '''
    
    x = da.coords[dim]
    y = da.values
    axis = da.dims.index(dim)
    func = interpolate.interp1d(x=x, y=y, axis=axis,
                                bounds_error=bounds_error,
                                fill_value=fill_value)

    def callf(coords=None, name_dim=None):
        data = func(coords)

        dims_interp = list(da.dims)
        coords_interp = [coords if d == dim else da.coords[d]
                         for d in dims_interp]

        if name_dim:
            dims_interp[dims_interp.index(dim)] = name_dim
        
        da_interp = xr.DataArray(data, dims=dims_interp, coords=coords_interp,
                                 attrs=da.attrs)
        return da_interp
    
    return callf


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


def interp_layers2levels(ds, vars=None):
    '''
    Interpolate layer values to levels.
    
    Args:
        ds: xarray.Dataset
        vars: list of variables in `ds` for which layers values are to be
              interpolated onto levels. Defaults to an empty list.
    Returns:
        ds: xarray.Dataset, with new variable for the level values added
            for each variable in `vars`
    '''
    if not vars:
        vars = []
        
    for var in vars:
        try:
            da = ds[var]
        except KeyError:
            continue
        else:
            interpfunc = get_interpfunc(da, dim='lev')
            da_interp = interpfunc(coords=ds.coords['ilev'], name_dim='ilev')
            ds['i' + var] = (da_interp.dims, da_interp, da_interp.attrs)
    return ds


def get_mmr_name_CAMhist(name, mode):
    name_mmr = aeroconst.SPECIES_MMR[name]
    name_camhist = name_mmr + '_a{:d}'.format(mode)
    return name_camhist


def get_raer_column(ds, lon=0, lat=0, time=0):
    '''
    Returns mass mixing ratio of aerosol species in MAM3,
    in a numpy array of the shape required by modal_aero_wateruptake_sub().
    '''
    pcols, pver, ntot_amode, max_nspec_amode = 1, 30, 3, 6
    
    args_isel = dict(lon=lon, lat=lat, time=time)

    raer = np.zeros((pcols, pver, ntot_amode, max_nspec_amode))
    for imode, (mode, dict_species) in enumerate(aeroconst.MAM3_SPECIES.items()):
        for ispecies, (species, name) in enumerate(dict_species.items()):
            name_mmr = aeroconst.SPECIES_MMR[name]
            name_camhist = name_mmr + '_a{:d}'.format(mode)
            raer[:, :, imode, ispecies] = ds[name_camhist].isel(**args_isel).values
    return raer


def aerosol_species_mmr(ds):
    ntot_amode = len(aeroconst.MAM3_SPECIES.keys())
    max_nspec_amode = max(len(dict_mode.keys())
                          for mode, dict_mode in aeroconst.MAM3_SPECIES.items())

    modes = range(1, ntot_amode + 1)
    species = range(1, max_nspec_amode + 1)

    ds.coords['mode'] = ('mode', modes)
    ds.coords['species'] = ('species', species)

    arr_dims = ('time', 'lev', 'lat', 'lon', 'mode', 'species')
    arr_shape = [len(ds.coords[dim]) for dim in arr_dims]

    ds.update({'aerosol_species_mmr':
               (arr_dims, np.full(arr_shape, np.nan))})

    for mode, dict_mode in aeroconst.MAM3_SPECIES.items():
        for species, name in dict_mode.items():
            name_mmr = get_mmr_name_CAMhist(name, mode)
            ds['aerosol_species_mmr'].\
                loc[dict(mode=mode, species=species)] = ds[name_mmr]
    return ds


def wateruptake_column(ds, itime=0, ilon=0, ilat=0):
    '''
    Calculate the water uptake of aerosols for a single-column
    by calling the modal_aero_waterupatke subroutine from
    the chemistry module of CAM.
    INPUT:
    ds --- CAM history in xarray.Dataset
    itime --- time index
    ilon --- longitude index
    ilat --- latitude index
    OUTPUT:
    ds --- CAM history in xarray.Dataset with the following new fields:
           1. QAERWAT (time, lon, lat, lev, mode)
           2. DGNCUR_AWET (time, lon, lat, lev, mode)
           3. WETDENS (time, lon, lat, lev, mode)
    '''
    pcols, pver, ntot_amode, max_nspec_amode = 1, 30, 3, 6
    
    args_isel = {'time': itime, 'lon': ilon, 'lat': ilat}

    modes = [1, 2, 3]

    try:
        relative_humidity = ds['RELHUM'].isel(**args_isel)
        cloud_fraction = ds['CLOUD'].isel(**args_isel)
        species_mmr = get_raer_column(ds, **args_isel)
    
        relative_humidity = relative_humidity.values.reshape((pcols, pver))
        cloud_fraction = cloud_fraction.values.reshape((pcols, pver))
        
        qaerwat, dgncur_awet, wetdens = aerowateruptake.\
                                        modal_aero_wateruptake_sub(
            ncol=1,
            cldn=cloud_fraction,
            relative_humidity=relative_humidity,
            raer=species_mmr)
    except KeyError as e:
        print('Needed variables missing from CAM history.')
        raise e
    else:
        dict_updates = {'QAERWAT': qaerwat,
                        'DGNCUR_AWET': dgncur_awet,
                        'WETDENS': wetdens}
    
        required_shape = (len(ds.coords['time']),
                          len(ds.coords['lev']),
                          len(ds.coords['lat']),
                          len(ds.coords['lon']),
                          len(ds.coords['mode']))
        required_dims = ['time', 'lev', 'lat', 'lon', 'mode']
        
        for name, data in dict_updates.items():
            if name not in ds:
                # add new dimension and coordinates for aerosol mode
                ds.coords['mode'] = (('mode',), modes)
                # initialise data variables QAERWAT, DGNCUR_AWET and WETDENS
                ds.update({name: (required_dims, np.zeros(required_shape))})

#            ds[name][dict(**args_isel)] = xarray.DataArray(\
#                data[0,:,:],
#                dims = ['lev', 'mode'],
#                coords = [ds.coords['lev'], ds.coords['mode']])
            ds[name][dict(**args_isel)] = data[0,:,:]
        return ds
                

def wateruptake(ds):
    '''
    Water uptake by aerosols
    INPUT:
    ds --- xarray.Dataset (typically loaded from CAM history file)
    OUTPUT:
    ds ---- as input, with the following additional data variables:
            qaerwat --- aerosol water (time, lat, lon, lev, mode)
            dgncur_awet --- wet radius (time, lat, lon, lev, mode)
            wetdens --- wet density (time, lat, lon, lev, mode)
    '''
    stackdims = ('time', 'lat', 'lon')

    pcols = np.prod([ds.coords[dim].shape[0] for dim in stackdims])
    cldn = ds['CLOUD'].stack(pcols=stackdims).transpose('pcols', 'lev')
    rh = ds['RELHUM'].stack(pcols=stackdims).transpose('pcols', 'lev')
    raer = ds['aerosol_species_mmr'].stack(pcols=stackdims)\
               .transpose('pcols', 'lev', 'mode', 'species')

    qaerwat, dgncur_awet, wetdens = aerowateruptake.\
        modal_aero_wateruptake_sub(pcols=pcols, cldn=cldn, \
                                   relative_humidity=rh, raer=raer)

    dims = ('time', 'lat', 'lon', 'lev', 'mode')
    shape = tuple(ds.dims[dim] for dim in dims)

    ds.update({'qaerwat': (dims, qaerwat.reshape(shape)),
               'dgncur_awet': (dims, dgncur_awet.reshape(shape)),
               'wetdens': (dims, wetdens.reshape(shape))})
    
    return ds

                
                
def modal_aero_sw(ds):
    stackdims = ('time', 'lat', 'lon')
    pcols = np.prod([ds.coords[dim].shape[0] for dim in stackdims])    

    # dynamic input variables
    mass
    specmmr = ds['aerosol_species_mmr']\
              .stack(pcols=stackdims)\
              .transpose('species', 'mode', 'pcols', 'lev')
    dgnumwet = ds['dgnumwet']\
               .stack(pcols=stackdims)\
               .transpose('pcols', 'lev', 'mode')
    qaerwat = ds['qaerwat']\
              .stack(pcols=stackdims)\
              .transpose('pcols', 'lev', 'mode')

    # aerosol constants
    specdens = aeroconst.get_specdens()
    specrefindex = aeroconst.get_specrefindex()
    extpsw = aeroconst.get_extpsw()
    abspsw = aeroconst.get_abspws()
    asmpsw = aeroconst.get_asmpsw()
    refrtabsw = aeroconst.get_refrtabsw()
    refitabsw = aeroconst.get_refitabsw()
    crefwsw = aeroconst.get_crefwsw()

    tauxar, wa, ga, fa = f2py_modal_aero_sw.modal_aero_sw(pcols,
                                                          mass,
                                                          specmmr,
                                                          dgnumwet, qaerwat,
                                                          specdens,
                                                          specrefindex,
                                                          extpsw, abspsw, asmpsw,
                                                          refrtabsw, refitabsw,
                                                          crefwsw)

    ds.coords['sw_band'] = ('sw_band', extpsw.coords['sw_band'])
    
    dims = stackdims + ['lev', 'sw_band']
    shape = tuple(ds.dims[dim] for dim in dims)
    ds.update({'tauxar': (dims,
                          tauxar.reshape(shape),
                          {'long_name': 'optical depth'}),
               'wa': (dims,
                      wa.reshape(shape),
                      {'long_name': 'single scattering albedo'}),
               'ga': (dims,
                      ga.reshape(shape),
                      {'long_name': 'asymmetry factor'}),
               'fa': (dims,
                      fa.reshape(shape),
                      {'long_name': 'forward scattering'})
               })

    return ds
    





if __name__ == '__main__':
    print(aeroconst.SPECIES_MMR)
