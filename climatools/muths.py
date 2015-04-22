

import numpy as np

def round_to_1(number):
    '''
    This rounds a number to the first significant number
    '''
    return np.round(number, -int(np.floor(np.log10(number))))


def pow_base10_for_decimal(number, decimal = 0):
    '''
    Returns the power of 10 NUMBER is required to
    be multipliedy by to have a coefficient to DECIMAL
    number of decimal places. e.g. NUMBER = 3 and decimal = 1
    gives -1, because 3e-1 = .3, which has 1 decimal place.
    '''
    return - int(np.floor(np.log10(number)) + int(decimal))
    
