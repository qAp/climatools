


def hybrid2mbar(ds, level_type = 'lev'):
    '''
    returns xray DataArray of levels in mbar
    INPUT:
    ds --- xray Dataset from .nc open_dataset()
    level_type --- \'lev\' for layer(level) pressure
                   \'ilev\' for level(interface) pressure
    '''
    if level_type == 'lev':
        p = 1e-2 * (ds['hyam'] * ds['P0'] + ds['hybm'] * ds['PS'])
    elif level_type == 'ilev':
        p = 1e-2 * (ds['hyai'] * ds['P0'] + ds['hybi'] * ds['PS'])
    p.attrs['units'] = 'mbar'
    return p[{'time': 0, 'lat': 0, 'lon': 0}]
