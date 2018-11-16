
'''
This module is for exporting the data from lblnew-bestfit.
'''

import os
import io
import itertools
import importlib

import pymongo
import numpy as np
import pandas as pd

import climatools.lblnew.bestfit_params as bestfit
import climatools.lblnew.setup_bestfit as setup_bestfit
import climatools.lblnew.pipeline as pipeline
from climatools.cliradlw import setup as setup_cliradlw
import climatools.cliradlw.utils as utils_cliradlw



client = pymongo.MongoClient('localhost', 27017, connect=False)



def make_query(param=None):
    '''
    Returns the MongoDB query for a lblnew-bestfit 
    run's document.
    
    Parameters
    ----------
    param: dict
    lblnew-bestfit input parameters.
    '''
    return {'param.' + name: value for name, value in param.items()}

# These are the gases and spectral bands
# that have been fitted using the k-distribution method

def h2o_gasbands():
    return [('h2o', '1'), 
            ('h2o', '2'),
            ('h2o', '3a'),
            ('h2o', '3b'),
            ('h2o', '3c'),
            ('h2o', '4'),
            ('h2o', '5'),
            ('h2o', '6'),
            ('h2o', '7'), 
            ('h2o', '8'),
            ('h2o', '9')]


def co2_gasbands():
    return [('co2', '3a'), ('co2', '3b'), ('co2', '3c'),
            ('co2', '4'), ('co2', '5'), ('co2', '9')]


def o3_gasbands():
    return [('o3', '5'), ('o3', '9')]


def n2o_gasbands():
    return [('n2o', '3a'), ('n2o', '6'), ('n2o', '7')]


def ch4_gasbands():
    return [('ch4', '6'), ('ch4', '7')]




def band_map():
    '''
    Maps spectral bands in lblnew to spectral bands in clirad.
    '''
    return {'1': '1',
            '2': '2',
            '3a': '3',
            '3b': '4',
            '3c': '5',
            '4': '6', 
            '5': '7',
            '6': '8',
            '7': '9', 
            '8': '10',
            '9': '11'}



def into_chunks(l, chunksize):
    '''
    Splits list/iteratable into chunks.
    '''
    return itertools.zip_longest(*(chunksize * [iter(l)]))



def vector_to_F77list(array, num_values_per_line=4, dtype=float,
                      float_format=False):
    '''
    Divides a list of numbers into chunks of a given size, turn
    each chunk into a string in which the numbers in the chunk
    are separated by commas, and returns a list of such strings
    for all chunks.

    Parameters
    ----------
    array: list-like
           List/array of numbers.
    num_values_per_line: int
                         Number of numbers in each chunk. The
                         final chunk will have equal or fewer
                         numbers than this.
    dtype: string format specifier
           int or float[default]
    lines: list
           List of strings containing comma-separated numbers.

    Example
    -------
    >> vector_to_F77list(range(17))
    ['   0.000000e+00,   1.000000e+00,   2.000000e+00,   3.000000e+00,',
 '   4.000000e+00,   5.000000e+00,   6.000000e+00,   7.000000e+00,',
 '   8.000000e+00,   9.000000e+00,   1.000000e+01,   1.100000e+01,',
 '   1.200000e+01,   1.300000e+01,   1.400000e+01,   1.500000e+01,',
 '   1.600000e+01']
    '''
    if dtype == float:
        if float_format:
            strfmt = '{:5.0f}.'
        else:
            strfmt = '{:15.6e}'
    elif dtype == int:
        strfmt = '{:15d}'
    else:
        raise ValueError('dtype must be either float or int.')
    
    chunks = into_chunks(array, num_values_per_line)
    
    chunks = list(chunks)
    
    lines = []
    for chunk in chunks[:-1]:
        vs = [strfmt.format(v) for v in chunk if v != None]
        line = ','.join(vs)
        line = line + ','
        lines.append(line)
        
    vs = [strfmt.format(v) for v in chunks[-1] if v != None]
    line = ','.join(vs)
    lines.append(line)
    return lines



