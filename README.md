# Collection of routines for processing and visualising data output from climate models

Often the data output from climate models are stored in netCDF or HDF files.  This library uses
[xray][xray] to import and manipulate these data, 
and [matplotlib][matplotlib] module to make various different types of plots of these data.

Examples of usage can be found in most of the [IPython][ipython] notebooks here, where the data
are from runs of the Single-column Community Atmosphere Model ([SCAM][scam]).


[xray]: http://xray.readthedocs.org/en/stable/
[matplotlib]: http://matplotlib.org/
[scam]: http://www.cesm.ucar.edu/models/atm-cam/