import os
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



def take_difference_between_cases(datasets):
    '''
    Take all possible differences between Datasets in DATASETS.
    INPUT:
    datasets --- dictionary of xray Datasets
    OUTPUT:
    dictionary of xray Datsets of differences between Datsets in the input
    DATASETS
    '''
    diff_strs = get_cases_difference()
    
    return {x + ' - ' + y: datasets[x] - datasets[y]
            for x, y in diff_strs}
