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


