
import os
import importlib
import pprint


import climatools.cliradlw.utils as utils
import climatools.atm.absorbers as absorbers

import climatools.lblnew.runrecord_bestfit as runrecord_bestfit
import climatools.lblnew.runrecord_overlap as runrecord_overlap



importlib.reload(utils)
importlib.reload(absorbers)
importlib.reload(runrecord_bestfit)
importlib.reload(runrecord_overlap)





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




