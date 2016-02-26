import os
import itertools
import collections
import pandas as pd


'''
INPUT_RRTM records
'''


def record_1_1(CXID = None):
    '''Returns 80 characters of user identification'''
    L = 80
    if CXID and len(CXID) > 78:
        raise InputError('User identification\
        cannot be longer than 78.')
    return '{0:2}{1:78}'.format('$ ', CXID or '')


def record_1_2(IAER = None,
               IATM = None,
               ISCAT = None,
               ISTRM = None,
               IOUT = None,
               IMCA = None,
               ICLD = None,
               IDELM = None,
               ICOS = None):
    notes = ((18, None, None),
             (2, '{:>2d}', IAER),
             (29, None, None),
             (1, '{:1d}', IATM),
             (32, None, None),
             (1, '{:1d}', ISCAT),
             (1, None, None),
             (1, '{:1d}', ISTRM),
             (2, None, None),
             (3, '{:>3d}', IOUT),
             (3, None, None),
             (1, '{:1d}', IMCA),
             (1, '{:d}', ICLD),
             (3, None, None),
             (1, '{:1d}', IDELM),
             (1, '{:1d}', ICOS))
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_1_2_1(JULDAT = None,
                 SZA = None,
                 ISOLVAR = None,
                 SOLVAR = None):
    notes = tuple([(12, None, None),
                   (3, '{:>3d}', JULDAT),
                   (3, None, None),
                   (7, '{:>7.4f}', SZA),
                   (4, None, None),
                   (1, None, None)] + 
                  [(5, '{:>5.3f}', sv) for sv in SOLVAR or 14 * [None]])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_1_4(IEMIS = None,
               IREFLECT = None,
               SEMISS = None):
    notes = tuple([(11, None, None),
                   (1, '{:d}', IEMIS),
                   (2, None, None),
                   (1, '{:d}', IREFLECT)] +
                  [(5, '{:>5.3f}', sm) for sm in SEMISS or 14 * [None]])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_3_1(MODEL = None,
               IBMAX = None,
               NOPRNT = None,
               NMOL = None,
               IPUNCH = None,
               MUNITS = None,
               RE = None,
               CO2MX = None,
               REF_LAT = None):
    notes = (
        (5, '{:>5d}', MODEL),
        (5, None, None),
        (5, '{:>5d}', IBMAX),
        (5, None, None),
        (5, '{:>5d}', NOPRNT),
        (5, '{:>5d}', NMOL),
        (5, '{:>5d}', IPUNCH),
        (3, None, None),
        (2, '{:>2d}', MUNITS),
        (10, '{:>10.3f}', RE),
        (20, None, None),
        (10, '{:10.3f}', CO2MX)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_2(HBOUND = None,
               HTOA = None):
    notes = (
        (10, '{:>10.3f}', HBOUND),
        (10, '{:>10.3f}', HTOA)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_3_A(AVTRAT = None,
                 TDIFF1 = None,
                 TDIFF2 = None,
                 ALTD1 = None,
                 ALTD2 = None):
    notes = tuple((10, '{:10.3f}', value) \
                  for value in [AVTRAT, TDIFF1, TDIFF2, ALTD1, ALTD2])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_3_3_B(IBMAX = None,
                 PATH_atmpro = None):
    Nrow, fmtspec = 8, '{:>10.3f}'
    with pd.get_store(PATH_atmpro) as store:
        atmpro = store['atmpro']
    if IBMAX < 0:
        name = 'pressure'
    elif IBMAX > 0:
        name = 'altitude'
    else:
        raise ValueError('record_3_3_B is not applicable for IMBAX = 0')
    totdata = atmpro[name][::-1][: abs(IBMAX)]
    notes_rows = (
        ((Nrow, fmtspec, value) for value in row) \
        for row in itertools.zip_longest(*(Nrow * [iter(totdata)]))
        )
    records_rows = (''.join(length * ' ' if value == None\
                            else fmtspec.format(value)\
                            for length, fmtspec, value in notes) \
                            for notes in notes_rows)
    return '\n'.join(records_rows)


def record_3_4(IMMAX = None,
               HMOD = None):
    notes = (
        (5, '{:>5d}', IMMAX),
        (24, '{:>24s}', HMOD)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_5(NMOL = None,
               ZM = None,
               PM = None,
               TM = None,
               JCHARP = None,
               JCHART = None,
               JCHAR = None):
    notes = tuple([
        (10, '{:>10.3e}', ZM),
        (10, '{:>10.3e}', PM),
        (10, '{:>10.3e}', TM),
        (5, None, None),
        (1, '{:s}', JCHARP),
        (1, '{:s}', JCHART),
        (3, None, None)] + \
                  [(1, '{:s}', jch) for jch in JCHAR or NMOL * [None]])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_3_6(NMOL = None,
               VMOL = None):
    if VMOL.shape and len(VMOL) != NMOL:
        raise InputError('NMOL = {}. \
        VMOL must have {} values'.format(NMOL, NMOL))
    notes = tuple((10, '{:>10.3e}', value) for value in VMOL)
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_5_to_3_6s(NMOL = None,
                       IMMAX = None,
                       PATH_atmpro = None):
    with pd.get_store(PATH_atmpro) as store:
        atmpro = store['atmpro'].sort_index(ascending = True)
        
    lines = collections.deque([])
    for indx in atmpro.index[: abs(IMMAX)]:
        lines.append(
            record_3_5(ZM = atmpro.loc[indx, 'altitude'],
                       PM = atmpro.loc[indx, 'pressure'],
                       TM = atmpro.loc[indx, 'temperature'],
                       JCHARP = 'A',
                       JCHART = 'A',
                       JCHAR = NMOL * ['A'])
                                                            )
        lines.append(
            record_3_6(NMOL = NMOL,
                       VMOL = atmpro.ix[indx, 3:])
            )
    return '\n'.join(lines)



def write_input_rrtm(ds=None, time=181, lat=-90, lon=0, aerosol=False):
    '''
    Writes INPUT_RRTM file for a column in ds.
    INPUT:
    ds --- xarray.Dataset, dataset containing all required variables
           for RRTMG-SW column model, for all time, latitude and longitude
    time --- time label of the column. [number of years after the initial time]
    lat --- latitude of the column. [degrees]
    lon --- longigutde of the column. [degrees]
    aerosol --- True or False.  True to include aerosol effects
    '''
    content = collections.deque([])

    # record 1.1
    cxid = 'CXID'
    content.append(record_1_1(CXID=cxid))

    # record 1.2
    iaer = 0
    iatm = 1
    iscat = 1
    istrm = None
    iout = 98
    imca = 0
    icld = 0
    idelm = 0
    content.append(record_1_2(IAER=iaer,
                              IATM=iatm,
                              ISCAT=iscat,
                              ISTRM=istrm,
                              IOUT=iout,
                              IMCA=imca,
                              ICLD=icld,
                              IDELM=idelm,
                              ICOS=icos))

    # record 1.2.1
    juldat = None
    sza = 60.
    isolvar = 0.
    solvar = None
    content.append(record_1_2_1(JULDAT=juldat,
                                SZA=sza,
                                ISOLVAR=isolvar,
                                SOLVAR=solvar))

    # record 1.4
    iemis = 0
    ireflect = 0
    semiss = None
    content.append(record_1_4(IEMIS=iemis,
                              IREFLECT=ireflect,
                              SEMISS=semiss))
    
    if IATM == 0:
        raise ValueError('Sorry, IATM=0 option is currently not implemented.')
        # record 2.1
        iform = None
        nlayrs = None
        nmol = None
        content.append(record_2_1(IFORM=iform,
                                  NLAYRS=nlayrs,
                                  NMOL=nmol))
        # record 2.1.1 to 2.1.3
        content.append(record_2_1_1to3(ds=ds))

    if IATM == 1:
        # record 3.1
        model = 0
        ibmax = - ds.dims[ilev]
        noprnt = 0
        nmol = 7
        ipunch = 0
        munits = None
        re = None
        co2mx = None
        ref_lat = None
        content.append(record_3_1(MODEL=model,
                                  IBMAX=ibmax,
                                  NOPRNT=noprnt,
                                  NMOL=nmol,
                                  IPUNCH=ipunch,
                                  MUNITS=munits,
                                  RE=re,
                                  CO2MX=co2mx,
                                  REF_LAT=ref_lat))

        # record 3.2
        hbound = 1e-2 * ds['PS'].sel(time=time, lat=lat, lon=lon)
        htoa = ds['level_pressure'].isel(ilev=0)
        content.append(record_3_2(HBOUND=hbound, HTOA=htoa))
            
        if IBMAX == 0:
            # record 3.3
            avtrat = None
            tdiff1 = None
            tdiff2 = None
            altd1 = None
            altd2 = None
            conent.append(record_3_3_A(AVTRAT=avtrat,
                                       TDIFF1=tdiff1,
                                       TDIFF2=tdiff2,
                                       ALTD1=altd1,
                                       ALTD2=altd2))
            
        else:
            # record 3.3.B
            content.append(record_3_3_B(IBMAX=ibmax, ds=ds))
            
        if MODEL == 0:
            # record 3.4
            immax = - ds.dims['ilev']
            hmod = '(lat,lon) = ({}, {})'.format(lat, lon)
            content.append(record_3_4(IMMAX=immax, HMOD=hmod))

            # record 3.5 to 3.6
            content.append(
                record_3_5_to_3_6s(NMOL=nmol, IMMAX=immax, ds=ds))
            
    with open('INPUT_RRTM', mode='w', encoding='utf-8') as file:
        file.write('\n'.join(content))
    
        
def write_in_aer_rrtm(ds, time=181, lat=-90, lon=0):
    '''
    Writes IN_AER_RRTM file for a column in ds.
    INPUT:
    ds --- xarray.Dataset, dataset containing all required variables
           for RRTMG-SW column model; to take into account of aerosol effects,
           , and for all times, latitudes and longitudes
    time --- time label of the column. [number of years after the initial time]
    lat --- latitude of the column. [degrees]
    lon --- longigutde of the column. [degrees]
    '''
    content = collections.deque([])
    
    # record A1.1
    naer=1
    content.append(record_a1_1(naer=1))
    
    # record A2.1
    nlay = ds.dims['lev']
    iaod = 1
    issa = 1
    ipha = 1
    content.append(record_a2_1(nlay=nlay,
                               iaod=iaod,
                               issa=issa,
                               ipha=ipha))
    
    # record A2.1.1 for all layers
    for lev in ds.coords['lev']:
        lay = lev2lay(lev)
        aod = ds['tauxar'].sel(time=time, lat=lat, lon=lon, lev=lev)
        content.append(record_a2_1_1(lay=lay, aod=aod))
        
    # record A2.2
    ssa = ds['wa'].sel(time=time, lat=lat, lon=lon)
    content.append(record_a2_2(ssa=ssa))
    
    # record A2.3
    phase = ds['ga'].sel(time=time, lat=lat, lon=lon)
    content.append(record_a2_3(phase=phase))

    with open('IN_AER_RRTM', mode='w', encoding='utf-8') as file:
        file.write('\n'.join(content))

        
def write_sw_inputfiles(ds, time=181, lat=-90, lon=0, aerosol=False):
    '''
    Writes INPUT_RRTM and/or IN_AER_RRTM files for a column in ds.
    INPUT:
    ds --- xarray.Dataset, dataset containing all required variables
           for RRTMG-SW column model; to take into account of aerosol effects,
           , and for all times, latitudes and longitudes
    time --- time label of the column. [number of years after the initial time]
    lat --- latitude of the column. [degrees]
    lon --- longigutde of the column. [degrees]
    aerosol --- True or False.  True to include aerosol effects,
                hence writing out IN_AER_RRTM in addition to INPUT_RRTM.
    '''
    write_input_rrtm(ds, time=time, lat=lat, lon=lon, aerosol=aerosol)
    if aerosol:
        write_in_aer_rrtm(ds, time=time, lat=lat, lon=lon)

