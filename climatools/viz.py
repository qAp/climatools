import sys
import random
import numpy as np
import itertools
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as matcolors

import climatools.muths as muths
import climatools.dates as dates
import climatools.misc as misc




def matplotlib_basic_colours():
    '''
    Returns a list of plot colours available in matplotlib.
    The colours in this list are easily distinguished from each
    other by eye.
    '''
    return ['b', 'g', 'r', 'c', 'm', 'y', 'k']


def matplotlib_nonnothing_linestyles(longname = False):
    '''
    Returns the list of plot linestyles available in matplotlib.
    Linestyles that are invisible are left out of this list.
    '''
    if longname:
        return [v for k, v in Line2D.markers.items() if v != '_draw_nothing']
    else:
        return [k for k, v in Line2D.lineStyles.items()
                if v != '_draw_nothing']
    
    
def matplotlib_nonnothing_markers(longname = False):
    '''
    Returns the list of plot markers available in matplotlib.
    Markers that are invisible are left out of this list.
    '''
    if longname:
        return [v for k, v in Line2D.markers.items() if v != 'nothing']
    else:
        return [k for k, v in Line2D.markers.items() if v != 'nothing']


def matplotlib_colour_linestyle_tuples(N = 10):
    '''
    Returns a shuffled list of unique tuples of plot colours and linestyles
    of length Npairs.
    INPUT:
    Npairs --- length of list returned,
    the number of unique tuples of plot colours and linestyles returned.
    '''
    colours = matplotlib_basic_colours()
    linestyles = matplotlib_nonnothing_linestyles()
    
    uniques = list(itertools.product(colours, linestyles))
    
    random.shuffle(uniques)
    return random.sample(uniques, N)


def matplotlib_colour_linestyle_marker_tuples(N = 10):
    colours = matplotlib_basic_colours()
    linestyles = matplotlib_nonnothing_linestyles()
    markers = matplotlib_nonnothing_markers()
    
    uniques = list(itertools.product(colours, linestyles, markers))
    
    random.shuffle(uniques)
    return random.sample(uniques, N)


def matplotlib_colormap_names(kind = 'divergent'):
    cmaps = dict([('Sequential', ['Blues', 'BuGn', 'BuPu',
                                  'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                                  'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                                  'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']),
                  ('Sequential (2)', ['afmhot', 'autumn', 'bone', 'cool', 'copper',
                                      'gist_heat', 'gray', 'hot', 'pink',
                                      'spring', 'summer', 'winter']),
                  ('Diverging',      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                                      'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                                      'seismic']),
                  ('Qualitative',    ['Accent', 'Dark2', 'Paired', 'Pastel1',
                                      'Pastel2', 'Set1', 'Set2', 'Set3']),
                  ('Miscellaneous',  ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                                      'brg', 'CMRmap', 'cubehelix',
                                      'gnuplot', 'gnuplot2', 'gist_ncar',
                                      'nipy_spectral', 'jet', 'rainbow',
                                      'gist_rainbow', 'hsv', 'flag', 'prism'])])
    
    ccmaps = dict([('sequential', cmaps['Sequential'] + cmaps['Sequential (2)']),
                   ('diverging', cmaps['Diverging']),
                   ('qualitative', cmaps['Qualitative']),
                   ('misc', cmaps['Miscellaneous'])])
    return ccmaps[kind]


def dates_locators_by_timescale():
    locators = {'year': matplotlib.dates.YearLocator,
                'month': matplotlib.dates.MonthLocator,
                'day': matplotlib.dates.DayLocator,
                'hour': matplotlib.dates.HourLocator,
                'minute': matplotlib.dates.MinuteLocator}
    return locators

    

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




