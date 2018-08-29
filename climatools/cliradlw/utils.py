

def mapband_old2new():
    '''
    Map old spectral bands to new spectral bands.
    '''
    return {'1': 1,
            '2': 2,
            '3a': 3,
            '3b': 4,
            '3c': 5,
            '4': 6, 
            '5': 7,
            '6': 8,
            '7': 9, 
            '8': 10,
            '9': 11}



def mapband_new2old():
    '''
    Map new spectral bands to old spectral bands.
    '''
    old2new = mapband_old2new()
    return {new: old for old, new in old2new.items()}
