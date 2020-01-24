import xarray as xr



def load_camhistory(readfrom=None):
    with xr.open_dataset(readfrom, decode_cf=False) as ds:
        return ds.copy(deep = True)
