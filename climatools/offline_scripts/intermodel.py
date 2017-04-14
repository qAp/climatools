import os
import io
import itertools
import collections

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from IPython import display

import rtmtools.lblrtm.aerutils as aerutils
import rtmtools.lblrtm.aeranalyse as aeranalyse
import rtmtools.lblrtm.visualisation as viz

import rtmtools.clirad.sw.wrangle as cliradwrangle
import rtmtools.clirad.sw.analyse as cliradanalyse
import climatools.clirad.info as cliradinfo

import rtmtools.rrtmg.lw.wrangle as rrtmgwrangle
import climatools.rrtmg.info as rrtmginfo









def lw_results_all_wavenumbers(infos_wavenumber=None,
                               infos_spectralband=None,
                               name_molecule='name of molecule'):
    '''
    Script to summarise and display *longwave* results
    from different radiation models, for the whole of
    the spectral range over which the results have been
    calculated.

    Parameters
    ----------
    infos_wavenumber: list of tuples, with each tuple
                      representing a set of radiation results in which 
                      the spectral dimension is specified in wavenumbers
                      (line-by-line models, or RRTMG).
                      Each tuple specifies the name for the results set,
                      the colour and the linestyle used to plot it,
                      and a pandas.Panel containing its data.
                      For example, `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    infos_spectralband: list of tuples, with each tuple representing a set
                        of radiation results in which the spectral dimension
                        is specified in spectral band numbers. i.e. CLIRAD
                        Each tuple specifies the name for the results set,
                        the colour and the linestyle used to plot it,
                        and a pandas.Panel containing its data.
                        For example, `(\'CLIRAD\', \'b\', \'--\', pnl_clirad)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''
    # align the spectral dimensions
    if infos_wavenumber:
        (names_wavenumber,
         colours_wavenumber,
         linestyles_wavenumber,
         pnls_wavenumber) = map(list, zip(*infos_wavenumber))
        
        dfs_wavenumber = [aeranalyse\
                          .sum_OUTPUT_RADSUM_over_wbands(pnl,
                                                         V1=0, V2=3000)
                          for pnl in pnls_wavenumber]
    else:
        (names_wavenumber,
         colours_wavenumber,
         linestyles_wavenumber,
         dfs_wavenumber) = [], [] , [], []
        
    if infos_spectralband:
        (names_spectralband,
         colours_spectralband,
         linestyles_spectralband,
         pnls_spectralband) = map(list, zip(*infos_spectralband))
        
        dfs_spectralband = [cliradanalyse\
                            .sum_OUTPUT_CLIRAD_over_wbands(pnl,
                                                           wbands=range(1, 11))
                            for pnl in pnls_spectralband]
    else:
        (names_spectralband,
         colours_spectralband,
         linestyles_spectralband,
         dfs_spectralband) = [], [], [], []
        
    # sort into data and display properties
    dfs = dfs_wavenumber + dfs_spectralband
    names = names_wavenumber + names_spectralband
    colours = colours_wavenumber + colours_spectralband
    linestyles = linestyles_wavenumber + linestyles_spectralband
    
    # make summary table for differences fluxes and heating rate
    atm_levels = [70, 30, 0]
    dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
    df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                       names=names,
                                       return_original=True)
    
    # write summary table to excel file
    name_excelfile = 'longwave_mls_{}_total.xlsx'.format(name_molecule)
    with pd.ExcelWriter(name_excelfile) as writer:
        df_diffs.to_excel(writer, sheet_name='total')
        
    # display summary table in notebook
    for name_diff in df_diffs.index.levels[0]:
        df_print = df_diffs.loc[(name_diff, slice(None)), :]
        df_print.index = df_print.index.droplevel(0)
        print(name_diff)
        print(df_print)
        print()
        
    viz.plot_pres_vs_hrcr(dfs=dfs,
                          names=names,
                          linestyles=linestyles,
                          colours=colours,
                          title=('Total cooling rate. {}'\
                                 .format(name_molecule)),
                          cooling_rate=True,
                          xlim_linear=None,
                          xlim_log=None)

    
    display.display(plt.gcf()); plt.close()


def sw_results_all_wavenumbers(infos_wavenumber=None,
                               infos_spectralband=None,
                               name_molecule='name of molecule'):
    '''
    Script to summarise and display *shortwave* results
    from different radiation models, for the whole of
    the spectral range over which the results have been
    calculated.

    Parameters
    ----------
    infos_wavenumber: list of tuples, with each tuple
                      representing a set of radiation results in which 
                      the spectral dimension is specified in wavenumbers
                      (line-by-line models, or RRTMG).
                      Each tuple specifies the name for the results set,
                      the colour and the linestyle used to plot it,
                      and a pandas.Panel containing its data.
                      For example, `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    infos_spectralband: list of tuples, with each tuple representing a set
                        of radiation results in which the spectral dimension
                        is specified in spectral band numbers. i.e. CLIRAD
                        Each tuple specifies the name for the results set,
                        the colour and the linestyle used to plot it,
                        and a pandas.Panel containing its data.
                        For example, `(\'CLIRAD\', \'b\', \'--\', pnl_clirad)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''
    # align the spectral dimensions
    if infos_wavenumber:
        (names_wavenumber,
         colours_wavenumber,
         linestyles_wavenumber,
         pnls_wavenumber) = map(list, zip(*infos_wavenumber))
        
        dfs_wavenumber = [aeranalyse\
                          .sum_OUTPUT_RADSUM_over_wbands(pnl,
                                                         V1=1000,
                                                         V2=25000)
                          for pnl in pnls_wavenumber]
    else:
        (names_wavenumber,
         colours_wavenumber,
         linestyles_wavenumber,
         dfs_wavenumber) = [], [] , [], []
        
    if infos_spectralband:
        (names_spectralband,
         colours_spectralband,
         linestyles_spectralband,
         pnls_spectralband) = map(list, zip(*infos_spectralband))
        
        dfs_spectralband = [cliradanalyse\
                            .sum_OUTPUT_CLIRAD_over_wbands(pnl,
                                                           wbands=range(1, 11))
                            for pnl in pnls_spectralband]
    else:
        (names_spectralband,
         colours_spectralband,
         linestyles_spectralband,
         dfs_spectralband) = [], [], [], []
        
    # sort into data and display properties
    dfs = dfs_wavenumber + dfs_spectralband
    dfs = [df[['pressure',
               'flux_up', 'flux_down', 'net_flux',
               'heating_rate']]
           for df in dfs]
    names = names_wavenumber + names_spectralband
    colours = colours_wavenumber + colours_spectralband
    linestyles = linestyles_wavenumber + linestyles_spectralband
    
    # make summary table for differences fluxes and heating rate
    atm_levels = [70, 30, 0]
    dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
    df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                       names=names,
                                       return_original=True)
    
    # write summary table to excel file
    name_excelfile = 'shortwave_mls_{}_total.xlsx'.format(name_molecule)
    with pd.ExcelWriter(name_excelfile) as writer:
        df_diffs.to_excel(writer, sheet_name='total')
        
    # display summary table in notebook
    for name_diff in df_diffs.index.levels[0]:
        df_print = df_diffs.loc[(name_diff, slice(None)), :]
        df_print.index = df_print.index.droplevel(0)
        print(name_diff)
        print(df_print)
        print()
        
    viz.plot_pres_vs_hrcr(dfs=dfs,
                          names=names,
                          linestyles=linestyles,
                          colours=colours,
                          title=('Total heating rate. {}'\
                                 .format(name_molecule)),
                          cooling_rate=False,
                          xlim_linear=None,
                          xlim_log=None)
    
    display.display(plt.gcf()); plt.close()