def round_levels_with_zero_centred_between_two(vmin0 = -1, vmax0 = 2, Nsteps0 = 10):
    '''
    Suppose you want to divide the range (vmin0, vmax0) into roughly Nsteps0 intervals, where vmin0 < 0 < vmax0.
    This function returns a new range(vmin, vmax) and new Nsteps that is
    as close to the desired one as possible, but are such that dv = (vmax - vmin) / Nsteps
    is a nice round value, and the value zero is centred on one of the Nsteps intervals.
    INPUT:
    vmin0 --- lower limit, must be negative.
    vmax0 --- upper limit, must be positive.
    Nsteps0 --- rough desired number of intervals between vmin0 and vmax0.
    OUTPUT:
    vmin --- lower limit
    vmax --- upper limit
    Nsteps --- number of intervals between vmin and vmax
    '''
    dv0 = (vmax0 - vmin0) / Nsteps0
    dv = muths.round_to_1(dv0)
    half_dv = .5 * dv
    vmin = 0 - dv * int(np.ceil((0 - vmin0 - half_dv) / dv)) - half_dv
    vmax = 0 + dv * int(np.ceil((vmax0 - 0 - half_dv) / dv)) + half_dv
    Nsteps = int((vmax - vmin) / dv)
    return (vmin, vmax, Nsteps)
    
    

def slice_divergent_colormap(cmap = None, vmin = -1, vmax = 2):
    '''
    A divergent colormap is one that is centred at white, while extending
    to the two sides of it are two distintive colour types.  For example,
    the divergent colormap bwr is centred on white; to one side are blues
    and to the other reds. The length on either side of white are the same
    by default, making it useful to map to intervals where the negative and
    positive limits are equal in maginitude, such as (-1, 1), (-241, 241), etc.

    This function slices the default colormap up such that it can be mapped
    to (keeping white mapped to zero)
    intervals that are not symmetrical about 0, such as (-100, 2), (-2, 349), etc.
    
    INPUT:
    cmap -- matplotlib colormap object (only really makes sense with a divergent one)
    vmin -- lower limit of interval (negative)
    vmax -- upper limit of interval (positive)
    OUTPUT:
    sliced_cmap -- sliced colormap with white mapped to zero of the interval (vmin, vmax)
    '''
    if not cmap:
        cmap = plt.get_cmap('bwr')
        
    real_range = vmax - vmin
    largest_abs_range = 2 * max(abs(vmin), abs(vmax))
    fractional_range = real_range / largest_abs_range
    
    if abs(vmin) > abs(vmax):
        cmap_min, cmap_max = 0, fractional_range
    elif abs(vmax) > abs(vmin):
        cmap_min, cmap_max = 1 - fractional_range, 1
    else:
        cmap_min, cmap_max = 0, 1

    sliced_cmap = matcolors.\
                  LinearSegmentedColormap.from_list('test_cmap',
                                                    cmap(np.linspace(cmap_min, cmap_max)))
    return sliced_cmap
    



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



def get_datetime_major_locator(xlist):
    '''
    Return a good dates locator for major ticks.
    INPUT:
    xlist --- list: [number of unique years amongst minor ticks,
                     number of unique months amongst minor ticks,
                     number of unique days amongst minor ticks,
                     number of unique hours amongst minor ticks,
                     number of unique minutes amongst minor ticks]
    OUTPUT:
    locator  -- one of [matplotlib.dates.YearLocator,
                        matplotlib.dates.MonthLocator,
                        matplotlib.dates.DayLocator,
                        matplotlib.dates.HourLocator,
                        matplotlib.dates.MinuteLocator]
    '''
    locators = [matplotlib.dates.YearLocator,
                matplotlib.dates.MonthLocator,
                matplotlib.dates.DayLocator,
                matplotlib.dates.HourLocator,
                matplotlib.dates.MinuteLocator]
    
    max_number_majorticks = 5

    for k, x in enumerate(xlist):
        if x <= 1:
            continue
        else:
            if x > max_number_majorticks:
                return locators[k - 1] if k > 0 else None
            else:
                return locators[k]
            return None



