import os

import pandas as pd
import xarray as xr

import climatools.cliradlw.setup as setup_cliradlw
import climatools.cliradlw.pipeline as pipe_cliradlw





'''
This module is for managing datasets associated with 
the new k-distribution method's clirad-lw.
'''


def load_output_file(path_csv):
    '''
    Load output file to xarray.Dataset.  
    The output file can be from either lblnew
    or clirad, as long as it's .csv and multi-index
    format.
    
    Parameters
    ----------
    path_csv: str
              Path to the .csv file to be loaded.
    ds: xarray.Dataset
        Data in the input file in the form of an xarray.Dataset.
    '''
    toindex = ['i', 'band', 'pressure', 'igg', 'g']    
    df = pd.read_csv(path_csv, sep=r'\s+')
    df = df.set_index([i for i in toindex if i in df.columns])
    df = df.rename(columns={'sfu': 'flug',
                            'sfd': 'fldg',
                            'fnet': 'fnetg',
                            'coolr': 'coolrg'})
    ds = xr.Dataset.from_dataframe(df)

    for l in ('level', 'layer'):
        if l in ds.data_vars:
            if len(ds[l].dims) > 1:
                surface = {d: 0 for d in ds.dims if d != 'pressure'}
                coord_level = ds[l][surface]
                ds.coords[l] = ('pressure', coord_level)
            else:
                ds.coords[l] = ('pressure', ds[l])
    
    return ds



def clirad_params_atm(atmpro='mls'):
    '''
    Return the input parameter dictionaries for the
    (band, molecule)s in the toy atmosphere
    (defined in nongreys_byband()).  Note that
    molecule here refers to a dictionary containing 
    the concentration for one or more gases.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile: 'mls', 'saw' or 'trp'.
    d: dict
        Dictionary of {band: param} type.
    '''
    d = {}
    for band, molecule in nongreys_byband().items():
        for param in runrecord.test_cases():
            if [band] == param['band'] and molecule == param['molecule']:
                param['atmpro'] = atmpro
                d[band] = param
                break                
    return d



def analysis_dirs_atm(atmpro='mls'):
    '''
    Maps spectral band to the absolute path of the
    clirad-lw run in which the toy atmosphere's
    radiation is computed.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''
    params = clirad_params_atm(atmpro=atmpro)
    return {band: pipe_cliradlw.get_analysis_dir(param=param,
                                                 setup=setup_cliradlw) 
            for band, param in params.items()}



def clirad_data_atm(params_atm):
    '''
    Gather together clirad-lw's fluxes and cooling rates
    from all spectral bands in the toy atmosphere. 
    
    Parameters
    ----------
    params_atm: dict
        {band: cliradlw input parameter dictionary}

    d: dict
    'flux': xr.Dataset. [pressure, band]
         Fluxes.
    'cool': xr.Dataset. [pressure, band]
         Cooling rate.
    '''
    
    dirnames = [pipe_cliradlw.get_fortran_dir(param,
                                              setup=setup_cliradlw)
                for _, param in params_atm.items()]
    
    fpaths_flux = [os.path.join(n, 'output_flux.dat') for n in dirnames]
    fpaths_cool = [os.path.join(n, 'output_coolr.dat') for n in dirnames]
    
    fluxs = [load_output_file(p) for p in fpaths_flux]    
    cools = [load_output_file(p) for p in fpaths_cool]
    
    d = {}
    d['flux'] = sum(fluxs)
    d['cool'] = sum(cools)
    return d
