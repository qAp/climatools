

import numpy as np

def round_to_1(number):
    '''
    This rounds a number to the first significant number
    '''
    return np.round(number, -int(np.floor(np.log10(number))))
