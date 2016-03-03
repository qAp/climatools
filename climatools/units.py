


def hybrid2mbar(ds):
    '''
    Get level and layer pressures by converting
    from hybrid coordinates.
    INPUT:
    ds --- xray.Dataset containing hybrid layer and level coordinates
    OUTPUT:
    ds --- same as input but with additional coordinate variables,
           pressure and ipressure, for layer pressure
           and level pressure, respectively. Both are in milibars.
    '''
    if 'lev' in ds:
        layer_pressure = 1e-2 * (ds['hyam'] * ds['P0'] + ds['hybm'] * ds['PS'])
        ds.coords['pressure'] = (layer_pressure.dims, layer_pressure)
        ds.coords['pressure']\
            .attrs.update({'units': 'mbar',
                           'long_name': 'pressure at mid-points',
                           'formula': 'hyam * P0 + hybm * PS'})        

    if 'ilev' in ds:
        level_pressure = 1e-2 * (ds['hyai'] * ds['P0'] + ds['hybi'] * ds['PS'])
        ds.coords['ipressure'] = (level_pressure.dims, level_pressure)
        ds.coords['ipressure']\
            .attrs.update({'units': 'mbar',
                           'long_name': 'pressure at interfaces',
                           'formula': 'hyai * P0 + hybi * PS'})
    return ds




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


def wavenumber_to_nanometres(v):
    '''
    Convert cm-1 to nm
    '''
    return 10**7 / v
