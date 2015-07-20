import os
import random
import numpy as np
import pandas as pd
import xray

import climatools.units as climaunits
import climatools.dates as climadates
import climatools.geocoords as climageocoords


# these functions sort of prepare data (say from CAM history) before visualisation 


def convert_pressure_time_units(cases):
    '''
    Convert pressure and time units to mbar and datetime objects.
    This assumes all datasets have the same pressure and time
    coordinates.  This conversion is done early using fields such as
    hyam, which will not be needed later.
    '''
    ds = cases[random.choice(list(cases.keys()))]
    lev = climaunits.hybrid2mbar(ds, level_type = 'lev')
    ilev = climaunits.hybrid2mbar(ds, level_type = 'ilev')
    datetimes = climadates.time2datetimes(ds)
    datetimes = [climadates.\
                 UTCtime_to_localtime(datetime,
                                      lon = climageocoords.\
                                      positivise_longitude(ds['lon'].values[0])) \
                 for datetime in datetimes]
    for name, ds in cases.items():
        ds.coords['ilev'] = ('ilev', ilev, {'units': 'mbar', 'long_name': 'interface pressure'})
        ds.coords['lev'] = ('lev', lev, {'units': 'mbar', 'long_name': 'level pressure'})
        ds.coords['time'] = ('time', datetimes, {'units': 'datetime', 'long_name': 'time'})
    return cases
    

def gather_interests_from_cases(cases, interests):
    '''
    Creates a dictionary with keys being the cases.
    For each case is an Xray Dataset containing the interested fields
    '''
    datasets = {}
    
    for case, ds in cases.items():
        datasets[case] = ds[interests].copy(deep = True)
        datasets[case].attrs['case_name'] = case
    return datasets
    
    


def take_difference_between_cases(datasets, diff_strs):
    '''
    Take the difference between all cases for every field
    and return in a similar dictionary
    '''
    return {x + ' - ' + y: datasets[x] - datasets[y]
            for x, y in diff_strs}





def passon_attrs_casename(datasets, diff_datasets, interests = None):
    '''
    Create an attribute for each case.
    Copy over attributes to the differences.
    This is not nice, might be good to get rid of
    the dependency on this.
    '''
    for ds_name, ds in diff_datasets.items():
        ds.attrs['case_name'] = ds_name
        for interest in interests:
            ds[interest].attrs = dict(
                datasets[random.choice(list(datasets.keys()))][interest].attrs)
            ds[interest].attrs['case_name'] = ds_name

    for ds_name, ds in datasets.items():
        for interest in interests:
            ds[interest].attrs['case_name'] = ds_name
            
    return datasets, diff_datasets
        

