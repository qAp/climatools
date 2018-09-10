
# coding: utf-8

# In[1197]:

import os
import ast
import json
import importlib 
import itertools
import collections
import pprint

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib
import matplotlib.pyplot as plt

from bokeh.io import output_notebook, show
from bokeh.palettes import all_palettes
from bokeh.layouts import gridplot
from bokeh.plotting import figure

import climatools.lblnew.dataset as lbldata
import climatools.cliradlw.dataset as cliraddata
from climatools.atm.absorbers import nongreys_byband
from climatools.atm.absorbers import greys_byband

import climatools.html.html as climahtml
from climatools.lblnew.dataio import *
import climatools.plot.plot as plot


from IPython import display

importlib.reload(lbldata)
importlib.reload(cliraddata)
importlib.reload(plot)





output_notebook()




'''
Get the clirad-lw and lblnew `param`s for all spectral bands.  
These are returned by functions `clirad_params_atm` and
`lblnew_params_atm`, respectively.
'''


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
    params_atm = clirad_params_atm_singlerun(atmpro=atmpro)
    d_clirad_singlerun = cliraddata.clirad_data_atm(params_atm)
    
    params_atm = cliraddata.clirad_params_atm(atmpro=atmpro)
    d_clirad = cliraddata.clirad_data_atm(params_atm)

    params_atm = lbldata.lblnew_params_atm(atmpro=atmpro)
    d_crd = lbldata.crd_data_atm(params_atm)

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
    d_clirad_singlerun = cliraddata.clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))
    d_clirad = cliraddata.clirad_data_atm(cliraddata.clirad_params_atm(atmpro=atmpro))
    d_crd = lbldata.crd_data_atm(lbldata.lblnew_params_atm(atmpro=atmpro))
    
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
    p_cool_liny = plot.plt_vert_profile_bokeh(pltdata=data_cool)
    p_cool_logy = plot.plt_vert_profile_bokeh(pltdata=data_cool, 
                                 y_axis_type='log',
                                 prange=(.01, 200))
    
    data_cooldiff = pltdata_cooldiff(atmpro=atmpro)
    p_cooldiff_logy = plot.plt_vert_profile_bokeh(pltdata=data_cooldiff,
                                     y_axis_type='log',
                                     prange=(.01, 200))
    
    everything = gridplot(p_cool_liny, p_cool_logy, 
                          p_cooldiff_logy,
                          ncols=3)
    show(everything)
    display.display(
        display.Markdown('*FIGURE.* Cooling rates & difference.'))



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

    ds_crd = lbldata.crd_data_atm(lbldata.lblnew_params_atm(atmpro=atmpro))['flux']
    ds_clirad = cliraddata.clirad_data_atm(
        cliraddata.clirad_params_atm(atmpro=atmpro))['flux']
    ds_clirad_singlerun = cliraddata.clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))['flux']
    
    ip, varname = 0, 'flug'
    da = (ds_clirad_singlerun - ds_crd).isel(pressure=ip)[varname]
    da = fmt(da)
    p_toa = plot.hist_band_vs_flux(da, 
        title='TOA flux. CLIRAD (single-run) - CRD.')

    ip, varname = -1, 'fldg'
    da = (ds_clirad_singlerun - ds_crd).isel(pressure=ip)[varname]
    da = fmt(da)
    p_sfc = plot.hist_band_vs_flux(da, 
        title='SFC flux. CLIRAD (single-run) - CRD.')    
    
    atm_crd = (ds_crd.isel(pressure=0) 
               - ds_crd.isel(pressure=-1))['fnetg']
    atm_clirad_singlerun = (ds_clirad_singlerun.isel(pressure=0) 
                  - ds_clirad_singlerun.isel(pressure=-1))['fnetg'] 
    da = atm_clirad_singlerun - atm_crd
    da = fmt(da)
    p_atm = plot.hist_band_vs_flux(da, 
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
    
    ds_crd = lbldata.crd_data_atm(lbldata.lblnew_params_atm(atmpro=atmpro))['flux']
    olr_crd = ds_crd['flug'].isel(pressure=0)
    sfc_crd = ds_crd['fldg'].isel(pressure=-1)
    atm_crd = (ds_crd.isel(pressure=0)
               - ds_crd.isel(pressure=-1))['fnetg']
    
    ds_clirad = cliraddata.clirad_data_atm(
        cliraddata.clirad_params_atm(atmpro=atmpro))['flux']
    olr_clirad = ds_clirad['flug'].isel(pressure=0)
    sfc_clirad = ds_clirad['fldg'].isel(pressure=-1)
    atm_clirad = (ds_clirad.isel(pressure=0)
                  - ds_clirad.isel(pressure=-1))['fnetg']

    ds_clirad_singlerun = cliraddata.clirad_data_atm(
        clirad_params_atm_singlerun(atmpro=atmpro))['flux']
    olr_clirad_singlerun = ds_clirad_singlerun['flug'].isel(pressure=0)
    sfc_clirad_singlerun = ds_clirad_singlerun['fldg'].isel(pressure=-1)
    atm_clirad_singlerun = (ds_clirad_singlerun.isel(pressure=0)
                  - ds_clirad_singlerun.isel(pressure=-1))['fnetg']
    
    
    df = pd.DataFrame()
    df.index.name = 'Sum over bands'
    
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



def show_makeup():
    '''
    Display table showing the concentrations
    of the gases in each spectral band
    '''
    df = pd.DataFrame()

    for band, molecule in nongreys_byband().items():
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
    
    for band, molecule in greys_byband().items():
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

