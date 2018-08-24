
# coding: utf-8

# In[1197]:


import os
import ast
import json
import importlib 
import itertools
import collections
import pprint

from bokeh.io import output_notebook, show
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.models import Range1d, Legend, ColumnDataSource, FactorRange
from bokeh.palettes import all_palettes
from bokeh.transform import factor_cmap

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


import climatools.lblnew.bestfit_params as bestfits
from climatools.lblnew import setup_bestfit, setup_overlap
import climatools.lblnew.pipeline as pipe_lblnew
import climatools.cliradlw.setup as setup_cliradlw
import climatools.cliradlw.pipeline as pipe_cliradlw

import climatools.html.html as climahtml
from climatools.lblnew.dataio import *
from climatools.plot.plot import *


from IPython import display

#importlib.reload(bestfits)
#importlib.reload(setup_bestfit)
#importlib.reload(setup_overlap)
#importlib.reload(pipe_lblnew)
#importlib.reload(setup_cliradlw)
#importlib.reload(pipe_cliradlw)


# In[1198]:


output_notebook()


# In[1199]:


'''
Get the clirad-lw and lblnew `param`s for all spectral bands.  
These are returned by functions `clirad_params_atm` and
`lblnew_params_atm`, respectively.
'''

def molecules_byband_atm():
    return {1: {'h2o': 'atmpro'},
            2: {'h2o': 'atmpro'}, 
            3: {'co2': 0.0004, 'h2o': 'atmpro', 'n2o': 3.2e-07},
            4: {'co2': 0.0004, 'h2o': 'atmpro'},
            5: {'co2': 0.0004, 'h2o': 'atmpro'},
            6: {'co2': 0.0004, 'h2o': 'atmpro'},
            7: {'co2': 0.0004, 'h2o': 'atmpro', 'o3': 'atmpro'},
            8: {'h2o': 'atmpro'},
            9: {'ch4': 1.8e-06, 'h2o': 'atmpro', 'n2o': 3.2e-07},
            10: {'h2o': 'atmpro'},
            11: {'co2': 0.0004, 'h2o': 'atmpro'}}


def greyabsorbers_by_band_atm():
    return {1: {'con': 'atmpro'},
            2: {'con': 'atmpro'},
            3: {'con': 'atmpro'},
            4: {'con': 'atmpro'},
            5: {'con': 'atmpro'},
            6: {'con': 'atmpro'}, 
            7: {'con': 'atmpro'},
            8: {'con': 'atmpro', 'n2o': 3.2e-7}, 
            9: {'con': 'atmpro'}, 
            10: None,
            11: None}



def clirad_params_atm(atmpro='mls'):
    '''
    Return the input parameter dictionaries for the
    (band, molecule)s in the toy atmosphere
    (defined in molecules_byband_atm()).  Note that
    molecule here refers to a dictionary containing 
    the concentration for one or more gases.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile: 'mls', 'saw' or 'trp'.
    d: dict
        Dictionary of {band: param} type.
    '''
    d = {}
    for band, molecule in molecules_byband_atm().items():
        for param in setup_cliradlw.test_cases():
            if [band] == param['band'] and molecule == param['molecule']:
                param['atmpro'] = atmpro
                d[band] = param
                break                
    return d



def clirad_params_atm_singlerun(atmpro='mls'):
    '''
    Define the input parameter dictionary (or `param`) of
    a clirad-lw run and return it.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''
    param0 = {'band': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
              'commitnumber': '8f82f9b',
              'molecule': {'ch4': 1.8e-06,
                           'co2': 0.0004,
                           'h2o': 'atmpro',
                           'n2o': 3.2e-07,
                           'o3': 'atmpro'}}
    
    d_atmpros = {'mls': 294, 'saw': 257, 'trp': 300}
    
    param = param0.copy()
    param['atmpro'] = atmpro
    param['tsfc'] = d_atmpros[atmpro]
    
    d = {}
    d['all'] = param
    return d



def analysis_dirs_atm(atmpro='mls'):
    '''
    Maps spectral band to the absolute path of the
    clirad-lw run in which the toy atmosphere's
    radiation is computed.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''
    params = clirad_params_atm(atmpro=atmpro)
    return {band: pipe_cliradlw.get_analysis_dir(param=param,
                                                 setup=setup_cliradlw) 
            for band, param in params.items()}



