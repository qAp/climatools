import os
import itertools

import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt

from ..html.html import *

from IPython import display



def print_diff_benchmark(dict_df, benchmark='crd'):
    othermodels = [model for model in dict_df.keys()]
    othermodels.remove(benchmark)

    df_bench = dict_df[benchmark]

    print()
    print(benchmark.upper())
    display.display(df_bench)

    for model in othermodels:
        print()
        print(model.upper())
        display.display(dict_df[model])


    for model in othermodels:
        df_model = dict_df[model]

        print()
        print('{} - {}'.format(model.upper(), benchmark.upper()))
        if not all(df_model.index == df_bench.index):
            print('Model indices not identical to benchmark indices, '
                  "forcing model indices to be the same as benchmark's")
            df_model.index = df_bench.index
        display.display(df_model - df_bench)
        

def load_dataset_crd(vartype, rundir):
    if vartype == 'flux':
        fname = 'output_fluxg.dat'
        vdim = 'level'
    elif vartype == 'cooling rate':
        fname = 'output_coolrg.dat'
        vdim = 'layer'

    fpath = os.path.join(rundir, fname)
    
    df = pd.read_csv(fpath, sep=r'\s+')
    df = df.set_index(['pressure', 'g'])
    ds = xr.Dataset.from_dataframe(df)
    ds.coords[vdim] = ('pressure', ds[vdim].isel(g=0))
    return ds



def load_dataset_clirad(vartype, rundir):
    if vartype == 'flux':
        fname = 'output_fluxg.dat'
        vdim = 'level'
    elif vartype == 'cooling rate':
        fname = 'output_coolrg.dat'
        vdim = 'layer'

    fpath = os.path.join(rundir, fname)

    df = pd.read_csv(fpath, sep=r'\s+')
    df = df.set_index(['pressure', 'band', 'g'])
    ds = xr.Dataset.from_dataframe(df)
    ds.coords[vdim] = ('pressure', ds[vdim].isel(g=0, band=0))
    ds = ds.sel(band=7)
    del ds.coords['band']
    return ds



class Model(object):
    def __init__(self, **kwargs):
        self.rundir = kwargs.pop('rundir', None)
        self.type_model = kwargs.pop('type_model', None)
        self.linestyle = '-'
        self.data = {}

    def load_data(self):
        if not (self.rundir and self.type_model):
            raise ValueError("Cannot load data"
                             " because no directory and model type info")
        
        if self.type_model == 'crd':
            self.data['flux'] = load_dataset_crd(vartype='flux',
                                                 rundir=self.rundir)
            self.data['cooling rate'] = load_dataset_crd(
                vartype='cooling rate',
                rundir=self.rundir)
        elif self.type_model == 'clirad':
            self.data['flux'] = load_dataset_clirad(
                vartype='flux', rundir=self.rundir)
            self.data['cooling rate'] = load_dataset_clirad(
                vartype='cooling rate', rundir=self.rundir)



class Fig_FluxCoolr(object):
    def __init__(self):
        self.ggroups = [1, 2, 3, 4]
        vartypes = ['flux', 'cooling rate']
        yscales = ['linear', 'log']
        self.names_ax = list(itertools.product(vartypes, yscales))
        self.hreftext = 'Figure: flux, cooling rate. g-group {g}'
        self.vartypes = vartypes
        self.yscales = yscales
        
        self.vars_plot = {vartype: None for vartype in vartypes}
        self.colors = {varname: None
                       for varname in ['flug', 'fnetg', 'coolrg']}
        self.varlims_from_indexrange = {yscale: None for yscale in yscales}

    def display_hrefanchor(self):
        for g in self.ggroups:
            s = self.hreftext.format(g=g)
            html = getHTML_hrefanchor(s)
            display.display(display.HTML(html))

    def plot(self, analysis):
        for g in self.ggroups:
            
            s = self.hreftext.format(g=g)
            html = getHTML_idanchor(s=s)
            markdown = getMarkdown_sectitle(s=s)
            display.display(display.HTML(html))
            display.display(display.Markdown(markdown))
            
            fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(15, 11))
            axs = axs.flatten()

            for ax, (vartype, yscale) in zip(axs, self.names_ax):
                for varname in self.vars_plot[vartype]:
                    for modelname, model in analysis.models.items():
                        model.data[vartype][varname]\
                             .sel(g=g)\
                             .climaviz\
                             .plot(ax=ax,
                                   linewidth=2, grid=True,
                                   label=modelname.upper() + ' ' + varname,
                                   color=self.colors[varname],
                                   linestyle=model.linestyle,
                                   index_on_yaxis=True,
                                   yincrease=False, yscale=yscale,
                                   varlim_from_indexrange=self.varlims_from_indexrange[yscale])
                ax.set_xlabel(vartype)
                        
            plt.tight_layout()
            display.display(plt.gcf())
            plt.close()        



class Analysis(object):
    def __init__(self):
        self.models = {}
        self.figs = {}

    def model(self, name, **kwargs):
        if name not in self.models:
            self.models[name] = Model(**kwargs)
        return self.models[name]
        
    def fig_fluxcoolr(self, name, **kwargs):
        if name not in self.figs:
            self.figs[name] = Fig_FluxCoolr(**kwargs)
        return self.figs[name]


        