def get_N_unique_datetimeperiod_labels(ticklocs):
    '''
    Return  number of unique datetime labels for periods
    YEAR, MONTH, DAY, HOUR, MINUTE.
    INPUT:
    ticklocs --- tick locators in datetime in floating point numbers
                 (days since 0001-01-01 UTC, plus 1)
    OUTPUT --- list: [number of unique years amongst minor ticks,
                      number of unique months amongst minor ticks,
                      number of unique days amongst minor ticks,
                      number of unique hours amongst minor ticks,
                      number of unique minutes amongst minor ticks] 
    '''
    minorticklocs = [matplotlib.dates.num2date(tickloc)
                    for tickloc in ticklocs] #ax.xaxis.get_minorticklocs()
    return [len(set([tickloc.year for tickloc in minorticklocs])),
            len(set([tickloc.month for tickloc in minorticklocs])),
            len(set([tickloc.day for tickloc in minorticklocs])),
            len(set([tickloc.hour for tickloc in minorticklocs])),
            len(set([tickloc.minute for tickloc in minorticklocs]))]



def split_to_major_minor_timescales(Nlabels):
    timescales = ('year', 'month', 'day', 'hour', 'minute',)

    maxN_major_ticks = 5

    for k, x in enumerate(Nlabels):
        if x <= 1:
            continue
        else:
            if x > maxN_major_ticks:
                return (timescales[: k], timescales[k:])
            else:
                return (timescales[: k + 1], timescales[k + 1:])
            return timescales[:]
    return major_timescales, minor_timescales




def get_datetime_tick_formats(timescales):
    directives = {'year':   '%Y',
                  'month':  '%m',
                  'day':    '%d',
                  'hour':   '%H',
                  'minute': '%M'}
    ymds = [directives[timescale] for timescale in timescales
            if timescale in ['year', 'month', 'day']]
    hms = [directives[timescale] for timescale in timescales
           if timescale in ['hour', 'minute']]
    return ' '.join(['/'.join(ymds), ':'.join(hms)])




def set_xaxis_datetime_ticklocs_ticklabels(xaxis, duration = pd.Timedelta(days = 1)):
    '''
    Set major and minor tick locations and labels
    INPUT:
    xaxis --- matplotlib.axis.xaxis/yaxis on which ticks and ticklabels are to be set
    duration --- duration which the axis spans in pandas.Timedelta 
    '''
    # maximum allowed major and minor intervals
    maxN_major, maxN_minor = 5, 18

    timescales = ('year', 'month', 'day', 'hour', 'minute')

    locators = (
        matplotlib.dates.YearLocator,
        matplotlib.dates.MonthLocator,
        matplotlib.dates.DayLocator,
        matplotlib.dates.HourLocator,
        matplotlib.dates.MinuteLocator,
        )

    bylocators = (
        lambda x: matplotlib.dates.YearLocator(x),
        lambda x: matplotlib.dates.MonthLocator(bymonth = range(1, 13, x)),
        lambda x: matplotlib.dates.DayLocator(bymonthday = range(1, 32, x)),
        lambda x: matplotlib.dates.HourLocator(byhour = range(0, 24, x)),
        lambda x: matplotlib.dates.MinuteLocator(byminute = range(0, 60, x))
        )

    timedeltas = (pd.Timedelta(days = 365),
                  pd.Timedelta(days = 30),
                  pd.Timedelta(days = 1),
                  pd.Timedelta(hours = 1),
                  pd.Timedelta(minutes = 1))

    # get number of timescales in duration
    N_tscales = [duration / timedelta for timedelta in  timedeltas]

    # choose which timescales to be major and minor
    # get the index
    # essentially the rule is that the number of major intervals cannot
    # exceed maxN_major
    gr8r_than_1 = [n > 1 for n in N_tscales]
    if not any(gr8r_than_1):
        indx_major, idx_minor = -1, None
    elif all(gr8r_than_1):
        if N_tscales[0] > maxN_major:
            indx_major, indx_minor = None, 0
        else:
            index_major, indx_minor = 0, 1
    else:
        indx = gr8r_than_1.index(True)
        if N_tscales[indx] > maxN_major:
            indx_major, indx_minor = indx - 1, indx
        else:
            indx_major, indx_minor = indx, indx + 1


    # create major dates locator
    if indx_major:
        locator_major = locators[indx_major]()

    # create major tick label formatters
    if indx_major:
        fmt_major = get_datetime_tick_formats(timescales[: indx_major + 1])

    # create major ticks and labels
    if indx_major:
        xaxis.set_major_locator(locator_major)
        xaxis.set_major_formatter(matplotlib.dates.DateFormatter('\n' + fmt_major))

                                             
    # create minor dates locator
    if indx_minor:
        if N_tscales[indx_minor] <= maxN_minor:
            locator_minor = locators[indx_minor]()
        else:
            # scale down the number of minor ticks if there are too many
            N_to_group = int(np.ceil(N_tscales[indx_minor] / maxN_minor))
            locator_minor = bylocators[indx_minor](N_to_group)

    # create minor tick formatters
    if indx_minor:
        fmt_minor = get_datetime_tick_formats([timescales[indx_minor]])

    # create minor ticks and labels
    if indx_minor:
        xaxis.set_minor_locator(locator_minor)
        xaxis.set_minor_formatter(matplotlib.dates.DateFormatter(fmt_minor))

    
    
    


    
