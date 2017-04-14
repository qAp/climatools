



import scipy.interpolate as interpolate
import xarray as xr




def get_interpfunc(da=None, dim='time',
                   bounds_error=False, fill_value='extrapolate'):
    '''
    Linearly interpolates `da` along dimension `dim`.  This function
    returns a function that evaluates `da` at a set of values along
    dimension `dim`.

    Parameters
    ----------
    da : xarray.DataArray
    dim : string
          name of dimension to interpolate along
    '''
    
    x = da.coords[dim]
    y = da.values
    axis = da.dims.index(dim)
    func = interpolate.interp1d(x=x, y=y, axis=axis,
                                bounds_error=bounds_error,
                                fill_value=fill_value)

    def callf(coords=None, name_dim=None):
        data = func(coords)

        dims_interp = list(da.dims)
        coords_interp = [coords if d == dim else da.coords[d]
                         for d in dims_interp]

        if name_dim:
            dims_interp[dims_interp.index(dim)] = name_dim
        
        da_interp = xr.DataArray(data,
                                 dims=dims_interp, coords=coords_interp,
                                 attrs=da.attrs)
        return da_interp
    
    return callf



def interp_layers2levels(ds, vars=None):
    '''
    Interpolate layer values to levels.
    
    Args:
        ds: xarray.Dataset
        vars: list of variables in `ds` for which layers values are to be
              interpolated onto levels. Defaults to an empty list.
    Returns:
        ds: xarray.Dataset, with new variable for the level values added
            for each variable in `vars`
    '''
    if not vars:
        vars = []
        
    for var in vars:
        try:
            da = ds[var]
        except KeyError:
            continue
        else:
            interpfunc = get_interpfunc(da, dim='lev')
            da_interp = interpfunc(coords=ds.coords['ilev'],
                                   name_dim='ilev')
            ds['i' + var] = (da_interp.dims, da_interp, da_interp.attrs)
    return ds
