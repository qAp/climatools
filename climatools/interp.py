
import os
import sys

import numpy as np
import scipy as sp
import pandas as pd

import cubic # f2py3-produced module






def cubic_spline(x_sample, y_sample, x_predict):
    '''
    Cubic spline interpolation.
    INPUT:
    x_sample --- sample x values
    y_sample --- sample y values
    x_predict --- x values for which y values are to be predicted
    OUTPUT:
    y_predict --- predicted y values
    NOTES:
    Numerical Recipes in Fortran (3.3 Cubic Spline Interpolation)
    '''
    y2 = cubic.spline(x_sample, y_sample, 2e30, 2e30)
    cubic_spline_fit = np.vectorize(lambda x: cubic.splint(x_sample, y_sample, y2, x))
    return cubic_spline_fit(x_predict)
    




    