def lblnew_params_atm(atmpro='mls'):
    '''
    Maps band to absolute path of the 
    lblnew run in which the toy atmosphere's
    radiation is computed.  
    
    The toy atmosphere's content is 
    defined by molecules_byband_atm().

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    d: dict
    {band: param} dictionary for the lblnew runs.
    '''
    dirs = analysis_dirs_atm(atmpro=atmpro)
    
    d = {}
    for band, dirname in dirs.items():
        with open(os.path.join(dirname, 'param.py'), 
                  mode='r', encoding='utf-8') as f:
            _, l = f.readlines()
        
        s = l.split('=')[1].strip()
        d[band] = ast.literal_eval(s)
    return d


# In[1200]:


def db_getdir():
    atmpro = 'mls'
    params = clirad_params_atm_singlerun(atmpro=atmpro)
    param = params['all']
    
    fdir = pipe_cliradlw.get_fortran_dir(param=param, 
                                         setup=setup_cliradlw)
    return fdir


def db_ktable():
    fdir = db_getdir()    
    fpath = os.path.join(fdir, 'ktable.dat')
    
    df = pd.read_csv(fpath, sep=r'\s+')
    df = df.set_index(['band', 'mid', 'il', 'it', 'g'])
    ds = xr.Dataset.from_dataframe(df)
    return ds


def db_ng_dgs():
    fdir = db_getdir()
    fpath = os.path.join(fdir, 'ng_dgs.dat')
    
    df = pd.read_csv(fpath, sep=r'\s+')
    df = df.set_index(['band', 'mid', 'g'])
    ds = xr.Dataset.from_dataframe(df)
    return ds



def show_makeup():
    '''
    Display table showing the concentrations
    of the gases in each spectral band
    '''
    df = pd.DataFrame()

    for band, molecule in molecules_byband_atm().items():
        for name, conc in molecule.items():
            df.loc[name, band] = str(conc)

    df = df.fillna(0)
    df.columns.name = 'clirad band'
    df.index.name = 'molecule'
    
    display.display(df)
    
    display.display(
        display.Markdown('*TABLE.* Non-grey absorbers in the atmosphere.'))



def show_grey_makeup():
    df = pd.DataFrame()
    
    for band, molecule in greyabsorbers_by_band_atm().items():
        if molecule == None:
            pass
        else:
            for name, conc in molecule.items():
                df.loc[name, band] = str(conc)
                
    df = df.fillna(0)
    df.columns.name = 'clirad band'
    df.index.name = 'absorber'
    
    display.display(df)
    display.display(
        display.Markdown('*TABLE.* Grey absorbers in the atmosphere.')
    )


# In[1202]:


def load_output_file(path_csv):
    '''
    Load output file to xarray.Dataset.  
    The output file can be from either lblnew
    or clirad, as long as it's .csv and multi-index
    format.
    
    Parameters
    ----------
    path_csv: str
              Path to the .csv file to be loaded.
    ds: xarray.Dataset
        Data in the input file in the form of an xarray.Dataset.
    '''
    toindex = ['i', 'band', 'pressure', 'igg', 'g']    
    df = pd.read_csv(path_csv, sep=r'\s+')
    df = df.set_index([i for i in toindex if i in df.columns])
    df = df.rename(columns={'sfu': 'flug',
                            'sfd': 'fldg',
                            'fnet': 'fnetg',
                            'coolr': 'coolrg'})
    ds = xr.Dataset.from_dataframe(df)

    for l in ('level', 'layer'):
        if l in ds.data_vars:
            if len(ds[l].dims) > 1:
                surface = {d: 0 for d in ds.dims if d != 'pressure'}
                coord_level = ds[l][surface]
                ds.coords[l] = ('pressure', coord_level)
            else:
                ds.coords[l] = ('pressure', ds[l])
    
    return ds


