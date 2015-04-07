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



def plot_DataArray(ax, da,
                   datetime_label = True,
                   title = '', label = ':D', colour = 'b', linestyle = '-',
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
            label = label, color = colour, linestyle = linestyle)
    
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



def contourf_DataArray(ax, da,
                       datetime_label = True, mbar_label = True,
                       contour_levels = None,
                       cmap = matplotlib.cm.jet,
                       extend = 'neither'):
    '''
    Returns a contour-fill plot of time vs level vs variable for variable
    of dimensions (time, level, lon0, lat0), where lon0 and lat0 are fixed.
    INPUT:
    da --- xray DataArray
    contour_levels --- tuple (vmin, vmax, vstep) of
                   minimum, maximum and step of contour levels to use
    cmap --- maplotlib colormap object
    extend --- whether use colour and extend colorbar for those values
               above maximum contour level, or below minimum contour level:
               \'neither\', \'both\', \'min\' or \'max\'
    '''

    y = da['lev'].values
    x = [pd.Timestamp(dtns).to_datetime() for dtns in da['time'].values]
    Z = da[{'lon': 0, 'lat': 0}].transpose('lev', 'time')
    
    if contour_levels:
        lev_min, lev_max, lev_step = contour_levels
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
