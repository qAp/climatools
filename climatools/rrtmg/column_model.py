import os
import itertools
import collections
import functools

import pandas as pd





def write_record_string(func):
    @functools.wraps(func)
    def callf(*args, **kwargs):
        notes = func(*args, **kwargs)
        return ''.join(length * ' ' if value == None
                       else fmtspec.format(value)
                       for length, fmtspec, value in notes)
    return callf


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


@write_record_string
def record_1_2(IAER = None,
               IATM = None,
               ISCAT = None,
               ISTRM = None,
               IOUT = None,
               IMCA = None,
               ICLD = None,
               IDELM = None,
               ICOS = None):
    return ((18, None, None),
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


@write_record_string
def record_1_2_1(JULDAT = None,
                 SZA = None,
                 ISOLVAR = None,
                 SOLVAR = None):
    return tuple([(12, None, None),
                  (3, '{:>3d}', JULDAT),
                  (3, None, None),
                  (7, '{:>7.4f}', SZA),
                  (4, None, None),
                  (1, None, None)] + 
                 [(5, '{:>5.3f}', sv) for sv in SOLVAR or 14 * [None]])


@write_record_string
def record_1_4(IEMIS = None,
               IREFLECT = None,
               SEMISS = None):
    return tuple([(11, None, None),
                  (1, '{:d}', IEMIS),
                  (2, None, None),
                  (1, '{:d}', IREFLECT)] +
                 [(5, '{:>5.3f}', sm) for sm in SEMISS or 14 * [None]])


@write_record_string
def record_3_1(MODEL = None,
               IBMAX = None,
               NOPRNT = None,
               NMOL = None,
               IPUNCH = None,
               MUNITS = None,
               RE = None,
               CO2MX = None,
               REF_LAT = None):
    return ((5, '{:>5d}', MODEL),
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
            (10, '{:10.3f}', CO2MX))


@write_record_string
def record_3_2(HBOUND = None,
               HTOA = None):
    return ((10, '{:>10.3f}', float(HBOUND)),
            (10, '{:>10.3f}', float(HTOA)))


@write_record_string
def record_3_3_A(AVTRAT = None,
                 TDIFF1 = None,
                 TDIFF2 = None,
                 ALTD1 = None,
                 ALTD2 = None):
    return tuple((10, '{:10.3f}', value)
                 for value in [AVTRAT, TDIFF1, TDIFF2, ALTD1, ALTD2])


def record_3_3_B(ds=None, IBMAX=None,
                 time=None, lat=None, lon=None):
    Nrow, fmtspec = 8, '{:>10.3f}'

    if IBMAX < 0:
        name = 'ipressure'
    elif IBMAX > 0:
        name = 'altitude'
    else:
        raise ValueError('record_3_3_B is not applicable for IMBAX = 0')
    
    totdata = (ds[name]
               .sel(time=time, lat=lat, lon=lon)[::-1][: abs(IBMAX)].values)

    notes_rows = (
        ((Nrow, fmtspec, value) for value in row) 
        for row in itertools.zip_longest(*(Nrow * [iter(totdata)]))
        )
    records_rows = (''.join(length * ' ' if value == None\
                            else fmtspec.format(value)\
                            for length, fmtspec, value in notes) \
                            for notes in notes_rows)
    return '\n'.join(records_rows)


@write_record_string
def record_3_4(IMMAX = None,
               HMOD = None):
    return ((5, '{:>5d}', IMMAX),
            (24, '{:>24s}', HMOD))


def record_3_5(nmol=None,
               zm=0, pm=0, tm=0,
               jcharp='A', jchart='A',
               jchar_h2o='A', jchar_co2='A', jchar_o3='A', jchar_n2o='A',
               jchar_co='A', jchar_ch4='A', jchar_o2='A'):
    '''
    Parameters
    ----------
    nmol: number of gases/molecules from the beginning of the molecules
          list in the documentation
    zm: altitude
    pm: pressure. units need to be consistent with `jcharp`
    tm: temperature. units need to be consistent with `jchart`
    jcharp: units tag for pressure
    jchart: units tag for temperature
    jchar_h2o: units tag for h2o concentration specified in record 3.6
    jchar_co2: same meaning as for `jchar_h2o`
    '''
    maxlist_jchars = [jchar_h2o, jchar_co2, jchar_o3, jchar_n2o,
                      jchar_co, jchar_ch4, jchar_o2]

    list_jchars = maxlist_jchars[:nmol]

    notes = tuple([
        (10, '{:>10.3e}', zm),
        (10, '{:>10.3e}', pm),
        (10, '{:>10.3e}', tm),
        (5, None, None),
        (1, '{:s}', jcharp),
        (1, '{:s}', jchart),
        (3, None, None)] + [(1, '{:s}', jch) for jch in list_jchars])
    
    try:
        return ''.join(length * ' ' if value is None
                       else fmtspec.format(value)
                       for length, fmtspec, value in notes)
    except TypeError:
        zm = float(zm)
        pm = float(pm)
        tm = float(tm)

        notes = tuple([
            (10, '{:>10.3e}', zm),
            (10, '{:>10.3e}', pm),
            (10, '{:>10.3e}', tm),
            (5, None, None),
            (1, '{:s}', jcharp),
            (1, '{:s}', jchart),
            (3, None, None)]
        + [(1, '{:s}', jch) for jch in list_jchars])
        
        return ''.join(length * ' ' if value is None
                       else fmtspec.format(value)
                       for length, fmtspec, value in notes)


def record_3_6(nmol=None,
               h2o=0, co2=0, o3=0, n2o=0, co=0, ch4=0, o2=0):
    '''
    Parameters
    ----------
    nmol: number of gases/molecules from the beginning of the
          molecules list in the documentation
    h2o: concentration of h2o. Units should be consistent with tag used
         record 3.5.
    co2: same meaning as for h2o.
    '''
    maxlist_concs = [h2o, co2, o3, n2o, co, ch4, o2]
    
    list_concs = maxlist_concs[:nmol]
    notes = tuple((10, '{:>10.3e}', value) for value in list_concs)
    try:
        return ''.join(length * ' ' if value is None
                       else fmtspec.format(value)
                       for length, fmtspec, value in notes)
    except TypeError:
        return ''.join(length * ' ' if value is None
                       else fmtspec.format(float(value))
                       for length, fmtspec, value in notes)
                       

def record_3_5_to_3_6s(ds=None, NMOL=None, IMMAX=None,
                       time=None, lat=None, lon=None):
    
    surface = dict(time=time, lat=lat, lon=lon)

    lines = collections.deque([])

    for ilev in ds.coords['ilev'].values[::-1]:
        surface_ilev = dict(ilev=ilev, **surface)
        
        record_ilev = record_3_5(nmol=NMOL,
                                 zm=0.,
                                 pm=ds['ipressure'].sel(**surface_ilev),
                                 tm=ds['iT'].sel(**surface_ilev),
                                 jcharp='A',
                                 jchart='A',
                                 jchar_h2o='C',
                                 jchar_co2='A',
                                 jchar_o3='A',
                                 jchar_n2o='A',
                                 jchar_co='A',
                                 jchar_ch4='A',
                                 jchar_o2='C')

        lines.append(record_ilev)

        record_ilev = record_3_6(nmol=NMOL,
                                 h2o=ds['iQ'].sel(**surface_ilev),
                                 co2=ds['co2vmr'],
                                 o3=ds['iO3'].sel(**surface_ilev),
                                 n2o=ds['n2ovmr'],
                                 co=0,
                                 ch4=ds['ch4vmr'],
                                 o2=ds['o2mmr'])
        
        lines.append(record_ilev)

    return '\n'.join(lines)





'''
Records for IN_AER_RRTM
'''




@write_record_string
def record_a1_1(naer=None):
    return ((5, '{:>5d}', naer),)


@write_record_string
def record_a2_1(nlay=None, iaod=None, issa=None, ipha=None):
    return ((5, '{:>5d}', nlay),
            (10, '{:>5d}', iaod),
            (15, '{:>5d}', issa),
            (20, '{:>5d}', ipha))


@write_record_string
def record_a2_1_1(iaod=None, lay=None, aod=None):
    if iaod != 1:
        raise ValueError('Sorry, only the iaod=1 option \
        is currently implemented.')

    notes = tuple([(5, '{:>5d}', lay)] +
                  [(7, '{:>7.4f}', aod_band)
                   for aod_band in aod])
    return notes


@write_record_string
def record_a2_2(issa=None, ssa=None):
    if issa != 1:
        raise ValueError('Sorry, only the issa=1 option \
        is currently implemented.')

    notes = tuple((5, '{:>5.2f}', ssa_band)
                  for ssa_band in ssa)
    return notes


@write_record_string
def record_a2_3(ipha=None, phase=None):
    if ipha != 1:
        raise ValueError('Sorry, only the ipha=1 option is currently implemented.')

    notes = tuple((5, '{:>5.2f}', phase_band)
                  for phase_band in phase)
    return notes
    

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
    iaer = 10 if aerosol else 0
    iatm = 1
    iscat = 1
    istrm = None
    iout = 98
    imca = 0
    icld = 0
    idelm = 0
    icos = 0
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
    juldat = int(ds.coords['time'].values[0] % 365)
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
    
    if iatm == 0:
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

    if iatm == 1:
        # record 3.1
        model = 0
        ibmax = - ds.dims['ilev']
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
        htoa = ds['ipressure'].sel(time=time, lat=lat, lon=lon).isel(ilev=0)
        content.append(record_3_2(HBOUND=hbound, HTOA=htoa))
            
        if ibmax == 0:
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
            content.append(record_3_3_B(ds=ds, IBMAX=ibmax,
                                        time=time, lat=lat, lon=lon))
            
        if model == 0:
            # record 3.4
            immax = - ds.dims['ilev']
            hmod = '({}, {})'.format(lat, lon)
            content.append(record_3_4(IMMAX=immax, HMOD=hmod))

            # record 3.5 to 3.6
            content.append(
                record_3_5_to_3_6s(ds=ds, NMOL=nmol, IMMAX=immax,
                                   time=time, lat=lat, lon=lon))
            
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
    for i, lev in enumerate(ds.coords['lev'][::-1]):
        lay = i + 1
        aod = 1e-22 * ds['tauxar'].sel(time=time, lat=lat, lon=lon, lev=lev).values
        content.append(record_a2_1_1(iaod=iaod, lay=lay, aod=aod))
        
    # record A2.2
    ssa = 1e-22 * ds['wa'].sel(time=time, lat=lat, lon=lon).isel(lev=0).values
    content.append(record_a2_2(issa=issa, ssa=ssa))
    
    # record A2.3
    phase = 1e-22 * ds['ga'].sel(time=time, lat=lat, lon=lon).isel(lev=0).values
    content.append(record_a2_3(ipha=ipha, phase=phase))

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


def create_rrtmg_symlink():
    path_rrtmg = '/nuwa_cluster/home/jackyu/radiation/rrtmg/SW/rrtmg_sw_v3.9/column_model/build/rrtmg_sw_v3.9_linux_pgi'
    name_link = 'rrtmg.exe'
    command = 'ln -s {source} {destination}'
    os.system(command.format(source=path_rrtmg, destination=name_link))
