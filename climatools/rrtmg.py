



def wavenumber_bands(region = 'sw'):
    '''
    Returns wavenumber bands used by RRTMG
    Units: cm-1
    '''
    if region == 'sw':
        wavenum1 = [2600., 3250., 4000., 4650., 5150., 6150., 7700.,
                    8050.,12850.,16000.,22650.,29000.,38000.,  820.]
        wavenum2 = [3250., 4000., 4650., 5150., 6150., 7700., 8050.,
                    12850.,16000.,22650.,29000.,38000.,50000., 2600.]
    elif region == 'lw':
        wavenum1 = [10., 350., 500., 630., 700., 820.,
                    980., 1080., 1180., 1390., 1480., 1800.,
                    2080., 2250., 2390., 2600.]
        wavenum2 = [350.,  500.,  630.,  700.,  820.,  980.,
                    1080., 1180., 1390., 1480., 1800., 2080.,
                    2250., 2390., 2600., 3250.]
    else:
        raise ValueError('region must be either sw for shortwave, or lw for longwave')
    return {k + 1: [(low, high)] for k, (low, high) in enumerate(zip(wavenum1, wavenum2))}




def midband_wavenumbers(region = 'sw'):
    '''
    Returns the wavenumber in the middle of each spectral band
    Units: cm^{-1}
    '''
    wavebands = wavenumber_bands(region = region)
    midband_numbers = [.5 * sum(limit)
                       for iband, limits in wavebands.items()
                       for limit in limits]
    return sorted(midband_numbers)
        




def solar_irradiance():
    '''
    Returns the solar irradiance in each spectral band.
    Units: W m^{-2} cm
    '''
    d = {1: [12.11],
         2: [20.36],
         3: [23.73],
         4: [22.43],
         5: [55.63],
         6: [102.93],
         7: [24.29],
         8: [345.74],
         9: [218.19],
         10: [347.2],
         11: [129.49],
         12: [50.15],
         13: [3.08],
         14: [12.89]}
    return d
