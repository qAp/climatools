import os
import itertools

import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ..plot.plot import *
from ..html.html import *

from IPython import display




def load_dataset_crd(vartype, rundir,
                     fpath_flux=None, fpath_coolr=None):
    if vartype == 'flux':
        if fpath_flux == None:
            fname = 'output_fluxg.dat'
        else:
            fname = fpath_flux
        vdim = 'level'
    elif vartype == 'cooling rate':
        if fpath_coolr == None:
            fname = 'output_coolrg.dat'
        else:
            fname = fpath_coolr
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
        self.fpath_flux = None
        self.fpath_coolr = None

    def load_data(self):
        if not (self.rundir and self.type_model):
            raise ValueError("Cannot load data"
                             " because no directory and model type info")
        
        if self.type_model == 'crd':
            
            self.data['flux'] = load_dataset_crd(vartype='flux',
                                                 rundir=self.rundir,
                                                 fpath_flux=self.fpath_flux)
            self.data['cooling rate'] = load_dataset_crd(
                vartype='cooling rate',
                rundir=self.rundir,
                fpath_coolr=self.fpath_coolr)
        elif self.type_model == 'clirad':
            self.data['flux'] = load_dataset_clirad(
                vartype='flux', rundir=self.rundir)
            self.data['cooling rate'] = load_dataset_clirad(
                vartype='cooling rate', rundir=self.rundir)

        df_dgdgs = pd.read_csv(os.path.join(self.rundir, 'dgdgs.dat'),
                               sep=r'\s+')
        df_dgdgs = df_dgdgs.set_index(['g'])
        self.data['dgdgs'] = xr.Dataset.from_dataframe(df_dgdgs)



class Fig_FluxCoolr(object):
    def __init__(self, ggroups=None, vartypes=None):
        yscales = ['linear', 'log']
        
        if ggroups is None:
            self.ggroups = [1, 2, 3, 4]
        else:
            self.ggroups = ggroups
            
        if vartypes is None:
            self.vartypes = ['flux', 'cooling rate']
        else:
            self.vartypes = vartypes
            
        self.names_ax = list(itertools.product(self.vartypes, yscales))
        self.hreftext = ('Figure: ' +
                         ', '.join(vartype for vartype in self.vartypes)
                         + ' g-group {g}')
        self.yscales = yscales
        
        self.vars_plot = {vartype: None for vartype in self.vartypes}
        self.colors = {varname: None
                       for varname in ['flug', 'fnetg', 'coolrg']}
        self.varlims_from_indexrange = {yscale: None for yscale in yscales}

    def display_hrefanchor(self):
        for g in self.ggroups + ['total']:
            s = self.hreftext.format(g=g)
            html = getHTML_hrefanchor(s)
            display.display(display.HTML(html))

    def set_pressure_displayrange(self, low=None, high=None):
        '''
        If set, would set the eventual limits of the axis 
        on which the index values are plotted. (The y-axis).
        '''
        self.pressure_display_low = low
        self.pressure_display_high = high
        

    def plot(self, analysis):
        
        for g in self.ggroups + ['total']:
            
            s = self.hreftext.format(g=g)
            html = getHTML_idanchor(s=s)
            markdown = getMarkdown_sectitle(s=s)
            display.display(display.HTML(html))
            display.display(display.Markdown(markdown))
            
            fig, axs = plt.subplots(nrows=len(self.vartypes), ncols=2,
                                    figsize=(15, 5 * len(self.vartypes) + 1))
            axs = axs.flatten()

            for ax, (vartype, yscale) in zip(axs, self.names_ax):
                for varname in self.vars_plot[vartype]:
                    for modelname, model in analysis.models.items():
                        if g == 'total':
                            da = model.data[vartype][varname].sum('g')
                        else:
                            da = model.data[vartype][varname].sel(g=g)
                        da.climaviz\
                          .plot(ax=ax,
                                linewidth=2, grid=True,
                                label=modelname.upper() + ' ' + varname,
                                color=self.colors[varname],
                                linestyle=model.linestyle,
                                index_on_yaxis=True,
                                yincrease=False, yscale=yscale,
                                varlim_from_indexrange=self.varlims_from_indexrange[yscale])

                if getattr(self, 'pressure_display_low', None):
                    ax.set_ylim(top=self.pressure_display_low)

                if getattr(self, 'pressure_display_high', None):
                    ax.set_ylim(bottom=self.pressure_display_high)
                    
                if vartype == 'flux':
                    ax.set_xlabel(vartype + ' ($W m^{-2}$)')
                elif vartype == 'cooling rate':
                    ax.set_xlabel(vartype + ' ($deg/day$)')

                ax.set_ylabel(ax.get_ylabel() + ' ($hPa$)')
                        
            plt.tight_layout()
            display.display(plt.gcf())
            plt.close()        



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

        


class Table(object):
    def __init__(self):
        self.vartype = None
        self.sumg = False
        self.at_pressures = None
        self.hreftext = 'Table: {vartype}. g-groups {sumg}'

    def display_hrefanchor(self):
        s = self.hreftext.format(vartype=self.vartype,
                                 sumg='' if self.sumg == False else 'total')
        html = getHTML_hrefanchor(s=s)
        display.display(display.HTML(html))


    def display_dgdgs(self, model):
        if self.sumg == True:
            ds = model.data['dgdgs'].sum('g')
        else:
            ds = model.data['dgdgs']
        
        s = self.hreftext.format(vartype=self.vartype,
                                 sumg='' if self.sumg == False else 'total')
        html = getHTML_idanchor(s=s)
        markdown = getMarkdown_sectitle(s=s)
        display.display(display.HTML(html))
        display.display(display.Markdown(markdown))
        
        display.display(ds.to_dataframe())

        
    def display_withdiff(self, analysis, benchmark=None):
        if self.vartype == 'flux':
            self.vdim = 'level'
        elif self.vartype == 'cooling rate':
            self.vdim = 'layer'
        else:
            raise ValueError("`vartype` must be either "
                             "'flux' or 'cooling rate'")
        
        if list(self.at_pressures) == None:
            dict_ds = {name: model.data[self.vartype]
                       for name, model in analysis.models.items()}
        else:
            dict_ds = {name: model.data[self.vartype]\
                       .sel(pressure=self.at_pressures, method='nearest')
                       for name, model in analysis.models.items()}

        if self.sumg:
            dict_ds = {name: ds.sum('g') for name, ds in dict_ds.items()}

        dict_df = {name: ds.to_dataframe() for name, ds in dict_ds.items()}
        dict_df = {name: df.set_index([self.vdim], append=True)
                   for name, df in dict_df.items()}

        s = self.hreftext.format(vartype=self.vartype,
                                 sumg='' if self.sumg == False else 'total')
        html = getHTML_idanchor(s=s)
        markdown = getMarkdown_sectitle(s=s)
        display.display(display.HTML(html))
        display.display(display.Markdown(markdown))

        print_diff_benchmark(dict_df, benchmark=benchmark)


    




class Analysis(object):
    def __init__(self):
        self.models = {}
        self.figs = {}
        self.tables = {}

    def model(self, name, **kwargs):
        if name not in self.models:
            self.models[name] = Model(**kwargs)
        return self.models[name]

    def fig_fluxcoolr(self, name, **kwargs):
        if name not in self.figs:
            self.figs[name] = Fig_FluxCoolr(**kwargs)
        return self.figs[name]

    def table(self, name):
        if name not in self.tables:
            self.tables[name] = Table()
        return self.tables[name]

        