# In[1203]:


def lblnew_setup(param=None):
    '''
    Returns the setup module and output filenames for 
    an lblnew input parameter dictionary, indicating
    whether a filename is for 'crd' (line-by-line)
    or 'wgt' (k-dist), these being different
    for lblnew-bestfit and lblnew-overlap.
    
    Parameters
    ----------
    param: dict
        lblnew input parameter dictionary.
    '''
    if 'ng_refs' in param:
        return {'setup': setup_bestfit,
                'fname_flux_crd': 'output_flux.dat',
                'fname_cool_crd': 'output_coolr.dat',
                'fname_flux_wgt': 'output_wfluxg.dat',
                'fname_cool_wgt': 'output_wcoolrg.dat'}
    else:
        return {'setup': setup_overlap,
                'fname_flux_crd': 'output_flux.dat',
                'fname_cool_crd': 'output_coolr.dat',
                'fname_flux_wgt': 'output_wflux.dat',
                'fname_cool_wgt': 'output_wcoolr.dat'}

    

def load_lblnew_data(param):
    '''
    Load all output files from a given lblnew run.

    Parameters
    ----------
    param: dict
        lblnew input parameter dictionary.
    data_dict: dict
        xr.Datasets for output 'crd' and 'wgt'
        fluxes and cooling rates.
    '''
    fname_dsname = [('fname_flux_crd', 'ds_flux_crd'),
                    ('fname_cool_crd', 'ds_cool_crd'),
                    ('fname_flux_wgt', 'ds_flux_wgt'),
                    ('fname_cool_wgt', 'ds_cool_wgt')]
    
    d = lblnew_setup(param)
    dir_fortran = pipe_lblnew.get_dir_case(param, setup=d['setup'])
    
    data_dict = {}
    for fname, dsname in fname_dsname:
        fpath = os.path.join(dir_fortran, d[fname])
        data_dict[dsname] = load_output_file(fpath)
    return data_dict


# In[1204]:


def crd_data_atm(params_atm):
    '''
    Gather together the 'crd' fluxes and cooling rates
    from all spectral bands in the toy atmosphere.

    Parameters
    ----------
    params_atm: dict
        {band: lblnew input parameter dictionary}
                
    d: dict
       'flux': xr.Dataset. [pressure, band]
            Fluxes.
       'cool': xr.Dataset. [pressure, band]
            Cooling rate.
    '''
    
    results_atm = {band: load_lblnew_data(param) 
                   for band, param in params_atm.items()}
    
    bands = [band for band, _ in params_atm.items()]
    fluxs = [d['ds_flux_crd'] for _, d in results_atm.items()]
    cools = [d['ds_cool_crd'] for _, d in results_atm.items()]
    
    d = {}
    d['flux'] = xr.concat(fluxs, dim=bands).rename({'concat_dim': 'band'})
    d['cool'] = xr.concat(cools, dim=bands).rename({'concat_dim': 'band'})
    return d        
        
        

def clirad_data_atm(params_atm):
    '''
    Gather together clirad-lw's fluxes and cooling rates
    from all spectral bands in the toy atmosphere. 
    
    Parameters
    ----------
    params_atm: dict
        {band: cliradlw input parameter dictionary}

    d: dict
    'flux': xr.Dataset. [pressure, band]
         Fluxes.
    'cool': xr.Dataset. [pressure, band]
         Cooling rate.
    '''
    
    dirnames = [pipe_cliradlw.get_fortran_dir(param,
                                              setup=setup_cliradlw)
                for _, param in params_atm.items()]
    
    fpaths_flux = [os.path.join(n, 'output_flux.dat') for n in dirnames]
    fpaths_cool = [os.path.join(n, 'output_coolr.dat') for n in dirnames]
    
    fluxs = [load_output_file(p) for p in fpaths_flux]    
    cools = [load_output_file(p) for p in fpaths_cool]
    
    d = {}
    d['flux'] = sum(fluxs)
    d['cool'] = sum(cools)
    return d



