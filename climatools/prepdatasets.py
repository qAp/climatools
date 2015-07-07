import os
import random
import numpy as np
import pandas as pd
import xray


# these functions sort of prepare data (say from CAM history) before visualisation 


def gather_interests_from_cases(cases, interests):
    '''
    Filter out all variables other thant INTERESTS for all datasets in CASES.
    INPUT:
    cases --- dictionary of xray Datasets
    interests --- list, or iterable, of strings containins names of interests 
    OUTPUT:
    datasets --- dictionary of xray Datasets, each containing xray DataArrays for
                 interests
    '''
    datasets = {}
    for case, ds in cases.items():
        datasets[case] = ds[interests].copy(deep = True)
        datasets[case].attrs['case_name'] = case
    return datasets



def take_difference_between_cases(datasets, which_differences = None):
    '''
    Take all possible differences between Datasets in DATASETS.
    INPUT:
    datasets --- dictionary of xray Datasets
    which_differences --- list of tuples, each specifying a pair of Datasets
                          between which the difference is to be taken
    OUTPUT:
    dictionary of xray Datsets of differences between Datsets in the input
    DATASETS
    '''
    return {x + ' - ' + y: datasets[x] - datasets[y]
            for x, y in which_differences}



def passon_attrs_casename(datasets, diff_datasets, interests = None):
    '''
    Pass on attributes from DataArrays to differences between
    DataArrays
    INPUT:
    datasets --- dictionary of datasets between which differences have been taken
    diff_datasets --- dictionary of datasets of differences
    OUTPUT:
    datasets --- dictionary of datasets, each with a new attribute of case_name,
                 its key in the dictionary
    diff_datasets --- dictionary of datasets of differences, with attributes passed
                      from original DATASETS. Each dataset also has a new attribute of case_name,
                      its key in the dictionary
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
