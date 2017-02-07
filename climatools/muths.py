

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


def linspace_by_intervals(vmin, vmax, intervals=None):
    '''
    Divide the interval [`vmin`, `vmax`] into `len(intervals)`
    intervals.  Returns the (`intervals` + 1) values,
    including `vmin` and `vmax` in an numpy array.  The length
    of the intervals between the returned values are given by
    `intervals` (these values are used relative to each other).
    Note that if all the intervals are of the same length, it
    is easier to use numpy.linspace.

    Parameters
    ----------
    vmin: minimum value
    vmax: maximum value
    intervals: the lengths of the intervals to divide the range
               [vmin, vmax]
    spce: [numpy array]
          np.array([v0, v1, ..., vn]), where v0 = vmin, and vn = vmax
    '''
    if intervals is None:
        intervals = np.array([1])

    dv_norm = intervals / intervals.sum()
    spce = vmin + np.concatenate(([0], np.cumsum(dv_norm * (vmax - vmin))))
    return spce

        

    