# In[1205]:




import rtmtools.clirad.sw.wrangle as cliradwrangle

import importlib
importlib.reload(cliradwrangle)

def oldclirad_data_atm():
    '''
    Load the OLD clirad's results. mls only.

    Parameters
    ----------
    d: dict
    'flux': xr.Dataset. [pressure, band]
         Fluxes.
    'cool': xr.Dataset. [pressure, band]
         Cooling rate.
    '''
    fpath = os.path.join('/chia_cluster/home/jackyu/radiation',
                         'clirad-lw',
                         'LW',
                         'examples',
                         'mls75_h2o_atmpro_co2_.0004_o3_atmpro_n2o_3.2e-7_ch4_1.8e-6_H2012',
                         'OUTPUT_CLIRAD.dat')
    
    ds = cliradwrangle.load_OUTPUT_CLIRAD(readfrom=fpath)
    
    ds_cool = xr.Dataset()
    ds_cool.coords['pressure'] = ('pressure', ds['layer_pressure'])
    ds_cool.coords['band'] = ('band', ds['spectral_band'])
    ds_cool['coolrg'] = (('band', 'pressure'), - ds['heating_rate'])
    
    ds_flux = xr.Dataset()
    ds_flux.coords['pressure'] = ('pressure', ds['level_pressure'])
    ds_flux.coords['band'] = ('band', ds['spectral_band'])
    ds_flux['flug'] = (('band', 'pressure'), ds['flux_up'])
    ds_flux['fldg'] = (('band', 'pressure'), ds['flux_down'])
    ds_flux['fnetg'] = (('band', 'pressure'), ds['net_flux'])
    
    
    d = {}
    d['cool'] = ds_cool
    d['flux'] = ds_flux
    return d


# In[1206]:


def fmt_cool(ds_in):
    '''
    Deal with dimensions that are not the 'pressure/layer'
    dimension, to prepare the dataset for 
    pressure vs cooling rate plots.
    
    Parameters
    ----------
    ds_in: xarray.Dataset
        Cooling rate.
    '''
    ds = ds_in.copy(deep=True)
    if 'igg' in ds.dims:
        ds = ds.sel(igg=1)

    if 'g' in ds.dims:
        ds = ds.sum('g')
            
    if 'i' in ds.dims:
        ds = ds.sel(i=ds.dims['i'])
    
    if 'band' in ds.dims:
        try:
            ds = ds.squeeze('band')
        except ValueError:
            ds = ds.sum('band')
                
    return ds['coolrg']



def nice_xlims(pltdata=None, prange=None):
    '''
    For a line plot with the domain on the y-aixs
    and the image on the x-axis, work out a suitable 
    displayed range for the x-axis, given a domain 
    range.  This also works when multiple lines plotted.

    Parameters
    ----------
    pltdata: list
        Plotting data. A list of dictionaries, 
        each one containing the data and plot
        attributes for a curve.
    prange: tuple
        y-axis (domain) range over which the
        x-axis (codomain) range will be based.
    '''
    def get_slice(srs):
        return srs.sel(pressure=slice(*prange))
    
    srss = [d['srs'] for d in pltdata]
    vmin = min([get_slice(srs).min() for srs in srss])
    vmax = max([get_slice(srs).max() for srs in srss])
    dv = (vmax - vmin) * .01
    return float(vmin - dv), float(vmax + dv)


    
