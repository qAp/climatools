



def wavenumber_bands(region = 'sw'):
    '''
    Returns wavenumber bands used by CLIRAD
    Units: cm-1
    '''
    d = {}
    if region == 'sw':
        d[1] = [(35088, 44444),]
        d[2] = [(33333, 35088), (44444, 57142),]
        d[3] = [(30770, 33333),]
        d[4] = [(25000, 30770),]
        d[5] = [(14286, 25000),]
        d[6] = [(8200, 14280),]
        d[7] = [(4400, 8200),]
        d[8] = [(1000, 4400)]
    elif region == 'lw':
        d[1] = [(0, 340),]          #  h2o
        d[2] = [(340, 540),]        #  h2o
        d[3] = [(540, 800),]        #  h2o,cont,co2
        d[4] = [(800, 980),]        #  h2o,cont,  co2,f11,f12,f22
        d[5] = [(980, 1100),]       #  h2o,cont,o3
        #  co2,f11
        d[6] = [(1100, 1215),]      #    h2o,cont
        #        c                              n2o,ch4,f12,f22
        d[7] = [(1215, 1380),]      #  h2o,cont
        #        c                              n2o,ch4
        d[8] = [(1380, 1900),]      #    h2o
        d[9] = [(1900, 3000),]      #    h2o
        #        c
        #        c In addition, a narrow band in the 17 micrometer region (Band 10) is added
        #        c    to compute flux reduction due to n2o
        #        c
        d[10] = [(540, 620)]       # h2o,cont,co2,n2o
    else:
        raise ValueError('region must be either sw for shortwave, or lw for longwave')
    return d



def midband_wavenumbers(region = 'sw'):
    '''
    Returns the wavenumber in the middle of each spectral band
    Units: cm^{-1}
    '''
    wavebands = wavenumber_bands(region = 'sw')
    midband_numbers = [.5 * sum(limit) for iband, limits in wavebands.items() \
                       for limit in limits]
    return sorted(midband_numbers)





    