def vector_to_F77(array=None, num_values_per_line=4, dtype=float,
                  float_format=False):
    '''
    Returns the fortran of what goes in between the delimiters `(/`
    and `/)` for an array of numbers.  Fortran 77 delimiters for
    newline, `&`s, are used after a specified number of numbers per
    line.

    Parameters
    ----------
    array: list-like
           List/array of numbers.
    num_values_per_line: int
                         Number of numbers in each chunk. The
                         final chunk will have equal or fewer
                         numbers than this.
    dtype: string format specifier
           int or float[default]
    fortran: string
             Fortran for an array of numbers over one or more
             lines. 

    Example
    -------
    >> print(export.vector_to_F77(range(17), dtype=float))
     &   0.000000e+00,   1.000000e+00,   2.000000e+00,   3.000000e+00,
     &   4.000000e+00,   5.000000e+00,   6.000000e+00,   7.000000e+00,
     &   8.000000e+00,   9.000000e+00,   1.000000e+01,   1.100000e+01,
     &   1.200000e+01,   1.300000e+01,   1.400000e+01,   1.500000e+01,
     &   1.600000e+01
    '''
    lines = vector_to_F77list(array=array, 
                              num_values_per_line=num_values_per_line,
                              dtype=dtype, float_format=float_format)
    
    rlines = [5 * ' ' + '&' + l for l in lines]
    
    fortran = '\n'.join(rlines)
    return fortran



def comment_header(param):
    '''
    Returns a fortran comment showing the molecule and
    spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    mapband = utils_cliradlw.mapband_old2new()

    molecule = param['molecule']
    lblnew_band = param['band']
    clirad_band = mapband[lblnew_band]
    s = "! {} band{}"
    return f"! {molecule} band{clirad_band}"




def getl_ng(param):
    '''
    Returns fortran for the assignment of `ng` for
    a particular molecule and spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    mid = gas2mid(param['molecule'])
    band = band_map()[param['band']]
    ng = sum(param['ng_refs'])
    
    l_ng = 'ng({mid}, {band}) = {ng}'.format(mid=mid, band=band, ng=ng)
    return l_ng



def load_dgdgs(path):
    '''
    Load `dg` and `dgs` data from output file "dgdgs.dat"
    from lblnew-bestfit.

    Parameters
    ----------
    path: string
          The file path to 'dgdgs.dat'.

    df: pandas.DataFrame
        `dg` and `dgs`.
    '''
    df = pd.read_csv(path, sep=r'\s+')
    df = df.set_index('g')    
    return df



def dgdgs_to_F77(dgdgs):
    '''
    Returns the fortran for what goes in between array
    delimiters `(/` and `/)` for a list of `dgs` values.

    Parameters
    ----------
    dgdgs: list-like
           A list of `dgs` values.
    '''
    lines = vector_to_F77list(dgdgs, num_values_per_line=3)
    
    rlines = []
    rlines.append(5 * ' ' + '&' + lines[0])
    for line in lines[1:-1]:
        rlines.append(5 * ' ' + '&' + line)
    rlines.append(5 * ' ' + '&' + lines[-1])
    
    return '\n'.join(rlines)



def dgs(param):
    '''
    Returns fortran for the assignment statement
    of `dgs` for a molecule and a spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.

    Example
    -------
    For molecule=1, band=3, where ng=8:
    
    dgs(1:8, 1, 3) = (/                                                       
     &   5.648506e-04,   1.581680e-03,   9.087519e-03,   4.067653e-02,         
     &   7.966731e-02,   1.881423e-01,   4.535149e-01,   2.267649e-01          
     &/)
    '''
    mid = gas2mid(param['molecule'])
    band = band_map()[param['band']]
    ng = sum(param['ng_refs'])

    fpath = os.path.join(
        pipeline.get_dir_case(param, setup=setup_bestfit),
        'dgdgs.dat')
    dgdgs = load_dgdgs(fpath)
    s = vector_to_F77(dgdgs['dgs'], 
                      num_values_per_line=4, dtype=float)

    l0 = 'dgs(1:{ng}, {mid}, {band}) = (/'
    ls = [l0.format(mid=mid, band=band, ng=ng),
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)
    