def plt_cool_bokeh(pltdata=None, 
                   y_axis_type='linear', prange=(50, 1050)):
    '''
    Make line plot(s) for dataset(s), with the domain 
    on the y-aixs and the image on the x-axis.

    Parameters
    ----------
    pltdata: list
        Plotting data. A list of dictionaries, 
        each one containing the data and plot
        attributes for a curve.
    y_axis_type: string
        Plot y-scale. 'linear', or 'log'.
    prange: tuple
        y-axis (domain) range over which the
        x-axis (codomain) range will be based.
    p2: bokeh.plotting.figure
        Plotted figure.
    '''
    ymin = 1e-2 
    ymax = 1020
    
    p2 = figure(y_axis_type=y_axis_type, plot_width=300)
    xmin, xmax = nice_xlims(pltdata, prange=prange)
    
    rs = []
    for d in pltdata:
        rd = []
        if 'marker' in d:
            r_mark = getattr(p2, d['marker'])(d['srs'].values, 
                        d['srs'].coords['pressure'].values,
                        color=d['color'], alpha=.7)
            rd.append(r_mark)
        r_line = p2.line(d['srs'].values, 
                         d['srs'].coords['pressure'].values,
                         color=d['color'], alpha=d['alpha'], 
                         line_width=d['line_width'], 
                         line_dash=d['line_dash'])
        rd.append(r_line)
      
        rs.append(rd)
        
    p2.y_range = Range1d(ymax, ymin)  
    p2.yaxis.axis_label = 'pressure [mb]'
    
    p2.x_range = Range1d(xmin, xmax)
    p2.xaxis.axis_label = 'cooling rate [K/day]'
    
    items = [(d['label'], r) for r, d in zip(rs, pltdata)]
    legend = Legend(items=items, location=(10, 0))
    legend.label_text_font_size = '8pt'
    p2.add_layout(legend, 'above')
    p2.legend.orientation = 'horizontal'
    p2.legend.location = 'top_center'
    
    return p2


# In[1207]:


def pltdata_cool(atmpro='mls'):
    '''
    Prepare the plotting data for plotting cooling
    rate profiles that is compatible with
    plot_cool_bokeh(), and set the plot attibutes 
    for each curve.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    data: dict
        Plotting data. A list of dictionaries, 
        each one containing the data and plot
        attributes for a curve.            
    '''
    d_clirad_singlerun = clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))
    d_clirad = clirad_data_atm(clirad_params_atm(atmpro=atmpro))
    d_crd = crd_data_atm(lblnew_params_atm(atmpro=atmpro))

    ds_clirad_singlerun = d_clirad_singlerun['cool']
    ds_clirad = d_clirad['cool']
    ds_crd = d_crd['cool']

    colors = all_palettes['Set1'][4]
    
    data = [
        {'label': 'CLIRAD (single-run)',
        'srs': fmt_cool(ds_clirad_singlerun),
        'line_dash': 'dashed', 'line_width': 5,
        'color': colors[1], 'alpha': .6},
        {'label': 'CRD',
         'srs': fmt_cool(ds_crd),
         'line_dash': 'solid', 'line_width': 1.5,
         'marker': 'circle', 'marker_size': 5,
         'color': colors[2], 'alpha': 1}
    ]
#        {'label': 'CLIRAD',
#         'srs': fmt_cool(ds_clirad),
#         'line_dash': 'dashed', 'line_width': 5,
#         'color': colors[0], 'alpha': .6}
        
    # include old CLIRAD's results for mls profile
    if atmpro == 'mls':
        d_oldclirad = oldclirad_data_atm()
        ds_oldclirad = d_oldclirad['cool']        
        data.append(
            {'label': 'old CLIRAD (H2012)',
             'srs': fmt_cool(ds_oldclirad),
             'line_dash': 'solid', 'line_width': 1.5,
             'marker': 'square', 'marker_size': 3,
             'color': colors[3], 'alpha': .5})
    return data



