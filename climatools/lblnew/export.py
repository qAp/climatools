
'''
This module is for exporting the data from lblnew-bestfit.
'''

import os
import itertools
import importlib

import numpy as np
import pandas as pd

import climatools.lblnew.bestfit_params as bestfit
import climatools.lblnew.setup_bestfit as setup_bestfit
import climatools.lblnew.pipeline as pipeline
from climatools.cliradlw import setup as setup_cliradlw


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



def vector_to_F77list(array, num_values_per_line=4, dtype=float):
    '''
    
    '''
    if dtype == float:
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



def vector_to_F77(array=None, num_values_per_line=None, dtype=None):
    lines = vector_to_F77list(array=array, 
                              num_values_per_line=num_values_per_line,
                              dtype=dtype)
    
    rlines = [5 * ' ' + '&' + l for l in lines]
    
    fortran = '\n'.join(rlines)
    return fortran




def comment_header(param):
    s = "! {} band{}"
    return s.format(param['molecule'], param['band'])


def ng(param):
    s = "ng = {:d}"
    return s.format(sum(param['ng_refs']))


def load_dgdgs(path):
    df = pd.read_csv(path, sep=r'\s+')

    df = df.set_index('g')    
    return df


def dgdgs_to_F77(dgdgs):
    lines = vector_to_F77list(dgdgs, num_values_per_line=3)
    
    rlines = []
    rlines.append(5 * ' ' + '&' + lines[0])
    for line in lines[1:-1]:
        rlines.append(5 * ' ' + '&' + line)
    rlines.append(5 * ' ' + '&' + lines[-1])
    
    return '\n'.join(rlines)


def dgs(param):
    fpath = os.path.join(
        pipeline.get_dir_case(param, setup=setup_bestfit),
        'dgdgs.dat')
    dgdgs = load_dgdgs(fpath)
    s = vector_to_F77(dgdgs['dgs'], 
                      num_values_per_line=4, dtype=float)
    ls = ['dgs(1:ng) = (/',
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)
    

def fpath_ktable(param=None):
    
    fortran_dir = pipeline.get_dir_case(param, setup=setup_bestfit)
          
    fpath_lin = os.path.join(fortran_dir, 'kg_lin.dat')
    fpath_nonlin = os.path.join(fortran_dir, 'kg_nonlin.dat')
    fpath = {'kg_lin': fpath_lin, 'kg_nonlin': fpath_nonlin}
    return fpath


def load_ktable(fpath):
    '''
    Returns k-table in the same format as in lblnew.f
    
    Parameter
    ---------
    fpath: string
        Path to the file 'ktable.dat', generated by "lblnew.f".
    ktable: array (number of (p, t) pairs, number of g-intervals)
        Absorption coefficient values calculated at selected 
        (pressure, temperature) pairs.
    '''
    try:
        df = pd.read_csv(fpath, sep=r'\s+')
    except pd.errors.EmptyDataError:
        print('No data at:', fpath)
        return np.zeros((3, 3, 4))

    df = df.set_index(['g', 'pressure', 'temperature'])
    ng = len(df.index.levels[0].value_counts())
    nl = len(df.index.levels[1].value_counts())
    ktable = df['k'].values.reshape(ng, nl, -1)
    ktable = np.transpose(ktable, axes=(1, 2, 0))
    return ktable


def ktable_to_F77(ktable, name):
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

    
def ktable(param):
    ng = sum(param['ng_refs'])

    d = fpath_ktable(param=param)

    wgt = np.array([v for vs in param['wgt'] for v in vs])
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
    



def kdist_param_gasband(param):
    '''
    Returns list of strings for some gas and band.
    '''
    lines = []
    for f in (comment_header, ng, dgs):
        lines.append(f(param))
        
    lines.extend(ktable(param))
    
    return lines