def plot_DataArray(ax, da,
                   datetime_label = True,
                   title = '', label = ':D',
                   colour = 'b', linestyle = '-', marker = '.',
                   ylabel = 'ylabel', ylim = None, yscale = 'linear'):
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
    if 'lev' in da:
        yname = 'lev'
    elif 'ilev' in da:
        yname = 'ilev'
    else:
        raise ValueError('vertical dimension must be either named lev or ilev')
    
    y = da.coords[yname].values
    x = da[{'lon': 0, 'lat': 0}].values
    
    ax.plot(x, y,
            label = label, color = colour, linestyle = linestyle, linewidth = 2.3)
    
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
    ax.set_xscale(xscale)
    ax.xaxis.grid(b = True, which = 'major')

    if xlim:
        ax.set_xlim(xlim)
    else:
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
    if 'lev' in da:
        spatial_dim = 'lev'
    elif 'ilev' in da:
        spatial_dim = 'ilev'
    else:
        raise ValueError('spatial dimension to plot must be either lev or ilev')
    
    y = da[spatial_dim].values
    x = [pd.Timestamp(dtns).to_datetime() for dtns in da['time'].values]
    Z = da.transpose(spatial_dim, 'time')

    if cmap_levels:
        extend, lev_min, lev_max, lev_step = cmap_levels
    else:
        lev_min, lev_max, lev_step = Z.min(), Z.max(), (Z.max() - Z.min()) / 20
        extend = 'neither'

    if extend == 'both':
        cmap = slice_divergent_colormap(cmap = cmap, vmin = lev_min, vmax = lev_max)
        levels = np.linspace(lev_min, lev_max,
                             int((lev_max - lev_min) / lev_step) + 1)
    else:
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
                                 da.attrs['long_name']),
                 fontsize = 10)
    
    [spine.set_color((1., 1., 1)) for k, spine in ax.spines.items()]
    
    ax.invert_yaxis()
    ax.set_ylabel('{} [{}]'.format(spatial_dim, da[spatial_dim].units))
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(50))
    ax.yaxis.grid(b = True, which = 'major')
    ax.yaxis.set_tick_params(length = 6, which = 'major')
    ax.yaxis.set_tick_params(length = 3, which = 'minor')

    ax.set_xlabel('time [{}]'.format(da['time'].units))
    set_xaxis_datetime_ticklocs_ticklabels(ax.xaxis,
                                           duration = pd.Timedelta(x[-1] - x[0]))
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

    # Find and sort the boundries, datetimes at which each day-time
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
    '''
    Given several sets of colormap levels, find a common set
    that covers all the sets, with (Nsteps + 1) levels
    INPUT:
    cmap_levels --- a list of sets of colormap levels
    Nsteps --- number of intervals in the return set of levels
    OUTPUT:
    (extend, colormap min, colormap max)
    '''
    cmap_minmin = sorted(cmap_levels, key = lambda x: x[1])[0]
    cmap_maxmax = sorted(cmap_levels, key = lambda x: x[2])[-1]

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
        
    cmap_limits = (extend, cmap_minmin[1], cmap_maxmax[2])        
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
    dfs = df.stack()
    
    if np.all(dfs == 0):
        return ('both', - 1e-10, 1e-10)
    elif np.all(dfs <= 0):
        lev_min = dfs.quantile(q = 1 - quantile)
        return ('min', lev_min, 0.)
    elif np.all(dfs >= 0):
        lev_max = dfs.quantile(q = quantile)
        return ('max', 0., lev_max)
    else:
        return ('both',
                dfs[dfs <= 0].quantile(q = 1 - quantile),
                dfs[dfs >= 0].quantile(q = quantile))


