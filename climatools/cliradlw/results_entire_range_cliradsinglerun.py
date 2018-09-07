
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
import climatools.lblnew.dataset as lbldata
import climatools.cliradlw.setup as setup_cliradlw
import climatools.cliradlw.pipeline as pipe_cliradlw
from climatools.cliradlw import runrecord
import climatools.cliradlw.dataset as cliraddata
from climatools.atm.absorbers import nongreys_byband
from climatools.atm.absorbers import greys_byband

import climatools.html.html as climahtml
from climatools.lblnew.dataio import *
from climatools.plot.plot import *


from IPython import display

importlib.reload(bestfits)
importlib.reload(setup_bestfit)
importlib.reload(setup_overlap)
importlib.reload(pipe_lblnew)
importlib.reload(lbldata)
importlib.reload(setup_cliradlw)
importlib.reload(pipe_cliradlw)
importlib.reload(runrecord)
importlib.reload(cliraddata)





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


    
def plt_vert_profile_bokeh(pltdata=None, 
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
    p_cool_liny = plt_vert_profile_bokeh(pltdata=data_cool)
    p_cool_logy = plt_vert_profile_bokeh(pltdata=data_cool, 
                                 y_axis_type='log',
                                 prange=(.01, 200))
    
    data_cooldiff = pltdata_cooldiff(atmpro=atmpro)
    p_cooldiff_logy = plt_vert_profile_bokeh(pltdata=data_cooldiff,
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

    ds_crd = lbldata.crd_data_atm(lbldata.lblnew_params_atm(atmpro=atmpro))['flux']
    ds_clirad = cliraddata.clirad_data_atm(
        cliraddata.clirad_params_atm(atmpro=atmpro))['flux']
    ds_clirad_singlerun = cliraddata.clirad_data_atm(
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

