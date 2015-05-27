import sys
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

import climatools.muths as muths
import climatools.dates as dates




def symmetric_about_white_cmap_levels(rough_maxabs, Ncolours = 11):
    '''
    Returns min and max levels and step that will have 0 centred
    on the colour white on a diverging colourmap that diverges from
    the colour white
    INPUT:
    rough_maxabs -- rough maximum absolute value of the levels
                    (note the absolute value because max = -min
                    necessarily)
    Ncolours -- number of intervals on the colour bar
    '''
    try:
        assert Ncolours % 2 != 0
    except AssertionError:
        raise InputError('Number of colours needs to be an odd number.')

    int_dv = muths.round_to_1(2 * rough_maxabs / Ncolours)
    rough_dv = 2 * rough_maxabs / Ncolours
    ddv = int_dv - rough_dv
    maxabs = rough_maxabs + Ncolours / 2 * ddv
    return (- maxabs, maxabs, int_dv)



def axes_beyond_ticks(ax, which = 'x'):
    '''
    Draws the axes with a range that is just wider than
    the existing range so that tick labels at the
    lowest and highest values do not overlap with neighbouring
    subplots. Useful when there is no spacing in between subplots.
    INPUT:
    which --- x for x axis, y for y axis
    '''
    if which == 'x':
        ticklocs = ax.xaxis.get_majorticklocs()
        interval = ticklocs[1] - ticklocs[0]
        ax.set_xlim((ticklocs[0] - .6 * interval,
                     ticklocs[-1] + .6 * interval))
    elif which == 'y':
        ticklocs = ax.yaxis.get_majorticklocs()
        interval = ticklocs[1] - ticklocs[0]
        ax.set_ylim((ticklocs[0] - .6 * interval,
                     ticklocs[-1] + .6 * interval))
    else:
        raise InputError('which has to be either x or y')
    return ax




def plot_DataArray(ax, da,
                   datetime_label = True,
                   title = '', label = ':D',
                   colour = 'b', linestyle = '-', marker = '.',
                   ylabel = 'ylabel', ylim = (-80, 80), yscale = 'linear'):
    '''
    Returns a line plot of time v.s some variable that is in an DataArray
    of dimensions (time, lon0, lat0), where lon0 and lat0 are fixed.
    INPUT:
    da --- xray DataArray
    datetime_label --- True to use Python datetime objects to represent time
    label --- string used to label the line, needed to the legend
    OUTPUT:
    ax --- matplotlib Axes object
    '''
    x = da.coords['time'].values
    y = da[{'lon': 0, 'lat': 0}].values
    
    ax.plot(x, y,
            label = label,
            color = colour, linestyle = linestyle, marker = marker)
    
    ax.set_title(title)

    # backround
    ax.set_axis_bgcolor((1., 1., 1.))
    ax.set_axisbelow(b = True)

    # y-axis
    ax.set_ylabel('{}'.format(ylabel) + \
                  ' [{}]'.format(da.units))
    ax.set_yscale(yscale)
    ax.set_ylim(ylim)
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(10))
    ax.yaxis.set_tick_params(length = 6., which = 'major')
    ax.yaxis.set_tick_params(length = 3., which = 'minor')
    ax.yaxis.grid(b = True, which = 'major', color = (0., 0., 0.))

    # x-axis
    ax.set_xlabel('{} [{}]'.format(da.coords['time'].attrs['long_name'],
                                   da.coords['time'].attrs['units']))
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval = 1))
    ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator(byhour = [6, 12, 18]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d\n%b'))
    ax.xaxis.grid(b = True, which = 'major', color = (0., 0., 0.))
    ax.xaxis.set_tick_params(length = 6., which = 'major')
    ax.xaxis.set_tick_params(length = 3., which = 'minor')
    return ax


def plot_vertical_profile(ax, da,
                          label = '', colour = 'b', linestyle = '-',
                          title = None,
                          xlabel = None, xlim = None, xscale = 'linear',
                          xlabels_rotate = 0.,
                          ylabel = None, ylim = None, yscale = 'linear'):
    '''
    Plots vertical profile (i.e. pressure against some variable) on a maplotlib Axes
    INPUT:
    xaxis_pow --- power of 10 to multiply xlabels by (if equals = 10, 150 because 1500 * 1e-1)
    xlabels_rotate --- angle to rotate xlabels by [degrees]
    '''
    y = da.coords['lev'].values
    x = da[{'lon': 0, 'lat': 0}].values
    
    ax.plot(x, y,
            label = label, color = colour, linestyle = linestyle, linewidth = 1.5)
    
    if title:
        ax.set_title(title)
        
    # background
    ax.set_axis_bgcolor((1., 1., 1.))
    ax.set_axisbelow(b = True)
    
    # y-axis
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)
    ax.set_yscale(yscale)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(100))
    ax.yaxis.grid(b = True, which = 'major')
    
    # x-axis
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_xlim(xlim)
    ax.set_xscale(xscale)
    ax.xaxis.grid(b = True, which = 'major')

    xticklocs = ax.xaxis.get_majorticklocs()
    xtick_interval = xticklocs[1] - xticklocs[0]
    xaxis_pow = muths.pow_base10_for_decimal(xtick_interval, decimal = 1)
    ax.xaxis_pow = xaxis_pow
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, pos: '{:.1f}'.\
                                        format(10**xaxis_pow * x)))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation = xlabels_rotate)


    return ax