def get_nicenround_steps(cmap_limits, Nsteps = 10):
    '''
    Readjust given colormap limits in order to have
    nice and rounded intervals between levels.
    INPUT:
    cmap_limits --- tuple of extend, min level, max level
    Nsteps --- number of intervals in the colormap
    OUTPUT:
    tuple of extend, min level, max level, interval between level
    '''
    if cmap_limits[0] == 'both':
        cmap_min, cmap_max, cmap_Nsteps = round_levels_with_zero_centred_between_two(
            vmin0 = cmap_limits[1], vmax0 = cmap_limits[2], Nsteps0 = Nsteps)
        cmap_step = (cmap_max - cmap_min) / cmap_Nsteps
        return ('both', cmap_min, cmap_max, cmap_step)
    elif cmap_limits[0] in ['min', 'max']:
        extend, cmap_min, cmap_max = cmap_limits
        rough_cmap_step = (cmap_max - cmap_min) / Nsteps
        nice_cmap_step = muths.round_to_1(rough_cmap_step)
        cmap_Nsteps = int(np.ceil((cmap_max - cmap_min) / nice_cmap_step))
        if extend == 'min':
            # align the top
            nice_cmap_min = cmap_max - cmap_Nsteps * nice_cmap_step
            return (extend, nice_cmap_min, cmap_max, nice_cmap_step)
        elif extend == 'max':
            # align the bottom
            nice_cmap_max = cmap_min + cmap_Nsteps * nice_cmap_step
            return (extend, cmap_min, nice_cmap_max, nice_cmap_step)



def get_suitable_cmap(cmap_levels):
    '''
    Selects a divergent colormap if the colormap levels
    are positive and negative.
    INPUT:
    cmap_levels --- tuple (extend, cmap_min, cmap_max, cmap_step)
                    where extend is either \'min\', \'max\' or \'both\'.
    '''
    extend = cmap_levels[0]
    if extend == 'both':
        return plt.get_cmap('bwr')
    else:
        return plt.get_cmap('PuBuGn')
            

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

    quantile, Nsteps = .9999, 17
    cmap_limitss = [get_cmap_limits(da, quantile = quantile) for da in das]
    cmap_levels = [get_nicenround_steps(cmap_limits, Nsteps = Nsteps)
                   for cmap_limits in cmap_limitss]

    common_cmap_levels = get_common_cmap_levels(cmap_levels, Nsteps = Nsteps)

    if cmap == 'auto-select':
        cmap = get_suitable_cmap(common_cmap_levels)

    Nplots = len(cases)
    
    fig, axes = plt.subplots(nrows = 1, ncols = Nplots,
                             figsize = (10. * Nplots, 5), dpi = 300)
    
    for ax, da in zip([axes] if Nplots == 1 else axes, das):
        ax = contourf_DataArray(ax, da,
                                cmap_levels = common_cmap_levels,
                                cmap = cmap)
    plt.tight_layout()
    return fig
        
        
        
