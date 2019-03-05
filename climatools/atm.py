

from .cliradlw.utils import *
from .parameters import *



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



class AtmComposition():
    def __init__(self, gasinbands, gasconcs):
        self.gasinbands = gasinbands
        self.gasconcs = gasconcs

    def to_cliradparam(self, **kwargs):
        '''
        Return clirad input parameter dictionary.
        '''
        band = list(self.gasinbands.keys())
        molecule = self.gasconcs
        return CliradnewLWParam(band=band, molecule=molecule, **kwargs)

    def to_lblnewparam(self, bestfitonly=False, **kwargs):
        params = []
        for b, gs in self.gasinbands.items():
            band = mapband_new2old()[b] 
            if len(gs) == 1:
                mol = gs[0]
                conc = None if self.gasconcs[mol] == 'atmpro' else self.gasconcs[mol]
                params.append(
                    LBLnewBestfitParam(band=band, molecule=mol, conc=conc, **kwargs))
            else:
                molecule = {g: self.gasconcs[g] for g in gs}
                params.append(
                    LBLnewOverlapParam(band=band, molecule=molecule, **kwargs))
        return params
        
    @classmethod
    def cliradlw_nongreys(cls):
        '''
        Returns the composition for an atmosphere that contains
        only the 'non-grey' absorbers.  This was used as the 'overall'
        test for the new k-distribution method
        '''
        gasinbands = {1: ['h2o'],
                      2: ['h2o'],
                      3: ['h2o', 'co2', 'n2o'],
                      4: ['h2o', 'co2'],
                      5: ['h2o', 'co2'],
                      6: ['h2o', 'co2'],
                      7: ['h2o', 'co2', 'o3'],
                      8: ['h2o'],
                      9: ['h2o', 'n2o', 'ch4'],
                      10: ['h2o'],
                      11: ['h2o', 'co2']}
        gasconcs = {'h2o': 'atmpro',
                    'co2': 400e-6,
                    'o3': 'atmpro',
                    'n2o': 3.2e-7,
                    'ch4': 1.8e-6}
        return cls(gasinbands, gasconcs)

    def __repr__(self):
        gasinbands = 'Gases in each band:\n' + str(self.gasinbands)
        gasconcs = 'Gas concentrations:\n' + str(self.gasconcs)
        return f'{self.__class__}\n{gasinbands}\n{gasconcs}'
        
    