def pltdata_cooldiff(atmpro='mls'):
    '''
    Prepare the plotting data for plotting cooling
    rate difference profiles that is compatible with
    plot_cool_bokeh(), and set the plot attibutes 
    for each curve.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    data: dict
        Plotting data. A list of dictionaries, 
        each one containing the data and plot
        attributes for a curve.            
    '''
    d_clirad_singlerun = clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))
    d_clirad = clirad_data_atm(clirad_params_atm(atmpro=atmpro))
    d_crd = crd_data_atm(lblnew_params_atm(atmpro=atmpro))
    
    ds_clirad_singlerun = d_clirad_singlerun['cool']
    ds_clirad = d_clirad['cool']
    ds_crd = d_crd['cool']
    
    ds_diff = ds_clirad_singlerun - ds_crd
    
    colors = all_palettes['Set1'][4]
    
    data = [
        {'label': 'CLIRAD (single-run) - CRD',
         'srs': fmt_cool(ds_diff),
         'line_dash': 'solid', 'line_width': 1.5, 
         'marker': 'circle', 'marker_size': 7,
         'color': colors[3], 'alpha': .8}
    ]
    
    # include old CLIRAD's results for mls profile
    if atmpro == 'mls':
        d_oldclirad = oldclirad_data_atm()
        ds_oldclirad = d_oldclirad['cool']
        ds_oldclirad.coords['pressure'] = ds_crd.coords['pressure']
        ds_diff_old = ds_oldclirad.sum('band') - ds_crd.sum('band')
        data.append(
            {'label': 'old CLIRAD (H2012) - CRD',
             'srs': fmt_cool(ds_diff_old),
             'line_dash': 'dashed', 'line_width': 4,
             'color': colors[1], 'alpha': .5}
        )
    return data



def show_cool(atmpro='mls'):
    '''
    Produce figure with the following panes:
      1. Cooling rate profiles with linear pressure-axis.
      2. Cooling rate profile with log pressure-axis.
      3. Coolling rate profile difference with log 
         pressure-axis.
    and display the figure.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''
    data_cool = pltdata_cool(atmpro=atmpro)
    p_cool_liny = plt_cool_bokeh(pltdata=data_cool)
    p_cool_logy = plt_cool_bokeh(pltdata=data_cool, 
                                 y_axis_type='log',
                                 prange=(.01, 200))
    
    data_cooldiff = pltdata_cooldiff(atmpro=atmpro)
    p_cooldiff_logy = plt_cool_bokeh(pltdata=data_cooldiff,
                                     y_axis_type='log',
                                     prange=(.01, 200))
    
    everything = gridplot(p_cool_liny, p_cool_logy, 
                          p_cooldiff_logy,
                          ncols=3)
    show(everything)
    display.display(
        display.Markdown('*FIGURE.* Cooling rates & difference.'))


    


# In[1208]:





def hist_band_vs_flux(da, title='Title'):
    '''
    Plot the histogram: spectral band vs flux

    Parameters
    ----------
    da: xarray.DataArray (band,)
        Flux.
    p: bokeh.plotting.figure
        Histogram plot.
    '''
    bands = [str(b.values) for b in da['band']]

    source = ColumnDataSource(
        data={'band': bands, 'flux': da.values})

    p = figure(x_range=bands, title=title)
    p.vbar(source=source, x='band', top='flux', width=.9)

    p.yaxis.axis_label = 'flux (W m-2)'
    p.xaxis.axis_label = 'spectral band'
    
    return p




def show_hist_flux(atmpro='mls'):
    '''
    Display figure with the following band-vs-flux
    histograms:
        1. Upward flux at TOA. CLIRAD - CRD.
        2. Downward flux at surface. CLIRAD- CRD.
        3. Atmosphere heating.  CLIRAD - CRD.

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''
    def fmt(da_in):
        da = da_in.copy(deep=True)
        
        if 'i' in da.dims:
            da = da.sel(i=len(da['i']))
        
        if 'igg' in da.dims:
            da = da.sel(igg=1)
                
        if 'g' in da.dims:
            da = da.sum('g')
        return da

    ds_crd = crd_data_atm(lblnew_params_atm(atmpro=atmpro))['flux']
    ds_clirad = clirad_data_atm(
        clirad_params_atm(atmpro=atmpro))['flux']
    ds_clirad_singlerun = clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))['flux']
    
    ip, varname = 0, 'flug'
    da = (ds_clirad_singlerun - ds_crd).isel(pressure=ip)[varname]
    da = fmt(da)
    p_toa = hist_band_vs_flux(da, 
        title='TOA flux. CLIRAD (single-run) - CRD.')

    ip, varname = -1, 'fldg'
    da = (ds_clirad_singlerun - ds_crd).isel(pressure=ip)[varname]
    da = fmt(da)
    p_sfc = hist_band_vs_flux(da, 
        title='SFC flux. CLIRAD (single-run) - CRD.')    
    
    atm_crd = (ds_crd.isel(pressure=0) 
               - ds_crd.isel(pressure=-1))['fnetg']
    atm_clirad_singlerun = (ds_clirad_singlerun.isel(pressure=0) 
                  - ds_clirad_singlerun.isel(pressure=-1))['fnetg'] 
    da = atm_clirad_singlerun - atm_crd
    da = fmt(da)
    p_atm = hist_band_vs_flux(da, 
        title='Atmosphere heating. CLIRAD (single-run) - CRD.')

    everything = gridplot(p_toa, p_sfc, p_atm, ncols=3, 
                          plot_width=300, plot_height=300)
    
    show(everything)
    display.display(
        display.Markdown('*FIGURE.* Difference between CLIRAD and CRD'
          ' in TOA, SFC and net atmosphere flux,'
          ' in each spectral band.'))


    