def plotVS_timeaveraged_interest_for_all_cases(d3sets, diff_d3sets,
                                               interest = 'CLOUD',
                                               xscale = 'linear',
                                               bot_xlim = None, bot_xlabels_rotate = 0.,
                                               top_xlim = None, top_xlabels_rotate = 0.,
                                               yscale = 'linear', ylim = None,
                                               linestyles = None):
    
    
    vspairs = [[p.strip() for p in diff_case.split('-')]
               for diff_case in sorted(diff_d3sets.keys())]
    
    Nplots = len(vspairs)
    
    fig, axes = plt.subplots(figsize = (9, 9), dpi = 300,
                             nrows = 1, ncols = Nplots,
                             sharey = True)
    
    labels, handles = [], []
    
    axes.invert_yaxis() if Nplots ==1 else axes[0].invert_yaxis()
    
    for ax, vspair in zip([axes] if Nplots == 1 else axes, vspairs):
        x, y = vspair
        
        for model in vspair:
            if interest in ['AREI', 'AREL']:
                da = dates.average_over_time(d3sets[model][interest], key = lambda x: x > 0)
            else:
                da = dates.average_over_time(d3sets[model][interest])
            
            # plot each member in the comparison pair
            ax = plot_vertical_profile(ax, da,
                                       label = '{}'.format(model),
                                       colour = linestyles[model]['colour'],
                                       linestyle = linestyles[model]['linestyle'],
                                       xscale = xscale, xlabels_rotate = bot_xlabels_rotate,
                                       yscale = yscale,
                                       xlim = bot_xlim)
            
        ax = axes_beyond_ticks(ax, which = 'x')

        # plot difference on twiny
        diff_colour = (0.929, 0.329, 0.972)
        ax2 = ax.twiny()
        
        da = dates.average_over_time(diff_d3sets[' - '.join(vspair)][interest])
            
        ax2 = plot_vertical_profile(ax2, da,
                                    label = 'difference',
                                    colour = diff_colour, linestyle = '-',
                                    xscale = xscale, xlabels_rotate = top_xlabels_rotate,
                                    yscale = yscale,
                                    xlim = top_xlim)
        
        [ticklabel.set_color(diff_colour) for ticklabel in ax2.xaxis.get_ticklabels()]
        ax2 = axes_beyond_ticks(ax2, which = 'x')
        ax2.axvline(x = 0, color = 'r', alpha = .5)
        
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax.get_legend_handles_labels()
        handles.extend(handles1 + handles2)
        labels.extend(labels1 + labels2)
        
    ## Make 1 legend for whole figure
    uhandles, ulabels = misc.any_unique_labels(handles, labels)
    uhandles, ulabels = zip(*sorted(zip(uhandles, ulabels), key = lambda x: x[1]))
    fig.legend(uhandles, ulabels,
               loc = 'center', ncol = 3,
               bbox_to_anchor = (.35, .91), prop = {'size': 14})
    
    fig.suptitle(da.attrs['long_name'])
    
    plt.figtext(x = 0.02, y = .5, s = 'lev [mbar]', rotation = 90.)
    plt.figtext(x = .45, y = 0.08, s = '{} [{}]'.format(interest, da.units))
    plt.figtext(x = .7, y = .91, s = 'difference')
    if hasattr(ax2, 'xaxis_pow'):
        plt.figtext(x = .9, y = 0.08, s = '1e{}'.format(- ax.xaxis_pow))
        plt.figtext(x = .9, y = .91, s = '1e{}'.format(- ax2.xaxis_pow))
    plt.subplots_adjust(wspace = 0., top = .84, bottom = .15)
    return fig






