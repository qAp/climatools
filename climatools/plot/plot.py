


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
            
        #_ensure_plottable([x])
        
        primitive = ax.plot(x, darray, *args, **kwargs)
        
        ax.set_xlabel(xlabel)
        ax.set_title(darray._title_for_slice())
        
        if darray.name is not None:
            ax.set_ylabel(darray.name)

        # Rotate dates on xlabels
        if np.issubdtype(x.dtype, np.datetime64):
            plt.gcf().autofmt_xdate()

        return primitive
        