def fpath_ktable(param=None):
    '''
    Returns the file paths to the output files 'kg_lin.dat' 
    and 'kg_nonlin.dat' for a lblnew-bestfit run.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    query = make_query(param=param)
    rs = client.lblnew.bestfit_lw.find(query)
    r = next(rs)
    fpath = {'kg_lin': io.StringIO(r['kg_lin']),
             'kg_nonlin': io.StringIO(r['kg_nonlin'])}
    return fpath



def load_ktable(fpath):
    '''
    Returns k-table in the same format as in lblnew.f
    
    Parameter
    ---------
    fpath: string
        File path to either 'kg_lin.dat' or 'kg_nonlin.dat',
        containing the linear or non-linear k-tables.
    ktable: numpy.array. [pressure, temperature, g]
        k-table.
    '''
    try:
        df = pd.read_csv(fpath, sep=r'\s+')
    except pd.errors.EmptyDataError:
        print('No data at:', fpath)
        return np.zeros((3, 3, 4))

    df = df[df['pressure'] >= 1e-2]
    df = df.set_index(['g', 'pressure', 'temperature'])
    ng = len(df.index.levels[0].value_counts())
    nl = len(df.index.levels[1].value_counts())
    ktable = df['k'].values.reshape(ng, nl, -1)
    ktable = np.transpose(ktable, axes=(1, 2, 0))
    return ktable



def ktable_to_F77(ktable, name):
    '''
    Return a list of fortran assignment statements, each for
    a temperature and g.

    Parameters
    ----------
    ktable: numpy.array. [pressure, temperature, g]
        k-table.
    name: string
        Variable name for the k-table.

    Example
    -------
            [kg(:, 1, 1) = (/                                                  
     &   1.343974e-15,   1.350713e-15,   1.357494e-15,   1.364311e-15,         
     &   1.371176e-15,   1.378072e-15,   1.385008e-15,   1.392013e-15,         
     &   1.399067e-15,   1.406183e-15,   1.413397e-15,   1.420697e-15,         
     &   1.428097e-15,   1.435642e-15,   1.443312e-15,   1.451093e-15,
     ...
     &   1.765126e-17,   1.485894e-17,   1.247649e-17,   1.038610e-17,         
     &   8.562328e-18,   7.076162e-18                                          
     &/),
            kg(:, 2, 1) = (/                                                   
     &   1.487328e-15,   1.493143e-15,   1.498963e-15,   1.504783e-15,         
     &   1.510611e-15,   1.516431e-15,   1.522252e-15,   1.528094e-15,         
     &   1.533940e-15,   1.539799e-15,   1.545698e-15,   1.551625e-15, 
     ...
     &   1.956012e-17,   1.630528e-17,   1.356653e-17,   1.121399e-17,         
     &   9.203174e-18,   7.572534e-18                                          
     &/),
     ...
            kg(:, 5, 12) = (/                                                  
     &   1.345960e-23,   1.383604e-23,   1.422751e-23,   1.463427e-23,         
     &   1.505761e-23,   1.549696e-23,   1.595347e-23,   1.642938e-23,
     ...
     &   1.124578e-21,   1.455117e-21,   1.871587e-21,   2.367312e-21,    
     &   2.927146e-21,   3.585720e-21                                          
     &/)]
    '''
    nl, nt, ng = ktable.shape
    
    num_values_per_line = 4
    
    last_line = '/)'
    
    lines = []
    for ig in range(ng):
        for it in range(nt):
            first_line = '{}(:, {}, {}) = (/'.format(name, it + 1, ig + 1)
            lines_itg = vector_to_F77list(ktable[:, it, ig], 
                            num_values_per_line=num_values_per_line)
            lines_itg = [first_line] + lines_itg + [last_line]
        
            lines_itg_amp = []
            lines_itg_amp.append(lines_itg[0])
            for l in lines_itg[1:]:
                lines_itg_amp.append(5 * ' ' + '&' + l)
            
            s = '\n'.join(lines_itg_amp)
            
            lines.append(s)
      
    return lines


    
def ktable(param, adjust_wgt=None):
    '''
    Combines linear and non-linear k-tables together using `wgt`,
    then scale it with the diffusivity `w_diffuse`.  Then,
    return a list of fortran assignment statements, each for
    a temperature and g.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.

    Example
    -------
            [kg(:, 1, 1) = (/                                                  
     &   1.343974e-15,   1.350713e-15,   1.357494e-15,   1.364311e-15,         
     &   1.371176e-15,   1.378072e-15,   1.385008e-15,   1.392013e-15,         
     &   1.399067e-15,   1.406183e-15,   1.413397e-15,   1.420697e-15,         
     &   1.428097e-15,   1.435642e-15,   1.443312e-15,   1.451093e-15,
     ...
     &   1.765126e-17,   1.485894e-17,   1.247649e-17,   1.038610e-17,         
     &   8.562328e-18,   7.076162e-18                                          
     &/),
            kg(:, 2, 1) = (/                                                   
     &   1.487328e-15,   1.493143e-15,   1.498963e-15,   1.504783e-15,         
     &   1.510611e-15,   1.516431e-15,   1.522252e-15,   1.528094e-15,         
     &   1.533940e-15,   1.539799e-15,   1.545698e-15,   1.551625e-15, 
     ...
     &   1.956012e-17,   1.630528e-17,   1.356653e-17,   1.121399e-17,         
     &   9.203174e-18,   7.572534e-18                                          
     &/),
     ...
            kg(:, 5, 12) = (/                                                  
     &   1.345960e-23,   1.383604e-23,   1.422751e-23,   1.463427e-23,         
     &   1.505761e-23,   1.549696e-23,   1.595347e-23,   1.642938e-23,
     ...
     &   1.124578e-21,   1.455117e-21,   1.871587e-21,   2.367312e-21,    
     &   2.927146e-21,   3.585720e-21                                          
     &/)]
    '''
    ng = sum(param['ng_refs'])

    d = fpath_ktable(param=param)

    wgt = np.array([v for vs in param['wgt'] for v in vs])

    # Adjust wgt for specified (molecule, band)
    if adjust_wgt:
        if (param['molecule'] == adjust_wgt['molecule'] 
            and param['band'] == adjust_wgt['band']):
            wgt += adjust_wgt['dwgt']

    w_diffuse = np.array([v for vs in param['w_diffuse'] for v in vs])
    wgt = wgt.reshape(-1, ng)
    w_diffuse = w_diffuse.reshape(-1, ng)

    kg_lin = load_ktable(d['kg_lin'])
    kg_nonlin = load_ktable(d['kg_nonlin'])

    kg = w_diffuse * (wgt * kg_lin + (1 - wgt) * kg_nonlin)

    ls_kg = ktable_to_F77(kg, 'kg')

#    print('molecule', param['molecule'], 'band', param['band'])
#    print('wgt', wgt)
#    print('w_diffuse', w_diffuse)
#    print()
#    print(kg_lin.shape, kg_nonlin.shape, kg.shape)
    
    return ls_kg
    


def kdist_param_gasband(param, adjust_wgt=None):
    '''
    Return a list that contains a fortran comment
    indicating the molecule and spectral band, followed by 
    assignment statements for k-tables for a temperature
    and a g.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    lines = []
    for f in (comment_header,):
        lines.append(f(param))
        
    lines.extend(ktable(param, adjust_wgt=adjust_wgt))
    
    return lines