def plotVS_interest_for_all_cases(dsets, diff_dsets, interest = 'FLNT',
                                  left_ylim = None,
                                  right_ylim = None,
                                  linestyles = None):

    vspairs = [[p.strip() for p in diff_case.split('-')]
               for diff_case in sorted(diff_dsets.keys())]
    
    Nplots = len(vspairs)
    
    fig, axes = plt.subplots(figsize = (11, 3 * Nplots + 2.5), dpi = 300,
                             nrows = Nplots, ncols = 1)
    
    handles, labels = [], []
    
    for ax, vspair in zip([axes] if Nplots == 1 else axes, vspairs):
        x, y = vspair
        
        for model in vspair:
            ax = plot_DataArray(ax, dsets[model][interest],
                                label = '{}'.format(model),
                                colour = linestyles[model]['colour'],
                                linestyle = linestyles[model]['linestyle'],
                                marker = '',
                                ylabel = interest, ylim = left_ylim)
            
        da = diff_dsets[' - '.join(vspair)][interest]
        
        diff_colour = (0.929, 0.329, 0.972)
        ax2 = ax.twinx()
        ax2 = plot_DataArray(ax2, da, label = 'difference',
                             title = '',
                             colour = diff_colour, linestyle = '-', marker = '',
                             ylim = right_ylim)
        ax2.set_ylabel('')
        [label.set_color(diff_colour)
         for label in ax2.yaxis.get_ticklabels()]
        
        ### background shading for daytime and nighttime
        ax2 = daytime_nighttime_shading(ax2, da.coords['time'].to_pandas().index,
                                        hour_daystart = 6, hour_nightstart = 18)
        
        ## collect handles and labels for legend later
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles.extend(handles1 + handles2)
        labels.extend(labels1 + labels2)
        
    ## Make 1 legend for whole figure
    uhandles, ulabels = misc.any_unique_labels(handles, labels)
    uhandles, ulabels = zip(*sorted(zip(uhandles, ulabels),
                                    key = lambda x: x[1]))
    
    fig.suptitle(da.attrs['long_name'])
    
    fig.legend(uhandles, ulabels,
               loc = 'center', ncol = 3,
               bbox_to_anchor = (.45, .91), prop = {'size': 12})
    plt.subplots_adjust(wspace = 0., top = .84, bottom = .15)
    return fig