def contourf_DataArray(ax, da,
                       datetime_label = True, mbar_label = True,
                       cmap_levels = None,
                       cmap = matplotlib.cm.jet):
    '''
    Returns a contour-fill plot of time vs level vs variable for variable
    of dimensions (time, level, lon0, lat0), where lon0 and lat0 are fixed.
    INPUT:
    da --- xray DataArray
    cmap_levels --- tuple (extend, vmin, vmax, vstep) of
                   whether to extend colormap,
                   minimum, maximum and step of contour levels to use
    cmap --- maplotlib colormap object
    '''
    y = da['lev'].values
    x = [pd.Timestamp(dtns).to_datetime() for dtns in da['time'].values]
    Z = da.transpose('lev', 'time')

    if cmap_levels:
        extend, lev_min, lev_max, lev_step = cmap_levels
    else:
        lev_min, lev_max, lev_step = Z.min(), Z.max(), (Z.max() - Z.min()) / 20
        
    levels = np.arange(lev_min, lev_max + .1 * lev_step, lev_step)
    
    cs = ax.contourf(x, y, Z,
                     levels = levels,
                     cmap = cmap,
                     extend = extend)
    
    cs.cmap.set_over('yellow')
    cs.cmap.set_under('black')

    cbar = plt.colorbar(cs, ax = ax)
    cbar.ax.set_ylabel('[{}]'.format(da.units))
    cbar.set_ticks(levels)
    
    cbar.formatter.set_powerlimits((0, 0)) # this works as alternative to what's below

#    cbarlabel_decimal = 0
#    cbartick_pow = muths.pow_base10_for_decimal(lev_step,
#                                                decimal = cbarlabel_decimal)
#    print(lev_step, cbartick_pow)
#    cbar_format_string = '{}' #'{{:.{}f}}'.format(cbarlabel_decimal)
#    cbar.formatter = matplotlib.ticker.FuncFormatter(
#        lambda x, pos: cbar_format_string.format(10**int(cbartick_pow) * x))

#    cbar.ax.text(x = 1, y = 1.07, s = '1e{}'.format(- cbartick_pow))

    cbar.update_ticks()
    
    ax.set_title('{}\n{}'.format(da.attrs['case_name'],
                                 da.attrs['long_name']))
    
    [spine.set_color((1., 1., 1)) for k, spine in ax.spines.items()]
    
    ax.invert_yaxis()
    ax.set_ylabel('lev [{}]'.format(da['lev'].units))
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(50))
    ax.yaxis.grid(b = True, which = 'major')
    ax.yaxis.set_tick_params(length = 6, which = 'major')
    ax.yaxis.set_tick_params(length = 3, which = 'minor')

    ax.set_xlabel('time [{}]'.format(da['time'].units))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(interval = 2))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('\n%b %y'))
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.grid(b = True, which = 'minor')
    ax.xaxis.set_tick_params(length = 6, which = 'major')
    ax.xaxis.set_tick_params(length = 3, which = 'minor')
    
    return ax




def daytime_nighttime_shading(ax, dts,
                              hour_daystart = 8, hour_nightstart = 18):
    '''
    Shades in colours for day-time and night-time.
    INPUT:
    ax --- matplotlib Axes object
    dts --- an array/list of Pandas Timestamps (a Pandas DatetimeIndex)
    hour_daystart --- hour at which day-time starts
    hour_nightstart --- hour at which night-time starts
    '''
    # Change the Hour of each Timestamp to correspond to
    # that at which day-time or night-time starts
    dtsDN = dts.map(lambda x: dates.to_daytime_nighttime(\
        x, hour_daystart = hour_daystart,
        hour_nightstart = hour_nightstart))

    # Find and sort the boundries, datetimes at which each day-teim
    # and night-time period starts.  This includes incomplete periods
    # at either ends
    DNbndries = sorted([dts[0]] + \
                       [ts.to_datetime() for ts in set(dtsDN)] + \
                       [dts[-1]])
    
    # Fill in colours between the boundaries
    for leftbnd, rightbnd in zip(DNbndries[: -1], DNbndries[1:]):
        if leftbnd.hour == hour_daystart or \
               rightbnd.hour == hour_nightstart:
            ax.axvspan(leftbnd, rightbnd,
                       color = 'yellow', alpha = .1, edgecolor = None)
        else:
            ax.axvspan(leftbnd, rightbnd,
                       color = 'black', alpha = .1, edgecolor = None)
    return ax



