'''
Manages atmosphere composition: temperature, pressure, gas concentrations, etc. 
'''
from .cliradlw.utils import *
from .parameters import *
from .lblnew.bestfit_params import *

def greys_byband():
    return {1: {'con': 'atmpro'},
            2: {'con': 'atmpro'},
            3: {'con': 'atmpro'},
            4: {'con': 'atmpro'},
            5: {'con': 'atmpro'},
            6: {'con': 'atmpro'}, 
            7: {'con': 'atmpro'},
            8: {'con': 'atmpro', 'n2o': 3.2e-7}, 
            9: {'con': 'atmpro'}, 
            10: None,
            11: None}

def tropopause_pressures():
    '''
    These are the pressures, in mb, of the tropopause region
    in mls, saw and trp profiles.  
    '''
    return dict(mls=180.875, saw=299.75, trp=109.55)

class AtmComposition():
    def __init__(self, gasinbands, gasconcs):
        self.gasinbands = gasinbands
        self.gasconcs = gasconcs

    def to_cliradparam(self, **kwargs):
        "Return clirad input parameter dictionary."
        band = list(self.gasinbands.keys())
        molecule = self.gasconcs
        return CliradnewLWParam(band=band, molecule=molecule, **kwargs)

    def to_lblnewparam(self, bestfit_values=False, **kwargs):
        '''
        bestfit_values: boolean
            When lblnew-bestfit parameters are sought, whether to use the best-fit values
            saved in bestfit_params.py.
        '''
        params = []
        for b, gs in self.gasinbands.items():
            band = mapband_new2old()[b]

            if len(gs) == 1:
                for g in gs:
                    conc = None if self.gasconcs[g] == 'atmpro' else self.gasconcs[g]
                    p = LBLnewBestfitParam(band=band, molecule=g, conc=conc)
                    if bestfit_values:
                        bfv = kdist_params(molecule=p.molecule, band=p.band)
                        for n in ['vmin', 'vmax', 'dv', 'nv', 'ref_pts', 'ng_refs', 'ng_adju', 'klin',
                                  'option_wgt_k', 'option_wgt_flux', 'wgt', 'w_diffuse']:
                            setattr(p, n, bfv[n])
                    for n, v in kwargs.items(): setattr(p, n, v)
                    params.append(p)
            else:
                p = LBLnewOverlapParam(band=band, molecule={g: self.gasconcs[g] for g in gs})
                for n, v in kwargs.items(): setattr(p, n, v)
                params.append(p)
        return params
        
    @classmethod
    def cliradlw_nongreys(cls, onlygas=None, onlyband=None):
        '''
        Returns the composition for an atmosphere that contains
        only the 'non-grey' absorbers.  This was used as the 'overall'
        test for the new k-distribution method
        '''
        gasinbands = {1:['h2o'], 2:['h2o'], 3:['h2o', 'co2', 'n2o'], 4:['h2o', 'co2'],
                      5:['h2o', 'co2'], 6:['h2o', 'co2'], 7:['h2o', 'co2', 'o3'],
                      8:['h2o'], 9:['h2o', 'n2o', 'ch4'], 10:['h2o'], 11:['h2o', 'co2']}
        gasconcs = {'h2o':'atmpro', 'co2':400e-6, 'o3':'atmpro', 'n2o':3.2e-7, 'ch4':1.8e-6}
        if (onlygas and onlygas in gasconcs) and not onlyband:
            gasinbands = {b:[onlygas] for b, gs in gasinbands.items() if onlygas in gs}
            gasconcs = {onlygas:gasconcs[onlygas]}
        elif (onlyband and onlyband in gasinbands.keys()) and not onlygas:
            gasinbands = {onlyband:gasinbands[onlyband]}
            gasconcs = {g:conc for g, conc in gasconcs.items() if g in gasinbands[onlyband]}
        elif (onlygas in gasconcs) and (onlyband in gasinbands.keys()):
            gasinbands = {onlyband:[onlygas]}
            gasconcs = {onlygas:gasconcs[onlygas]}
        return cls(gasinbands, gasconcs)

    def __repr__(self):
        gasinbands = 'Gases in each band:\n' + str(self.gasinbands)
        gasconcs = 'Gas concentrations:\n' + str(self.gasconcs)
        return f'{self.__class__}\n{gasinbands}\n{gasconcs}'
        
    

    