def plot_pdseries_indexVSvalues_linearlog(srss=None,
                                          names=None,
                                          colours=None,
                                          linestyles=None,
                                          markers=None,
                                          ylim=None, ylabel=None, 
                                          xlim_linear=None, xlim_log=None,
                                          xlabel=None,
                                          title=None, 
                                          figsize=(8, 5)):
    '''
    Plots index versus values for one or more Pandas.Series,
    for both linear and log y-scales.
    
    When y-scale is linear, x-axis limits are the minimum and maximum
    values for the range of y above 1.  When y-scale log, x-axis limits
    are the minumum and maximum values for the range of y below 1.
    
    Parameters
    ----------
    srss : list of Pandas series to plot
    names : corresponding list of strings to label the above;
            these are used in the legend
    colours : corresponding list of matplotlib colours
              (e.g. \'k\', \'r\', etc.)
    linestyles : corresponding list of matplotlib linestyles
                 (e.g. \'-\', \'--\', etc.)
    markers : corresponding list of matplotlib markers
              (e.g. \'o\', \'+\', etc.)
    ylim : a tuple of length two containing the lower and upper
           limits on the y-axis
    xlim_linear : a tuple of length two containing
                  the lower and upper limits on the linear x-axis
    xlim_log : a tuple of length two containing the lower and upper limits
               on the log x-axis
    title : string containing the title of the figure
    xlabel : string containing the x-axis label
    ylabel : string containing the y-axis label
    figsize : tuple of length two containing the width and height,
              in centimetres, of the figure
    fig : matplotlib figure object for the plot
    '''
    xys = list(itertools.chain(*[(srs.values, srs.index.values)
                                 for srs in srss]))
    
    if not markers:
        markers = [None for _ in range(len(xys))]
        
    if not linestyles:
        linestyles = ['-' for _ in range(len(xys))]

    if not colours:
        colour_cycle = itertools.cycle(matplotlib_basic_colours())
        colours = [next(colour_cycle) for _ in range(len(xys))]

    if not names:
        names = [k + 1 for k in range(len(xys))]

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=figsize)
    
    for yscale, ax in zip(('linear', 'log'), axs):

        lines = ax.plot(*xys)

        [plt.setp(line,
                  linestyle=style, color=colour, marker=marker,
                  linewidth=2.)
         for line, style, colour, marker
         in zip(lines, linestyles, colours, markers)]
        
        ax.set_title(title)
        ax.grid(b=True)
        ax.legend(names, loc='best')

        if ylim:
            ax.set_ylim(ylim)
        ax.set_yscale(yscale)
        ax.invert_yaxis()
        ax.set_ylabel(ylabel)
        
        if yscale == 'linear':
            if xlim_linear:
                ax.set_xlim(xlim_linear)
            else:
                if ylim:
                    ymin, ymax = ylim
                    xmin = min([srs[(srs.index > 1e0) & (srs.index < ymax)]
                                .min() for srs in srss])
                    xmax = max([srs[(srs.index > 1e0) & (srs.index < ymin)]
                                .max() for srs in srss])
                else:
                    xmin = min([srs[srs.index > 1e0].min() for srs in srss])
                    xmax = max([srs[srs.index > 1e0].max() for srs in srss])
                    
                dx = xmax - xmin
                xmin -= .1 * dx
                xmax += .1 * dx
                ax.set_xlim((xmin, xmax))
        elif yscale == 'log':
            if xlim_log:
                ax.set_xlim(xlim_log)
            else:
                if ylim:
                    ymin, ymax = ylim
                    xmin = min([srs[(srs.index < 1e0) & (srs.index > ymin)]
                                .min() for srs in srss])
                    xmax = max([srs[(srs.index < 1e0) & (srs.index > ymin)]
                                .max() for srs in srss])
                else:
                    xmin = min([srs[srs.index < 1e0].min() for srs in srss])
                    xmax = max([srs[srs.index < 1e0].max() for srs in srss])
                    
                dx = xmax - xmin
                xmin -= .1 * dx
                xmax += .1 * dx
                ax.set_xlim((xmin, xmax))
                
        ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
        ax.set_xlabel(xlabel)
    return fig


def plot_pandas_series(ax=None,
                       srss=None, names=None,
                       colours=None, linestyles=None, markers=None,
                       values_vs_index=False,
                       logy=False, inverty=False, ylim=None, ylabel='ylabel',
                       logx=False, invertx=False, xlim=None, xlabel='xlabel',
                       title='title'):

    if values_vs_index:
        xys = list(itertools.chain(*[(srs.values, srs.index.values)
                                     for srs in srss]))
    else:
        xys = list(itertools.chain(*[(srs.index.values, srs.values)
                                     for srs in srss]))
    
    if not markers:
        markers = [None for _ in range(len(xys))]
        
    if not linestyles:
        linestyles = ['-' for _ in range(len(xys))]

    if not colours:
        colour_cycle = itertools.cycle(matplotlib_basic_colours())
        colours = [next(colour_cycle) for _ in range(len(xys))]

    if not names:
        names = [k + 1 for k in range(len(xys))]
        
    lines = ax.plot(*xys)

    [plt.setp(line,
              linestyle=style, color=colour, marker=marker,
              linewidth=1.7)
     for line, style, colour, marker
     in zip(lines, linestyles, colours, markers)]
        
    ax.set_title(title)
    ax.grid(b=True)
    ax.legend(names, loc='best')

    if ylim:
        ax.set_ylim(ylim)

    if logy:
        ax.set_yscale('log')

    if inverty:
        ax.invert_yaxis()

    ax.set_ylabel(ylabel)

    if xlim:
        ax.set_xlim(xlim)

    if logx:
        ax.set_xscale('log')

    ax.set_xlabel(xlabel)

    return ax
