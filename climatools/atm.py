



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



def nongreys_byband():
    '''
    These are the concentrations of non-grey 
    absorbers in each spectral band in 
    an atmosphere commonly used as reference.

    The absorption associated with each 
    (band, gas) pair here is computed using 
    the k-distrbution method.
    '''
    return {1: {'h2o': 'atmpro'},
            2: {'h2o': 'atmpro'}, 
            3: {'co2': 0.0004, 'h2o': 'atmpro', 'n2o': 3.2e-07},
            4: {'co2': 0.0004, 'h2o': 'atmpro'},
            5: {'co2': 0.0004, 'h2o': 'atmpro'},
            6: {'co2': 0.0004, 'h2o': 'atmpro'},
            7: {'co2': 0.0004, 'h2o': 'atmpro', 'o3': 'atmpro'},
            8: {'h2o': 'atmpro'},
            9: {'ch4': 1.8e-06, 'h2o': 'atmpro', 'n2o': 3.2e-07},
            10: {'h2o': 'atmpro'},
            11: {'co2': 0.0004, 'h2o': 'atmpro'}}



class ATMCompNongreys():
    def __init__(self):
        self.comp = nongreys_byband()

    def get_param_dict(self, band=None, molecule=None):
        if not band and not molecule:
            bands = list(self.comp.keys())
            molecule = {mol: conc for band, molconc in self.comp.items()
                        for mol, conc in molconc.items()}
            return {'band': bands, 'molecule': molecule}
        
        if not molecule and band:
            return {'band': [band], 'molecule': self.comp[band]}
        
        if molecule and not band:
            d = {}
            d['molecule'] = {molecule: conc
                             for band, molconc in self.comp.items()
                             for mol, conc in molconc.items() if mol == molecule}
            d['band'] = [band for band, molconc in self.comp.items()
                         if molecule in molconc]
            return d
        
        if molecule and band:
            if molecule not in self.comp[band]:
                print(f'There is no {molecule} in band {band}.')
                return None
            else:
                return {'band': [band],
                        'molecule': {mol: conc
                                     for mol, conc in self.comp[band].items()
                                     if mol == molecule}}