def kdist_param_gas(params, adjust_wgt=None):
    '''
    Return a list of fortran statements that form
    an if statement covering the k-tables for all 
    spectral bands for a given molecule.  

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    ls_gas: list
        List of fortran statements when joined assigns all the
        k-table values for all spectral bands for the SAME molecule.

    Example
    -------

         if (ib == 1) then                                                     
            ! h2o band1                                                        
            kg(:, 1, 1) = (/                                                   
     &   1.343974e-15,   1.350713e-15,   1.357494e-15,   1.364311e-15,         
     &   1.371176e-15,   1.378072e-15,   1.385008e-15,   1.392013e-15,         
     ...
         else if (ib == 11) then                                               
            ! h2o band9                                                        
            kg(:, 1, 1) = (/                                                   
     &   1.547249e-20,   1.579948e-20,   1.613146e-20,   1.646807e-20,         
     &   1.680980e-20,   1.715557e-20,   1.750571e-20,   1.786126e-20, 
     ...
     &   3.872232e-20,   3.693864e-20                                          
     &/) 
    '''
    molecules = [param['molecule'] for param in params]
    try:
        assert all([molecule == molecules[0] for molecule in molecules])
    except AssertionError:
        raise('All input param dicts should be for the same gas.')
        
    ls_gas = []
    for i, param in enumerate(params):
        if i == 0:
            s_if = 'if (ib == {}) then'
        else:
            s_if = 'else if (ib == {}) then'
        
        s_if = s_if.format(band_map()[param['band']])
                 
        ls = kdist_param_gasband(param, adjust_wgt=adjust_wgt)
        ls = [3 * ' ' + l for l in ls]
        ls = [s_if] + ls
        
        ls_gas.extend(ls)
       
    s = "write (*, *) 'k-table unavailable for {} band:', ib"
    s = s.format(molecules[0].upper())
    ls_else = []
    ls_else.append(s)
    ls_else.append('stop')
    ls_else = [3 * ' ' + l for l in ls_else]
    
    ls_gas.append('else')
    ls_gas.extend(ls_else)
    ls_gas.append('end if')      
    return ls_gas