def show_tb_flux(atmpro='mls'):
    '''
    Display the table:
    --------------------------------------------------------------------
                      | up flux at TOA | down flux at SFC | atm heating
    --------------------------------------------------------------------
    clirad (sum) - CRD|                |                  |
    clirad - CRD      |                |                  |
    CRD               |                |                  |
    --------------------------------------------------------------------

    Parameters
    ----------
    atmpro: string
        Atmosphere profile.
    '''    
    def fmt(da_in):
        da = da_in.copy(deep=True)
        
        if 'i' in da.dims:
            da = da.sel(i=len(da['i']))
        
        if 'igg' in da.dims:
            da = da.sel(igg=1)
                
        if 'g' in da.dims:
            da = da.sum('g')
            
        if 'band' in da.dims:
            try:
                da = da.squeeze('band')
            except ValueError:
                da = da.sum('band')                
        return da
    
    ds_crd = crd_data_atm(lblnew_params_atm(atmpro=atmpro))['flux']
    olr_crd = ds_crd['flug'].isel(pressure=0)
    sfc_crd = ds_crd['fldg'].isel(pressure=-1)
    atm_crd = (ds_crd.isel(pressure=0)
               - ds_crd.isel(pressure=-1))['fnetg']
    
    ds_clirad = clirad_data_atm(
        clirad_params_atm(atmpro=atmpro))['flux']
    olr_clirad = ds_clirad['flug'].isel(pressure=0)
    sfc_clirad = ds_clirad['fldg'].isel(pressure=-1)
    atm_clirad = (ds_clirad.isel(pressure=0)
                  - ds_clirad.isel(pressure=-1))['fnetg']

    ds_clirad_singlerun = clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))['flux']
    olr_clirad_singlerun = ds_clirad_singlerun['flug'].isel(pressure=0)
    sfc_clirad_singlerun = ds_clirad_singlerun['fldg'].isel(pressure=-1)
    atm_clirad_singlerun = (ds_clirad_singlerun.isel(pressure=0)
                  - ds_clirad_singlerun.isel(pressure=-1))['fnetg']
    
    if atmpro == 'mls':
        ds_oldclirad = oldclirad_data_atm()['flux']
        ds_oldclirad['pressure'] = ds_crd['pressure']
        olr_oldclirad = ds_oldclirad['flug'].isel(pressure=0)
        sfc_oldclirad = ds_oldclirad['fldg'].isel(pressure=-1)
        atm_oldclirad = (ds_oldclirad.isel(pressure=0)
                         - ds_oldclirad.isel(pressure=-1))['fnetg']
        
    
    
    df = pd.DataFrame()
    df.index.name = 'Sum over bands'
    
    if atmpro == 'mls':
        df.loc['old CLIRAD - CRD', 
               'OLR flux'] = (fmt(olr_oldclirad)
                              - fmt(olr_crd)).values
        df.loc['old CLIRAD - CRD', 
               'SFC flux'] = (fmt(sfc_oldclirad)
                              - fmt(sfc_crd)).values
        df.loc['old CLIRAD - CRD', 
               'ATM heating'] = (fmt(atm_oldclirad)
                                 - fmt(atm_crd)).values
    
    df.loc['CLIRAD (single-run) - CRD', 
           'OLR flux'] = (fmt(olr_clirad_singlerun) 
                          - fmt(olr_crd)).values
    df.loc['CLIRAD (single-run) - CRD', 
           'SFC flux'] = (fmt(sfc_clirad_singlerun) 
                          - fmt(sfc_crd)).values
    df.loc['CLIRAD (single-run) - CRD', 
           'ATM heating'] = (fmt(atm_clirad_singlerun) 
                             - fmt(atm_crd)).values

    df.loc['CRD', 'OLR flux'] = fmt(olr_crd).values
    df.loc['CRD', 'SFC flux'] = fmt(sfc_crd).values
    df.loc['CRD', 'ATM heating'] = fmt(atm_crd).values
        
    df = df.astype('float').round(2)
    
    display.display(df)
    display.display(
        display.Markdown('*TABLE.* Difference between CLIRAD and CRD'
          ' in TOA, SFC and net atmosphere flux,'
          ' over all spectral bands. CRD\'s'
          ' TOA, SFC and net atmosphere flux,'
          ' over all spectral bands.'))


