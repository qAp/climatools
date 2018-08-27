




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




