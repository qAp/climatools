# Collection of routines for processing and visualising data related to climate modelling

Often the data output from climate models are stored in netCDF or HDF files.  This library uses
[xray][xray] to import and manipulate these data, 
and [matplotlib][matplotlib] module to make various different types of plots of these data.
The time dimension of these data is handled by using Pandas's datetime objects.

Examples of usage can be found in most of the IPython notebooks [here][scam_notebooks], where the data
are from runs of the Single-column Community Atmosphere Model ([SCAM][scam]).  

# Some highlights
## Loading output data from offline radiation models
## Conveniently plot one-dimensional `xarray.DataArray`
The `.climaviz.plot` method can now be supplied with keyword arguments to adjust the axes' scales and directions, to indicate that the index values are to be plotted on the y-axis instead of on the x-axis, and to constrain the variable's axis' limits based on variable values over a specified range on the index's axis.
```
import numpy as np
import xarray as xr
import matplotlib 
import matplotlib.pyplot as plt
import climatools.plot.plot

x = np.linspace(-30, 30, 1000)
y = .02 * (x - 3) * (x - 7) * (x + 20) + 30 * np.sin(x) + 300
y1 = .05 * (x - 5) * (x + 5) * np.cos(x) + 40

da = xr.DataArray(data=y, dims=['x'], coords=[x], name='y')
da1 = xr.DataArray(data=y1, dims=['x'], coords=[x], name='y')

# plot the index on the y-axis
da.climaviz.plot(index_on_yaxis=True, figsize=(5, 7))
da1.climaviz.plot(index_on_yaxis=True, xscale='log', yincrease=False)
```
![1d plot example]
(https://github.com/qAp/climatools/blob/xarray_accessor/climatools/examples/1d_plotting/1dplot_example.png)

## Optimized axes ticks and labels for time labeals
## Optimized color bars for two-dimensional contour plots



[scam_notebooks]: http://nbviewer.ipython.org/github/qAp/SCAM_radiation_notebooks/tree/master/
[xray]: http://xray.readthedocs.org/en/stable/
[matplotlib]: http://matplotlib.org/
[scam]: http://www.cesm.ucar.edu/models/atm-cam/