def lw_results_by_rrtmg_bands(infos_rrtmg=None,
                              infos_lbl=None,
                              name_molecule='name of molecule'):
    '''
    Script to summarise and display *longwave* results
    from different radiation models, for spectral bands in RRTMG.

    Parameters
    ----------
    infos_rrtmg: list of tuples, with each tuple representing a set
                 of RRTMG-LW results.  Each tuple specifies the name
                 for the results set, the colour and the linestyle used
                 to plot it, and a pandas.Panel containing its data.
                 e.g. `(\'RRTMG\', \'g\', \'--\', pnl_rrtmg)`.
    infos_lbl: list of tuple, with each tuple representing a set of
               line-by-line results.  Each tuple specifies the name
               for the results set, the colour and the linestyle used
               to plot it, and a pandas.Panel containing its data.
               e.g. `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''
    wbands = list(itertools.chain.from_iterable(
        rrtmginfo.wavenumber_bands(region='lw').values()))
    
    # align spectral dimensions
    if infos_lbl:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = map(list, zip(*infos_lbl))
        
        pnls_lbl = [aeranalyse
                    .lines2bands(pnl_lbl, wbands=wbands)
                    for pnl_lbl in pnls_lbl]
    else:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = ([], [], [], [])
        
    if infos_rrtmg:
        (names_rrtmg,
         colours_rrtmg,
         linestyles_rrtmg,
         pnls_rrtmg) = map(list, zip(*infos_rrtmg))
    else:
        (names_rrtmg,
         colours_rrtmg,
         linestyles_rrtmg,
         pnls_rrtmg) = ([], [], [], [])
        
    # sort into data panels and display properties
    names = names_rrtmg + names_lbl
    colours = colours_rrtmg + colours_lbl
    linestyles = linestyles_rrtmg + linestyles_lbl
    pnls = pnls_rrtmg + pnls_lbl
    
    # Make summary table for differences fluxes and heating rate
    # at these atmosphere levels
    atm_levels = [70, 30, 0]
    
    # Open excel file to write the summary tables into
    name_excelfile = ('longwave_mls_{}_by_rrtmg_bands.xlsx'\
                      .format(name_molecule))
    with pd.ExcelWriter(name_excelfile) as writer:
        
        for i, (v1, v2) in enumerate(wbands):
            band = i + 1
            bandrange = '{} ~ {} cm-1'.format(v1, v2)
            dfs = [pnl[(v1, v2)] for pnl in pnls]
            
            # Make summary table for differences fluxes and heating rate
            dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
            df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                               names=names,
                                               return_original=True)
                        
            # display summary table in notebook
            print('RRTMG-LW. '
                  'Spectral band {}. '.format(band)
                  + bandrange
                  + '\n')
            for name_diff in df_diffs.index.levels[0]:
                df_print = df_diffs.loc[(name_diff, slice(None)), :]
                df_print.index = df_print.index.droplevel(0)
                print(name_diff)
                print(df_print)
                print()

            # write summary table to excel file
            df_diffs.columns = pd.MultiIndex.from_product((bandrange,
                                                           df_diffs.columns))
            df_diffs.to_excel(writer, sheet_name='{}'.format(band))
                
            # plot heating/cooling rate
            viz.plot_pres_vs_hrcr(dfs=dfs,
                                  names=names,
                                  linestyles=linestyles,
                                  colours=colours,
                                  title=('Cooling rate. '
                                         '{}. '
                                         'Band {}. '
                                         '{} ~ {} cm-1')\
                                         .format(name_molecule,
                                                 band,
                                                 v1, v2),
                                  cooling_rate=True,
                                  xlim_linear=None,
                                  xlim_log=None)
            
            display.display(plt.gcf()); plt.close()
            print()
            print('------------------------------------'
                  '------------------------------------')
            print()


def sw_results_by_rrtmg_bands(infos_rrtmg=None,
                              infos_lbl=None,
                              name_molecule='name of molecule'):
    '''
    Script to summarise and display *shortwave* results
    from different radiation models, for spectral bands in RRTMG.

    Parameters
    ----------
    infos_rrtmg: list of tuples, with each tuple representing a set
                 of RRTMG-LW results.  Each tuple specifies the name
                 for the results set, the colour and the linestyle used
                 to plot it, and a pandas.Panel containing its data.
                 e.g. `(\'RRTMG\', \'g\', \'--\', pnl_rrtmg)`.
    infos_lbl: list of tuple, with each tuple representing a set of
               line-by-line results.  Each tuple specifies the name
               for the results set, the colour and the linestyle used
               to plot it, and a pandas.Panel containing its data.
               e.g. `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''
    wbands = list(itertools.chain.from_iterable(
        rrtmginfo.wavenumber_bands(region='sw').values()))
    
    # align spectral dimensions
    if infos_lbl:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = map(list, zip(*infos_lbl))
        
        pnls_lbl = [aeranalyse
                    .lines2bands(pnl_lbl, wbands=wbands)
                    for pnl_lbl in pnls_lbl]
    else:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = ([], [], [], [])
        
    if infos_rrtmg:
        (names_rrtmg,
         colours_rrtmg,
         linestyles_rrtmg,
         pnls_rrtmg) = map(list, zip(*infos_rrtmg))
        
        if pnls_lbl:
            [aeranalyse.normalise_by_TOA_flux_down(pnl,
                                                   normalise_to=pnls_lbl[0])
             for pnl in pnls_rrtmg]
    else:
        (names_rrtmg,
         colours_rrtmg,
         linestyles_rrtmg,
         pnls_rrtmg) = ([], [], [], [])
        
    # sort into data panels and display properties
    names = names_rrtmg + names_lbl
    colours = colours_rrtmg + colours_lbl
    linestyles = linestyles_rrtmg + linestyles_lbl
    pnls = pnls_rrtmg + pnls_lbl
    pnls = [pnl.loc[:, :, ['pressure',
                           'flux_up', 'flux_down', 'net_flux',
                           'heating_rate']]
            for pnl in pnls]
    
    # Make summary table for differences fluxes and heating rate
    # at these atmosphere levels
    atm_levels = [70, 30, 0]
    
    # Open excel file to write the summary tables into
    name_excelfile = ('shortwave_mls_{}_by_rrtmg_bands.xlsx'\
                      .format(name_molecule))
    with pd.ExcelWriter(name_excelfile) as writer:
        
        for i, (v1, v2) in enumerate(wbands):
            band = i + 1
            bandrange = ('{} ~ {} cm-1'
                         .format(v1, v2))
            dfs = [pnl[(v1, v2)] for pnl in pnls]
            
            # Make summary table for differences fluxes and heating rate
            dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
            df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                               names=names,
                                               return_original=True)
            
            # display summary table in notebook
            print('RRTMG-SW spectral band. '
                  + 'Band {}. '.format(band)
                  + '{}.'.format(bandrange)
                  + '\n')
            for name_diff in df_diffs.index.levels[0]:
                df_print = df_diffs.loc[(name_diff, slice(None)), :]
                df_print.index = df_print.index.droplevel(0)
                print(name_diff)
                print(df_print)
                print()

            # write summary table to excel file
            df_diffs.columns = pd.MultiIndex.from_product((bandrange,
                                                           df_diffs.columns))
            df_diffs.to_excel(writer, sheet_name='{}'.format(band))
                
            # plot heating/cooling rate
            viz.plot_pres_vs_hrcr(dfs=dfs,
                                  names=names,
                                  linestyles=linestyles,
                                  colours=colours,
                                  title=('Heating rate. '
                                         '{}. '
                                         'Band {}. '
                                         '{}.')\
                                         .format(name_molecule,
                                                 band,
                                                 bandrange),
                                  cooling_rate=False,
                                  xlim_linear=None,
                                  xlim_log=None)
            
            display.display(plt.gcf()); plt.close()
            print()
            print('------------------------------------'
                  '------------------------------------')
            print()


def lw_results_by_cliard_bands(infos_clirad=None,
                               infos_lbl=None,
                               name_molecule='name of molecule'):
    '''
    Script to summarise and display *longwave* results from different
    radiation models, for spectral bands in CLIRAD-LW.

    Parameters
    ----------
    infos_clirad: list of tuples, with each tuple representing a set
                 of CLIRAD results.  Each tuple specifies the name
                 for the results set, the colour and the linestyle used
                 to plot it, and a pandas.Panel containing its data.
                 e.g. `(\'CLIRAD\', \'b\', \'--\', pnl_clirad)`.
    infos_lbl: list of tuple, with each tuple representing a set of
               line-by-line results.  Each tuple specifies the name
               for the results set, the colour and the linestyle used
               to plot it, and a pandas.Panel containing its data.
               e.g. `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''    
    wbands = cliradinfo.wavenumber_bands(region='lw')
    
    # align spectral dimensions
    if infos_lbl:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = map(list, zip(*infos_lbl))
        
        pnls_lbl = [cliradanalyse.lines2bands(pnl_lbl, wbands=wbands)
                    for pnl_lbl in pnls_lbl]
    else:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = ([], [], [], [])
        
    if infos_clirad:
        (names_clirad,
         colours_clirad,
         linestyles_clirad,
         pnls_clirad) = map(list, zip(*infos_clirad))
    else:
        (names_clirad,
         colours_clirad,
         linestyles_clirad,
         pnls_clirad) = ([], [], [], [])
        
    # sort into data panels and display properties
    names = names_clirad + names_lbl
    colours = colours_clirad + colours_lbl
    linestyles = linestyles_clirad + linestyles_lbl
    pnls = pnls_clirad + pnls_lbl
    
    # Make summary table for differences fluxes and heating rate
    # at these atmosphere levels
    atm_levels = [70, 30, 0]
    
    # Open excel file to write the summary tables into
    name_excelfile = ('longwave_mls_{}_by_clirad_bands.xlsx'\
                      .format(name_molecule))
    with pd.ExcelWriter(name_excelfile) as writer:
        
        for band in wbands.keys():
            bandrange = ' '.join(['{} ~ {}'.format(v1, v2)
                                  for v1, v2 in wbands[band]]) + ' cm-1'
            

            
            dfs = [pnl[band] for pnl in pnls]
            
            # Make summary table for differences fluxes and heating rate
            dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
            df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                               names=names,
                                               return_original=True)

            # display summary table in notebook
            print('CLIRAD-LW '
                  + 'Spectral band {}. '.format(band)
                  + bandrange
                  + '\n')
            for name_diff in df_diffs.index.levels[0]:
                df_print = df_diffs.loc[(name_diff, slice(None)), :]
                df_print.index = df_print.index.droplevel(0)
                print(name_diff)
                print(df_print)
                print()

            # write summary table to excel file
            df_diffs.columns = pd.MultiIndex.from_product((bandrange,
                                                           df_diffs.columns))
            df_diffs.to_excel(writer, sheet_name='{}'.format(band))
            
            # plot heating/cooling rate
            viz.plot_pres_vs_hrcr(dfs=dfs,
                                  names=names,
                                  linestyles=linestyles,
                                  colours=colours,
                                  title=('Cooling rate. '
                                         '{}. '
                                         'Band {}. '
                                         '{}')\
                                         .format(name_molecule,
                                                 band,
                                                 bandrange),
                                  cooling_rate=True,
                                  xlim_linear=None,
                                  xlim_log=None)
            
            display.display(plt.gcf()); plt.close()
            print()
            print('------------------------------------'
                  '------------------------------------')
            print()


def sw_results_by_clirad_bands(infos_clirad=None,
                               infos_lbl=None,
                               name_molecule='name of molecule'):
    '''
    Script to summarise and display *shortwave* results from different
    radiation models, for spectral bands in CLIRAD-SW.

    Parameters
    ----------
    infos_clirad: list of tuples, with each tuple representing a set
                 of CLIRAD results.  Each tuple specifies the name
                 for the results set, the colour and the linestyle used
                 to plot it, and a pandas.Panel containing its data.
                 e.g. `(\'CLIRAD\', \'b\', \'--\', pnl_clirad)`.
    infos_lbl: list of tuple, with each tuple representing a set of
               line-by-line results.  Each tuple specifies the name
               for the results set, the colour and the linestyle used
               to plot it, and a pandas.Panel containing its data.
               e.g. `(\'CRD\', \'b\', \'-\', pnl_crd)`.
    name_molecule: \'H2O\', \'CO2\', etc.
    '''    
    wbands = cliradinfo.wavenumber_bands(region='sw')
    
    # align spectral dimensions
    if infos_lbl:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = map(list, zip(*infos_lbl))
        
        pnls_lbl = [cliradanalyse.lines2bands(pnl_lbl, wbands=wbands)
                    for pnl_lbl in pnls_lbl]
    else:
        (names_lbl,
         colours_lbl,
         linestyles_lbl,
         pnls_lbl) = ([], [], [], [])
        
    if infos_clirad:
        (names_clirad,
         colours_clirad,
         linestyles_clirad,
         pnls_clirad) = map(list, zip(*infos_clirad))

        if pnls_lbl:
            [aeranalyse.normalise_by_TOA_flux_down(pnl,
                                                   normalise_to=pnls_lbl[0])
             for pnl in pnls_clirad]
    else:
        (names_clirad,
         colours_clirad,
         linestyles_clirad,
         pnls_clirad) = ([], [], [], [])
        
    # sort into data panels and display properties
    names = names_clirad + names_lbl
    colours = colours_clirad + colours_lbl
    linestyles = linestyles_clirad + linestyles_lbl
    pnls = pnls_clirad + pnls_lbl
    pnls = [pnl.loc[:, :, ['pressure',
                           'flux_up', 'flux_down', 'net_flux',
                           'heating_rate']]
            for pnl in pnls]
    
    # Make summary table for differences fluxes and heating rate
    # at these atmosphere levels
    atm_levels = [70, 30, 0]
    
    # Open excel file to write the summary tables into
    name_excelfile = ('shortwave_mls_{}_by_clirad_bands.xlsx'\
                      .format(name_molecule))
    with pd.ExcelWriter(name_excelfile) as writer:
        
        for band in wbands.keys():
            bandrange = ' '.join(['{} ~ {}'.format(v1, v2)
                                  for v1, v2 in wbands[band]]) + ' cm-1'
            
            dfs = [pnl[band] for pnl in pnls]
            
            # Make summary table for differences fluxes and heating rate
            dfs_atm_levels = [df.loc[atm_levels, :] for df in dfs]
            df_diffs = viz.tabulate_difference(dfs=dfs_atm_levels,
                                               names=names,
                                               return_original=True)
            
            # display summary table in notebook
            print('CLIRAD-SW spectral. '
                  + 'Band {}. '.format(band)
                  + bandrange
                  + '\n')
            for name_diff in df_diffs.index.levels[0]:
                df_print = df_diffs.loc[(name_diff, slice(None)), :]
                df_print.index = df_print.index.droplevel(0)
                print(name_diff)
                print(df_print)
                print()

            # write summary table to excel file
            df_diffs.columns = pd.MultiIndex.from_product((bandrange,
                                                           df_diffs.columns))
            df_diffs.to_excel(writer, sheet_name='{}'.format(band))
                
            # plot heating/cooling rate
            viz.plot_pres_vs_hrcr(dfs=dfs,
                                  names=names,
                                  linestyles=linestyles,
                                  colours=colours,
                                  title=('Heating rate. '
                                         '{}. '
                                         'Band {}. '
                                         '{}.')\
                                  .format(name_molecule,
                                          band,
                                          bandrange),
                                  cooling_rate=False,
                                  xlim_linear=None,
                                  xlim_log=None)
            
            display.display(plt.gcf()); plt.close()
            print()
            print('------------------------------------'
                  '------------------------------------')
            print()
