


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

        xincrease = kwargs.pop('xincrease', True)
        yincrease = kwargs.pop('yincrease', True)

        xscale = kwargs.pop('xscale', None)
        yscale = kwargs.pop('yscale', None)

        grid = kwargs.pop('grid', None)

        index_on_yaxis = kwargs.pop('index_on_yaxis', False)

        varlim_from_indexrange = kwargs.pop('varlim_from_indexrange', None)

        if varlim_from_indexrange:
            darray_slice = darray.loc[slice(*varlim_from_indexrange)]
            max_tmp = darray_slice.max()
            min_tmp = darray_slice.min()

            if index_on_yaxis:
                if not ax.lines:
                    ax.set_xlim(min_tmp, max_tmp)
                else:
                    min_now, max_now = ax.get_xlim()
                    ax.set_xlim((min(min_tmp, min_now),
                                 max(max_tmp, max_now)))
            else:
                if not ax.lines:
                    ax.set_ylim(min_tmp, max_tmp)
                else:
                    min_now, max_now = ax.get_ylim()
                    ax.set_ylim((min(min_tmp, min_now),
                                 max(max_tmp, max_now)))        

        xlabel, x = list(darray.indexes.items())[0]

        y = darray
        if darray.name is not None:
            ylabel = darray.name
        else:
            ylabel = None

        if index_on_yaxis:
            xlabel, ylabel = ylabel, xlabel
            x, y = y, x
        
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

        if xincrease:
            ax.set_xlim(sorted(ax.get_xlim()))
        else:
            ax.set_xlim(sorted(ax.get_xlim(), reverse=True))

        if yincrease:
            ax.set_ylim(sorted(ax.get_ylim()))
        else:
            ax.set_ylim(sorted(ax.get_ylim(), reverse=True))

        if xscale:
            ax.set_xscale(xscale)

        if yscale:
            ax.set_yscale(yscale)

        if grid:
            ax.grid(b=grid)



        if 'label' in kwargs:
            ax.legend(loc='best')
        
        return primitive
        