def get_common_cmap_levels(cmap_levels, Nsteps = 10):
    cmap_minmin = sorted(cmap_levels, key = lambda x: x[1])[0]
    cmap_maxmax = sorted(cmap_levels, key = lambda x: x[2])[0]

    if cmap_minmin[0] in ['min', 'both']:
        extend_min = True
    else:
        extend_min = False
    if cmap_maxmax[0] in ['max', 'both']:
        extend_max = True
    else:
        extend_max = False
        
    if extend_min and not extend_max:
        extend = 'min'
    elif extend_max and not extend_min:
        extend = 'max'
    elif extend_min and extend_max:
        extend = 'both'
    else:
        extend = 'neither'
        
    if extend == 'both':
        cmap_limits = (extend, max(abs(cmap_minmin[1]), abs(cmap_maxmax[2])), )
        Nsteps = 11
    elif extend in ['min', 'max']:
        cmap_limits = (extend, cmap_minmin[1], cmap_maxmax[2])
        Nsteps = 10
        
    return get_nicenround_steps(cmap_limits, Nsteps = Nsteps)
    



def get_cmap_limits(da, quantile = .5):
    '''
    Returns colormap limits from an xray DataArray.
    INPUT:
    da --- DataArray
    quantile --- between 0 and 1
    OUTPUT:
    (extend, lev_min or abs(lev_max), lev_max)
    extend --- how to extend the colormap, can be \'min\', \'max\', or \'both\'
    lev_min --- value of minimum level
    lev_max --- value of maximum level
    abs(lev_max) --- for data array with positive and negative values,
                     the value of the level that is farthest from zero
    '''
    df = da.to_pandas()
    
    if np.all(df <= 0):
        lev_min = df.stack().quantile(q = 1 - quantile)
        return ('min', lev_min, 0.)
    elif np.all(df >= 0):
        lev_max = df.stack().quantile(q = quantile)
        return ('max', 0., lev_max)
    else:
        dfmax, dfmin = df.stack().min(), df.stack().max()
        if abs(dfmax) > abs(dfmin):
            cmap_limit = df[df >= 0].stack().quantile(q = quantile)
        elif abs(dfmax) < abs(dfmin):
            cmap_limit = df[df <= 0].stack().quantile(q = 1 - quantile)
        else:
            cmap_limit = df[df >= 0].stack().quantile(q = quantile)
        return ('both', abs(cmap_limit))
        



def get_nicenround_steps(cmap_limits, Nsteps = 10):
    '''
    Readjust given colormap limits in order to have
    nice and rounded intervals between levels.
    INPUT:
    cmap_limits --- tuple of extend, min level, max level
                    or for extend == both, tuple of extend, max magnitude
    Nsteps --- number of intervals in the colormap
    OUTPUT:
    tuple of extend, min level, max level, interval between level
    '''
    if cmap_limits[0] == 'both':
        # align the centre with zero
        minmaxstep = symmetric_about_white_cmap_levels(cmap_limits[1],
                                                       Ncolours = Nsteps)
        return tuple(['both'] + list(minmaxstep))
    elif cmap_limits[0] in ['min', 'max']:
        extend, cmap_min, cmap_max = cmap_limits
        rough_cmap_step = (cmap_max - cmap_min) / Nsteps
        nice_cmap_step = muths.round_to_1(rough_cmap_step)
        if extend == 'min':
            # align the top
            nice_cmap_min = cmap_max - Nsteps * nice_cmap_step
            return (extend, nice_cmap_min, cmap_max, nice_cmap_step)
        elif extend == 'max':
            # align the bottom
            nice_cmap_max = cmap_min + Nsteps * nice_cmap_step
            return (extend, cmap_min, nice_cmap_max, nice_cmap_step)
        
            


