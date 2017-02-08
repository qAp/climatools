import os
import io
import collections
import re
import itertools

import numpy as np
import pandas as pd
import xarray as xr




def data(s=''):
    '''
    Extract all data statements (`data foo /1, 2, 3/` for example)
    from a piece of Fortran code. The entire data statement and
    the content (the stuff between the two forward-slashes) will
    be returned in a tuple.

    Parameters
    ----------
    s : {string}
        Fortran code
    '''
    
    pattern = r'''
    (data [^/]+ / ([^/]+) /)
    '''
    regex = re.compile(pattern, re.VERBOSE)
    return regex.findall(s)



def numbers(s=''):
    '''
    Extract numebers from a piece of Fortran code.  This covers
    numbers written in various forms, such as 8, .8, 8., -8E-09,
    8e-09.

    Parameters
    ----------
    s : {string}
        Fortran code
    '''
    pattern = '''
    (
    -?
    \d+
    (?: \. \d*)?
    (?: (?: E|e) (?: -|\+) \d+)?
    )
    (?: _r8)?
    '''
    regex = re.compile(pattern, re.VERBOSE)
    return regex.findall(s)


