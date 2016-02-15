import os
import sys

import numpy as np
import pandas as pd
import xarray

import climatools.aerosol.f2py3_modal_aero_wateruptake as aerowateruptake
import climatools.aerosol.aerosol_constants as aeroconst




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


def get_raer(ds):
    pass


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
    Calculates and adds to ds:
    * modal aerosol water
    * modal aerosol wet radii
    INPUT:
    ds --- xarray.Dataset (typically loaded from CAM history file)
    OUTPUT:
    None, but ds will be updated with new data arrays for
    modal aerosol water and modal aerosol wet radii
    '''
    for itime, time in enumerate(ds.coords['time']):
        for ilon, lon in enumerate(ds.coords['lon']):
            for ilat, lat in enumerate(ds.coords['lat']):
                ds = wateruptake_column(ds, itime=itime, ilon=ilon, ilat=ilat)

    return ds

                
                










if __name__ == '__main__':
    print(aeroconst.SPECIES_MMR)
