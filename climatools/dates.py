

import numpy as np
import pandas as pd



def time2datetimes(ds):
    '''
    Converts time in \'number of days since\' to
    Python datetime objects.
    INPUT:
    ds --- xray Dataset or DataArray object with time dimension
    OUTPUT:
    a Numpy array of Python datetime objects
    '''
    t0 = pd.to_datetime(ds['time'].units.split('since')[-1])
    timestamps = [t0 + pd.DateOffset(days = v)
                  for v in ds['time'].values]
    return np.array([stamp.to_datetime() for stamp in timestamps])



def to_daytime_nighttime(ts, hour_daystart = 8, hour_nightstart = 18):
        '''
        The start hour of daytime and nighttime are defined.
        If the hour of the timestamp is between the start hour of
        daytime and nighttime, its hourstamp is set to the start hour
        of daytime.  If it is smaller, its daystamp is rolled backward
        by one day and its hourstamp is set to the start hour of nighttime.
        If it is larger, its hourstamp i set to the start hour of nighttime.
        INPUT:
        ts --- Pandas Timestamp object
        hour_daystart --- hour of the day that daytime starts (0 to 23)
        hour_nightstart -- hour of the day that nighttime starts (0 to 23)
        '''
        if ts.hour < hour_daystart:
            return (ts - pd.DateOffset(days = 1))\
                   .replace(hour = hour_nightstart,
                            minute = 0, second = 0)
        elif hour_daystart <= ts.hour < hour_nightstart:
            return ts.replace(hour = hour_daystart,
                              minute = 0, second = 0)
        else:
            return ts.replace(hour = hour_nightstart,
                              minute = 0, second = 0)