def get_cmap_levels(da, quantile = .5):
    '''
    Get colormap levels for contourf plotting from data array
    INPUT:
    da --- DataArray
    quantile --- between 0. and 1., to indicate from what value
                 the colormap should extend beyond
    OUTPUT:
    tuple of (extend, minimum level, maximum level, interval between levels)
    '''
    cmap_limits = get_cmap_limits(da, quantile = quantile)
    if cmap_limits[0] == 'both':
        Nsteps = 11
    else:
        Nsteps = 10
    cmap_levels = get_nicenround_steps(cmap_limits,
                                       Nsteps = Nsteps)
    return cmap_levels
    
            



def contourf_interest_for_all_cases(d3sets, interest = 'CLOUD',
                                   cmap = plt.get_cmap('PuBuGn')):
    '''
    Function to contourf a set of DataArrays
    INPUT:
    d3sets --- a dictionary of xray.Datasets containing xray.DataArrays of
               dimensions (time, lev, lon, lat)
    interest --- which field to plot
    cmap --- matplotlib colormap object, i.e. which colormap to use for contourf
    '''
    cases = sorted(d3sets.keys())

    das = [d3sets[case][interest][{'lon': 0, 'lat': 0}] for case in cases]

    cmap_levels = [get_cmap_levels(da, quantile = .9999)\
                   for da in das]
    common_cmap_levels = get_common_cmap_levels(cmap_levels)

    Nplots = len(cases)
    
    fig, axes = plt.subplots(nrows = 1, ncols = Nplots,
                             figsize = (5.3 * Nplots, 5), dpi = 300)
    
    for ax, da in zip([axes] if Nplots == 1 else axes, das):
        ax = contourf_DataArray(ax, da,
                                cmap_levels = common_cmap_levels,
                                cmap = cmap)
    plt.tight_layout()
    return fig
        
        
        

def plotVS_timeaveraged_interest_for_all_cases(d3sets, diff_d3sets,
                                               interest = 'CLOUD',
                                               xscale = 'linear',
                                               bot_xlim = None,
                                               bot_xlabels_rotate = 0.,
                                               top_xlim = None,
                                               top_xlabels_rotate = 0.,
                                               yscale = 'linear',
                                               ylim = None,):
    line_props = get_line_props()
    
    vspairs = [[p.strip() for p in diff_case.split('-')]
               for diff_case in sorted(diff_d3sets.keys())]
    
    fig, axes = plt.subplots(figsize = (9, 9), dpi = 300,
                             nrows = 1, ncols = len(vspairs),
                             sharey = True)
    
    labels, handles = [], []
    
    axes[0].invert_yaxis()
    
    for ax, vspair in zip(axes, vspairs):
        x, y = vspair
        
        for model in vspair:
            da = average_over_time(d3sets[model][interest])
            
            # plot each member in the comparison pair
            ax = climaviz.plot_vertical_profile(ax, da,
                                                label = '{}'.format(model),
                                                colour = line_props[model]['colour'],
                                                linestyle = line_props[model]['linestyle'],
                                                xscale = xscale,
                                                xlabels_rotate = bot_xlabels_rotate,
                                                yscale = yscale)

        ax = climaviz.axes_beyond_ticks(ax, which = 'x')
            
        # plot difference on twiny
        ax2 = ax.twiny()
        
        da = average_over_time(diff_d3sets[' - '.join(vspair)][interest])
        
        ax2 = climaviz.plot_vertical_profile(ax2, da,
                                             label = 'difference',
                                             colour = (0.929, 0.329, 0.972), linestyle = '-',
                                             xscale = xscale, xlabels_rotate = top_xlabels_rotate,
                                             yscale = yscale)
        
        ax2 = climaviz.axes_beyond_ticks(ax2, which = 'x')
            
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax.get_legend_handles_labels()
        handles.extend(handles1 + handles2)
        labels.extend(labels1 + labels2)
        
    ## Make 1 legend for whole figure
    uhandles, ulabels = climamisc.any_unique_labels(handles, labels)
    uhandles, ulabels = zip(*sorted(zip(uhandles, ulabels), key = lambda x: x[1]))
    fig.legend(uhandles, ulabels,
               loc = 'center', ncol = 3,
               bbox_to_anchor = (.35, .85), prop = {'size': 12})
    
    fig.suptitle(da.attrs['long_name'])
    
    plt.figtext(x = 0.02, y = .5, s = 'lev [mbar]', rotation = 90.)
    plt.figtext(x = .45, y = 0.08, s = '{} [{}]'.format(interest, da.units))
    plt.figtext(x = .9, y = 0.08, s = '1e{}'.format(- ax.xaxis_pow))
    plt.figtext(x = .7, y = .91, s = 'difference')
    plt.figtext(x = .9, y = .91, s = '1e{}'.format(- ax2.xaxis_pow))
    plt.subplots_adjust(wspace = 0., top = .84, bottom = .15)
    
