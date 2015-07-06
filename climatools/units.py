


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


def convert_units(datasets, ilev, lev, datetimes):
    '''
    Convert units for certain fields for all cases in DATASETS.
    INPUT:
    datasets --- dictionary of xray Datasets some of whose variables\' units
                 are to be converted
    ilev --- level(interface) pressure in mbar
    lev  --- layer(level) pressure in mbar
    datetimes --- time in pandas DatetimeIndex objects
    OUTPUT:
    datasets -- same as in INPUT, after unit conversion
    NOTES:

    '''
    for name, ds in datasets.items():
        ds.coords['ilev'] = ('ilev', ilev, {'units': 'mbar'})
        ds.coords['lev'] = ('lev', lev, {'units': 'mbar'})
        ds.coords['time'] = ('time', datetimes, {'units': 'datetime'})
        
        for k in ['TOT_CLD_VISTAU',]:
            if k in ds:
                pass #ds[k].values[ds[k].isnull().values] = - 0.
            
        for k in ['FUS', 'FDS', 'net_FS', 'net_FSC']:
            if k in ds:
                ds[k] *= 1e3
                
        for k in ['QRL', 'QRS', 'DTCOND']:
            if k in ds:
                ds[k] *= 86400
                ds[k].attrs['units'] = 'K/day'
                
        for k in ['Q', ]:
            if k in ds:
                ds[k] *= 1e3
                ds[k].attrs['units'] = 'g/kg'
                
        for k in ['CLDICE', 'CLDLIQ', 'AQSNOW']:
            if k in ds:
                ds[k] *= 1e6
                ds[k].attrs['units'] = 'mg/kg'
    return datasets
