


import numpy as np

import xarray as xr


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
            plt.gcf().autofmt_xdate()

        # Rotate dates on ylabels
        if np.issubdtype(y.dtype, np.datetime64):
            plt.gcf().autofmt_xdate()

        if grid:
            ax.grid(b=grid)

        if 'label' in kwargs:
            ax.legend(loc='best')
        
        return primitive
        
