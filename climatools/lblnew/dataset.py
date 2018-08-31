
import os
import importlib
import pprint

import pandas as pd
import xarray as xr

import climatools.cliradlw.utils as utils
import climatools.atm.absorbers as absorbers

import climatools.lblnew.setup_bestfit as setup_bestfit
import climatools.lblnew.runrecord_bestfit as runrecord_bestfit

import climatools.lblnew.setup_overlap as setup_overlap
import climatools.lblnew.runrecord_overlap as runrecord_overlap

import climatools.lblnew.pipeline as pipeline


importlib.reload(utils)
importlib.reload(absorbers)

importlib.reload(setup_bestfit)
importlib.reload(runrecord_bestfit)

importlib.reload(setup_overlap)
importlib.reload(runrecord_overlap)

importlib.reload(pipeline)




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



def params_atm(atmpro=None):
    '''
    Search the run records and return 
    the input parameter dictionary of each spectral 
    band, together making up the model atmosphere.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile. Can be 'mls', 'saw', or 'trp'.
        If None, returns whatever profile is already 
        in the run records.
    params: list
        List of input parameter dictionaries that,
         together, make up the model/typical atmosphere.
    '''
    param_bands = absorbers.nongreys_byband()

    # Search constraints
    nv, dv = 1000, .001

    params = []
    for band, dmol in param_bands.items():
        band = utils.mapband_new2old()[band]
    
        if len(dmol.keys()) == 1:
            # Search in lblnew-bestfit records
            molecule, conc = [(molecule, conc)
                              for molecule, conc in dmol.items()][0]
    
            conc = None if conc == 'atmpro' else conc
    
            params.extend(
                [param for param in runrecord_bestfit.params()
                 if param['band'] == band
                 if param['molecule'] == molecule
                 if param['conc'] == conc])
    
        if len(dmol.keys()) > 1:
            # Search in lblnew-overlap records
            params.extend(
                [param for param in runrecord_overlap.params()
                 if param['band'] == band
                 if param['molecule'] == dmol
                 if param['nv'] == nv
                 if param['dv'] == dv])

    if atmpro:
        for param in params:
            param['atmpro'] = atmpro

    return params



def lblnew_setup(param=None):
    '''
    Return the appropriate lblnew.setup module
    for a given input parameter dictionary.

    Parameters
    ----------
    param: dict
        Input parameter dictionary for either
        lblnew-bestfit or lblnew-overlap.
    '''
    return setup_bestfit if 'ng_refs' in param else setup_overlap




def load_lblnew_data(param):
    '''
        
    '''
    fname_dsname = [('fname_flux_crd', 'ds_flux_crd'),
                    ('fname_cool_crd', 'ds_cool_crd'),
                    ('fname_flux_wgt', 'ds_flux_wgt'),
                    ('fname_cool_wgt', 'ds_cool_wgt')]

    setup = lblnew_setup(param)
    dir_fortran = pipeline.get_dir_case(param, setup=setup)

    data_dict = {}
    for fname, dsname in fname_dsname:
        fpath = os.path.join(dir_fortran, 
                             setup.output_datfile_name(fname))
        data_dict[dsname] = load_output_file(fpath)
    return data_dict


