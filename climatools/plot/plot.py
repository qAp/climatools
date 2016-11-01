


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
        
        if ax is None:
            ax = plt.gca()
            
        xlabel, x = list(darray.indexes.items())[0]

        y = darray
        if darray.name is not None:
            ylabel = darray.name
        else:
            ylabel = None

        index_on_yaxis = kwargs.pop('index_on_yaxis', False)
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

        return primitive
        
