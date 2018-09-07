
import numpy as np
import pandas as pd

import xarray as xr



from bokeh.plotting import figure
from bokeh.models import Range1d, Legend, ColumnDataSource, FactorRange

from bokeh.transform import factor_cmap

from ..viz import set_xaxis_datetime_ticklocs_ticklabels






@xr.register_dataarray_accessor('climaviz')
class ClimavizArrayAccessor(object):
    def __init__(self, xarray_da):
        self._obj = xarray_da
        
    def plot(self, *args, **kwargs):
        """
        Line plot of 1 dimensional DataArray index against values
        
        Wraps matplotlib.pyplot.plot
        
        Parameters
        ----------
        darray : DataArray
        Must be 1 dimensional
        ax : matplotlib axes, optional
        If not passed, uses the current axis
        *args, **kwargs : optional
        Additional arguments to matplotlib.pyplot.plot
        
        """
        import matplotlib.pyplot as plt

        darray = self._obj
        
        ndims = len(darray.dims)
        if ndims != 1:
            raise ValueError('Line plots are for 1 dimensional DataArrays. '
                             'Passed DataArray has {ndims} '
                             'dimensions'.format(ndims=ndims))
        
        # Ensures consistency with .plot method
        ax = kwargs.pop('ax', None)
        figsize = kwargs.pop('figsize', None)

        if ax is None:
            ax = plt.gca()
            if figsize:
                plt.gcf().set_size_inches(*figsize)

        # Unpack keyword arguments that will not be accepted by pyplot.plot
        xincrease = kwargs.pop('xincrease', None)
        yincrease = kwargs.pop('yincrease', None)

        xscale = kwargs.pop('xscale', None)
        yscale = kwargs.pop('yscale', None)

        grid = kwargs.pop('grid', None)

        index_on_yaxis = kwargs.pop('index_on_yaxis', False)

        varlim_from_indexrange = kwargs.pop('varlim_from_indexrange', None)

        # map DataArray values and index to x and y, or vice versa.
        xlabel, x = list(darray.indexes.items())[0]
        y = darray
        
        if darray.name is not None:
            ylabel = darray.name
        else:
            ylabel = None

        if index_on_yaxis:
            xlabel, ylabel = ylabel, xlabel
            x, y = y, x

        # set, or update, y-axis scale and limits
        if not index_on_yaxis:
            if varlim_from_indexrange == None:
                yslice = y
            else:
                yslice = y.loc[slice(*varlim_from_indexrange)]
        else:
            yslice = y

        if ax.lines:
            ylim_bot, ylim_top = list(ax.get_ylim())
            lims = [ylim_bot, ylim_top, yslice.min(), yslice.max()]
            ymin, ymax = min(lims), max(lims)
        else:
            ymin, ymax = yslice.min(), yslice.max()

        if ymin == ymax:
            ymin -= .06
            ymax += .06

        if yscale == 'linear':
            ax.set_yscale('linear')
            ax.yaxis.get_major_formatter().set_powerlimits((0, 1))
        elif yscale == 'log':
            if ymax <= 0:
                raise ValueError('Warning: yaxis. Max value to be plotted '
                                 'needs to be greater than zero '
                                 'in order to axis set to log scale.')
            elif ymin <= 0:
                print('Warning: yaxis. Min value to be plotted '
                      'is less or equal to zero. This part will be '
                      'omitted on a log scale.')
                ax.set_yscale('log')
            else:
                ax.set_yscale('log')
        else:
            if ax.get_yscale() == 'log':
                if ymin <= 0:
                    print('Warning: yaxis. Min value to be plotted '
                          'is less or equal to zero. This part will be '
                          'omitted on the exisitng log scale.'
                          'Consider using linear scale instead.')
            else:
                ax.yaxis.get_major_formatter().set_powerlimits((0, 1))

        if yincrease == True:
            ax.set_ylim(bottom=ymin, top=ymax)
        elif yincrease == False:
            ax.set_ylim(bottom=ymax, top=ymin)
        else:
            if ax.lines:
                if ylim_bot < ylim_top:
                    ax.set_ylim(bottom=ymin, top=ymax)
                else:
                    ax.set_ylim(bottom=ymax, top=ymin)
            else:
                ax.set_ylim(bottom=ymin, top=ymax)


        
        # set, or update, x-axis scale and limits
        if index_on_yaxis:
            if varlim_from_indexrange == None:
                xslice = x
            else:
                xslice = x.loc[slice(*varlim_from_indexrange)]
        else:
            xslice = x
                
        if ax.lines:
            xlim_left, xlim_right = list(ax.get_xlim())
            lims = [xlim_left, xlim_right, xslice.min(), xslice.max()]
            xmin, xmax = min(lims), max(lims)
        else:
            xmin, xmax = xslice.min(), xslice.max()

        if xmin == xmax:
            xmin -= .06
            xmax += .06

        if xscale == 'linear':
            ax.set_xscale('linear')
            ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
        elif xscale == 'log':
            if xmax <= 0:
                raise ValueError('Warning: xaxis. Max value to be plotted '
                                 'needs to be greater than zero '
                                 'in order to axis set to log scale.')
            elif xmin <= 0:
                print('Warning: xaxis. Min value to be plotted '
                      'is less or equal to zero. This part will be '
                      'omitted on a log scale.')
                ax.set_xscale('log')
            else:
                ax.set_xscale('log')
        else:
            if ax.get_xscale() == 'log':
                if xmin <= 0:
                    print('Warning: xaxis. Min value to be plotted '
                          'is less or equal to zero. This part will be '
                          'omitted on the exisitng log scale.'
                          'Consider using linear scale instead.')
            else:
                ax.xaxis.get_major_formatter().set_powerlimits((0, 1))

        if xincrease == True:
            ax.set_xlim(left=xmin, right=xmax)
        elif xincrease == False:
            ax.set_xlim(left=xmax, right=xmin)
        else:
            if ax.lines:
                if xlim_left < xlim_right:
                    ax.set_xlim(left=xmin, right=xmax)
                else:
                    ax.set_xlim(left=xmax, right=xmin)
            else:
                ax.set_xlim(left=xmin, right=xmax)


        # make the line plot: x against y
        primitive = ax.plot(x, y, *args, **kwargs)

        ax.set_title(darray._title_for_slice())
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)

        # Rotate dates on xlabels
        if np.issubdtype(x.dtype, np.datetime64):
            if index_on_yaxis:
                dtnss = x.values
            else:
                dtnss = x
            timestamps = [pd.Timestamp(dtns).to_datetime() for dtns in dtnss]
            duration = pd.Timedelta(timestamps[-1] - timestamps[0])
            set_xaxis_datetime_ticklocs_ticklabels(ax.xaxis, duration=duration)

        # Rotate dates on ylabels
        if np.issubdtype(y.dtype, np.datetime64):
            if index_on_yaxis:
                dtnss = y
            else:
                dtnss = y.values
            timestamps = [pd.Timestamp(dtns).to_datetime() for dtns in dtnss]
            duration = pd.Timedelta(timestamps[-1] - timestamps[0])
            set_xaxis_datetime_ticklocs_ticklabels(ax.yaxis, duration=duration)

        if grid:
            ax.grid(b=grid)

        if 'label' in kwargs:
            ax.legend(loc='best')
        
        return primitive



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
    p: bokeh.plotting.figure
        Plotted figure.
    '''
    ymin = 1e-2 
    ymax = 1020
    
    p = figure(y_axis_type=y_axis_type, plot_width=300)
    xmin, xmax = nice_xlims(pltdata, prange=prange)
    
    rs = []
    for d in pltdata:
        rd = []
        if 'marker' in d:
            r_mark = getattr(p, d['marker'])(d['srs'].values, 
                        d['srs'].coords['pressure'].values,
                        color=d['color'], alpha=.7)
            rd.append(r_mark)
        r_line = p.line(d['srs'].values, 
                         d['srs'].coords['pressure'].values,
                         color=d['color'], alpha=d['alpha'], 
                         line_width=d['line_width'], 
                         line_dash=d['line_dash'])
        rd.append(r_line)
      
        rs.append(rd)
        
    p.y_range = Range1d(ymax, ymin)  
    p.yaxis.axis_label = 'pressure [mb]'
    
    p.x_range = Range1d(xmin, xmax)
    p.xaxis.axis_label = 'cooling rate [K/day]'
    
    items = [(d['label'], r) for r, d in zip(rs, pltdata)]
    legend = Legend(items=items, location=(10, 0))
    legend.label_text_font_size = '8pt'
    p.add_layout(legend, 'above')
    p.legend.orientation = 'horizontal'
    p.legend.location = 'top_center'
    return p


        
