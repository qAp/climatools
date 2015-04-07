


def lev_hybrid2mbar(ds):
    '''
    returns xray DataArray of levels in mbar
    INPUT:
    ds --- xray Dataset from .nc open_dataset()
    '''
    p = 1e-2 * (ds['hyam'] * ds['P0'] + ds['hybm'] * ds['PS'])
    p.attrs['units'] = 'mbar'
    return p[{'time': 0, 'lat': 0, 'lon': 0}]