# In[1209]:


def show_html(s):
    display.display(display.HTML(s))

    
def show_markdown(s):
    display.display(display.Markdown(s))


def script():
    
    d_atm = {'mls': 'mid-latitude summer',
             'saw': 'sub-arctic winter',
             'trp': 'tropical'}
    
    title = ('## Results over entire range of molecules'
             ' and spectral bands')
    
    s_makeup = 'Makeup of atmosphere.'
    s_atmpro = '# {}'
    s_cool = 'Cooling rates. {}.'
    s_flux = 'Fluxes. {}.'
    
    atmpros = ['mls', 'saw', 'trp']
    
    # TOC
    show_markdown(title)
    show_markdown('### Table of Contents')
    show_html(climahtml.getHTML_hrefanchor(s_makeup))
    for atmpro in atmpros:
        show_markdown('**' + d_atm[atmpro] + '**')
        show_html(climahtml.getHTML_hrefanchor(s_cool.format(atmpro)))
        show_html(climahtml.getHTML_hrefanchor(s_flux.format(atmpro)))

        
    # Atmosphere makeup
    show_html(climahtml.getHTML_idanchor(s_makeup))
    show_markdown(climahtml.getMarkdown_sectitle(s_makeup))
    show_makeup()
    show_grey_makeup()
        
    for atmpro in atmpros:
        show_html(climahtml.getHTML_idanchor(s_cool.format(atmpro)))
        show_markdown(
            climahtml.getMarkdown_sectitle(s_cool.format(atmpro)))
        show_cool(atmpro=atmpro)
        show_html(climahtml.getHTML_idanchor(s_flux.format(atmpro)))
        show_markdown(
            climahtml.getMarkdown_sectitle(s_flux.format(atmpro)))
        show_hist_flux(atmpro=atmpro)
        show_tb_flux(atmpro=atmpro)
    
    
script()  


# In[ ]:


display.HTML('''<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit" value="Click here to toggle on/off the raw code."></form>''')