def gas2mid(gas):
    d = {'h2o': 1, 'co2': 2, 'o3': 3, 'n2o': 4, 'ch4': 5, 'o2':6}
    return d[gas]


def kdist_param(adjust_wgt=None):
    '''
    Return list of fortran statements that, when joined with '\n',
    form if-statements that assign k-table values for all spectral
    bands of all molecules.

    Example
    -------
    if (mid == 1) then                                                   
      if (ib == 1) then 
        ...
    else if (mid == 5) then                                                   
      if (ib == 8) then 
        ...
    end if
    '''
    gasband_gs = [h2o_gasbands(), co2_gasbands(), o3_gasbands(),
                  n2o_gasbands(), ch4_gasbands()]
    
    lines = []
    for i, gasbands in enumerate(gasband_gs):

        params = [bestfit.kdist_params(molecule=gas, band=band)
                  for gas, band in gasbands]
        
        if params:
            
            gas = params[0]['molecule']
            mid = gas2mid(gas)
        
            if i == 0:
                s_if = 'if (mid == {}) then'
            else:
                s_if = 'else if (mid == {}) then'
            s_if = s_if.format(mid)
        
            ls = kdist_param_gas(params, adjust_wgt=adjust_wgt)
            ls = [3 * ' ' + l for l in ls]
            ls = [s_if] + ls
        
            lines.extend(ls)
    
    s = "write (*, *) 'k-table unavailable for gas id:', mid"
    ls_else = []
    ls_else.append(s)
    ls_else.append('stop')
    ls_else = [3 * ' ' + l for l in ls_else]
    
    lines.append('else')
    lines.extend(ls_else)
    lines.append('end if')     
    return lines



def subroutine(adjust_wgt=None):
    '''
    Return list of lines of fortran which, when joined by '\n', form
    the subroutine `get_kdist_ktable()`.  This subroutine returns
    the k-table given `mid` and `ib`.
    '''
    ls = ('subroutine get_kdist_ktable(mid, ib, kg)',
          '! Get the dgs and k-tables corresponding to the lblnew bestfit parameters',
          '',
          'implicit none',
          '',
          'integer, parameter :: max_ng = 15  ! max number of g-interval allowed',
          'integer, parameter :: nl = 52  ! number of pressures',
          'integer, parameter :: nt = 5   ! number of temperatures',
          '',
          'integer :: mid ! gas id',
          'integer :: ib  ! spectral band number',
          'real :: kg(nl, nt, max_ng)  ! table of k (wgt & w_diffuse included.)',
          '',
          '',
          '')
    
    lines = list(ls)
    lines = lines + kdist_param(adjust_wgt=adjust_wgt)
    lines.append('return')
    lines.append('end')
    return lines



def file_content(adjust_wgt=None):
    '''
    Return a piece of fortran that defines the
    subroutine get_kdist_ktable().
    '''
    lines = subroutine(adjust_wgt=adjust_wgt)
    lines = [6 * ' ' + l for l in lines]
    s = '\n'.join(lines)
    return s