def kdist_param_gas(params):
    '''
    Returns list of strings for some gas.
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
                 
        ls = kdist_param_gasband(param)
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


def kdist_param():
    'Returns list of strings covering all gases and their bands'
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
        
            ls = kdist_param_gas(params)
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


def subroutine():
    ls = ('subroutine get_kdist_ktable(mid, ib, dgs, kg)',
          '! Get the dgs and k-tables corresponding to the lblnew bestfit parameters',
          '',
          'implicit none',
          '',
          'integer, parameter :: max_ng = 15  ! max number of g-interval allowed',
          'integer, parameter :: nl = 62  ! number of pressures',
          'integer, parameter :: nt = 5   ! number of temperatures',
          '',
          'integer :: mid ! gas id',
          'integer :: ib  ! spectral band number',
          'real :: dgs(max_ng)    ! Planck-weighted k-distribution function',
          'real :: kg(nl, nt, max_ng)  ! table of k (wgt & w_diffuse included.)',
          '',
          '',
          'integer :: ng ! number of g-intervals',
          '',
          '')
    
    lines = list(ls)
    lines = lines + kdist_param()
    lines.append('return')
    lines.append('end')
    return lines


def file_content():
    lines = subroutine()
    lines = [6 * ' ' + l for l in lines]
    s = '\n'.join(lines)
    return s




def wgt(param):
    vs = [v for ref in param['wgt'] for v in ref]
    s = vector_to_F77(vs, 
                      num_values_per_line=3, dtype=float)
    ls = ['wgt(1:ng) = (/',
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)



def w_diffuse(param):
    vs = [v for ref in param['w_diffuse'] for v in ref]
    s = vector_to_F77(vs, 
                      num_values_per_line=3, dtype=float)
    ls = ['w_diffuse(1:ng) = (/',
          s,
          5 * ' ' + '&' + '/)']
    return '\n'.join(ls)



def gasband_str_funcs():
    return (comment_header,
            ng,
            wgt,
            w_diffuse,)



def kdist_param_gasband_kdist_bestfits(param):
    '''
    Returns list of strings for some gas and band.
    '''
    print(param['molecule'], param['band'])
    return [f(param) for f in gasband_str_funcs()]



def kdist_param_gas_kdist_bestfits(params):
    '''
    Returns list of strings for some gas.
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
    'Returns list of strings covering all gases and their bands'
    gasband_gs = [h2o_gasbands(), co2_gasbands(), o3_gasbands(),
                  n2o_gasbands(), ch4_gasbands()]
    
    lines = []
    for i, gasbands in enumerate(gasband_gs):
        
        params = [bestfit.kdist_params(molecule=gas, band=band)
                  for gas, band in gasbands]
        
        gas = params[0]['molecule']
        mid = gas2mid(gas)
        
        if i == 0:
            s_if = 'if (mid == {}) then'
        else:
            s_if = 'else if (mid == {}) then'
        s_if = s_if.format(mid)
        
        ls = kdist_param_gas_kdist_bestfits(params)
        ls = [3 * ' ' + l for l in ls]
        ls = [s_if] + ls
        
        lines.extend(ls)
    
    s = "write (*, *) 'k-dist bestfits unavailable for gas id:', mid"
    s = s.format(mid)
    ls_else = []
    ls_else.append(s)
    ls_else.append('stop')
    ls_else = [3 * ' ' + l for l in ls_else]
    
    lines.append('else')
    lines.extend(ls_else)
    lines.append('end if')     
    return lines



def subroutine_kdist_bestfits():
    ls = ('subroutine get_kdist_bestfits(mid, ib, ng, wgt, w_diffuse)',
          '!     Get the lblnew bestfit parameters',
          '',
          'implicit none',
          '',
          'integer, parameter :: max_ng = 15  ! max number of g-interval allowed',
          '',
          'integer :: mid ! gas id',
          'integer :: ib  ! spectral band number',
          'integer :: ng ! number of g-intervals', 
          'real :: wgt(max_ng)',
          'real :: w_diffuse(max_ng)',)
    
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