def wgt(param):
    '''
    Return a fortran assignment statement for
    the `wgt` values for a particular molecule
    and spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    vs = [v for ref in param['wgt'] for v in ref]
    s = vector_to_F77(vs, 
                      num_values_per_line=3, dtype=float)
    ls = ['wgt(1:ng) = (/',
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)



def w_diffuse(param):
    '''
    Return a fortran assignment statement for
    the `w_diffuse` values for a particular molecule
    and spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    vs = [v for ref in param['w_diffuse'] for v in ref]
    s = vector_to_F77(vs, 
                      num_values_per_line=3, dtype=float)
    ls = ['w_diffuse(1:ng) = (/',
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)



def gasband_str_funcs():
    return (comment_header,
            getl_ng,
            dgs)



def kdist_param_gasband_kdist_bestfits(param):
    '''
    Return the following list of fortran statements:
    1. Comment that indicates which molecule and spectral band.
    2. Assign the value of `ng` for molecule and spectral band.
    3. Assign the values of `dgs` for molecule and spectral band.

    Parameters
    ----------
    param: dict
           Dictionary of input parameters for lblnew-bestfit.
    '''
    print(param['molecule'], param['band'])
    return [f(param) for f in gasband_str_funcs()]



def kdist_param_gas_kdist_bestfits(params):
    '''
    Return list of fortran statements which, when
    joined by '\n', form an if-statement that covers
    the assignment of values for `ng` and `dgs` for
    all spectral bands of some molecule.  
    
    (Deprecated: The format described in this function
     is currently not used.)
    '''
    molecules = [param['molecule'] for param in params]
    try:
        assert all([molecule == molecules[0] for molecule in molecules])
    except AssertionError:
        raise('All input param dicts should be for the same gas.')
        
    ls_gas = []
    for i, param in enumerate(params):
        if i == 0:
            s_if = 'if (ib == {}) then'
        else:
            s_if = 'else if (ib == {}) then'
        
        s_if = s_if.format(band_map()[param['band']])
                 
        ls = kdist_param_gasband_kdist_bestfits(param)
        ls = [3 * ' ' + l for l in ls]
        ls = [s_if] + ls
        
        ls_gas.extend(ls)
       
    s = "write (*, *) 'k-dist bestfits unavailable for {} band', ib"
    s = s.format(molecules[0].upper())
    ls_else = []
    ls_else.append(s)
    ls_else.append('stop')
    ls_else = [3 * ' ' + l for l in ls_else]
    
    ls_gas.append('else')
    ls_gas.extend(ls_else)
    ls_gas.append('end if')      
    return ls_gas



def kdist_param_kdist_bestfits():
    '''
    Return list of fortran assignment statements that cover
    all `ng` and `dgs` for all spectral bands and for all
    molecule.
    '''
    gasband_gs = [h2o_gasbands(), co2_gasbands(), o3_gasbands(),
                  n2o_gasbands(), ch4_gasbands()]

    params = [bestfit.kdist_params(molecule=molecule, band=band)
              for l in gasband_gs for molecule, band in l]

    ls = []
    for param in params:
        ls_param = kdist_param_gasband_kdist_bestfits(param)
        ls.extend(ls_param)
        ls.append('')
    return ls



def subroutine_kdist_bestfits():
    '''
    Return list of fortran statements which, when joined
    by '\n', form a subroutine which returns `ng` and `dgs`.
    '''
    ls = ('subroutine get_kdist_bestfits(ng, dgs)',
          '!     Get the lblnew bestfit parameters',
          '',
          'implicit none',
          '',
          'integer, parameter :: ngas = 5',
          'integer, parameter :: nband = 11',
          'integer, parameter :: max_ng = 15  ! max number of g-interval allowed',
          '',
          'integer :: ng(ngas, nband) ! number of g-intervals', 
          'real :: dgs(max_ng, ngas, nband) ! Planck-weighted k-dist function',)
    
    lines = list(ls)
    lines = lines + kdist_param_kdist_bestfits()
    lines.append('return')
    lines.append('end')
    return lines



def file_content_kdist_bestfits():
    lines = subroutine_kdist_bestfits()
    lines = [6 * ' ' + l for l in lines]
    s = '\n'.join(lines)
    return s



