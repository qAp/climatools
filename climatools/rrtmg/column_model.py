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
def record_1_2_1(juldat=None,
                 sza=None,
                 isolvar=None,
                 solvar=None):
    if juldat is not None:
        juldat = int(juldat)
    if sza is not None:
        sza = float(sza)
    if isolvar is not None:
        isolvar = float(isolvar)
    if solvar is not None:
        solvar = float(solvar)
    return tuple([(12, None, None),
                  (3, '{:>3d}', juldat),
                  (3, None, None),
                  (7, '{:>7.4f}', sza),
                  (4, None, None),
                  (1, None, None)] + 
                 [(5, '{:>5.3f}', sv) for sv in solvar or 14 * [None]])


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
def record_2_1(iform=None, nlayrs=None, nmol=None):
    '''
    Parameters
    ----------
    iform: column amount format flag. 0 or 1
           0: read read PAVE, WKL(M,L), WBROADL(L)
              in F10.4, E10.3, E10.3 formats (default)
           1: read PAVE, WKL(M,L), WBROADL(L) in E15.7 format
    nlayrs: number of layers (maximum of 200)
    nmol: value of highest molecule number used (default=7; maximum of 35)
    '''
    return ((1, None, None),
            (1, '{:d}', iform),
            (3, '{:>3d}', nlayrs),
            (5, '{:>5d}', nmol))


@write_record_string
def record_2_1_1(iform=1, is_surface_layer=False,
                 pave=None, pz_bot=None, pz_top=None,
                 tave=None, tz_bot=None, tz_top=None):
    '''
    Parameters
    ----------
    iform: column amount format flag. 0 or 1
           0: read read PAVE, WKL(M,L), WBROADL(L)
              in F10.4, E10.3, E10.3 formats (default)
           1: read PAVE, WKL(M,L), WBROADL(L) in E15.7 format
    is_surface_layer: boolean. True if current layer is
                      the surface layer
    pave: average pressure of layer [millibars]
          (**If IFORM=1, then PAVE in E15.7 format**)
    pz_bot: pressure at bottom of layer L
    pz_top: pressure at top of layer L
    tave: average temperature of layer [K]
    tz_bot: temperature at bottom of layer L
    tz_top: temperature at top of layer L
    '''
    if iform == 0:
        if is_surface_layer:
            '(3f10.4,a3,i2,1x,2(f7.2,f8.3,f7.2))'
            notes = ((10, '{:>10.4f}', float(pave)),
                     (10, '{:>10.4f}', float(tave)),
                     (10, '{:>10.4f}', 0),
                     (3, '{:>3s}', '0'),
                     (2, '{:>2d}', 0),
                     (1, None, None,),
                     (7, '{:>7.2f}', 0.),
                     (8, '{:>8.3f}', float(pz_bot)),
                     (7, '{:>7.2f}', float(tz_bot)),
                     (7, '{:>7.2f}', 0.),
                     (8, '{:>8.3f}', float(pz_top)),
                     (7, '{:>7.2f}', float(tz_top)))
        else:
            '(3f10.4,a3,i2,23x,(f7.2,f8.3,f7.2))'
            notes = ((10, '{:>10.4f}', float(pave)),
                     (10, '{:>10.4f}', float(tave)),
                     (10, '{:>10.4f}', 0),
                     (3, '{:>3s}', '0'),
                     (2, '{:>2d}', 0),
                     (23, None, None,),
                     (7, '{:>7.2f}', 0.),
                     (8, '{:>8.3f}', float(pz_top)),
                     (7, '{:>7.2f}', float(tz_top)))
            
    elif iform == 1:
        if is_surface_layer:
            '(g15.7,g10.4,g10.4,a3,i2,1x,2(g7.2,g8.3,g7.2))'
            notes = (
                (15, '{:>15.7f}', float(pave)),
                (10, '{:>10.4f}', float(tave)),
                (10, '{:>10.4f}', 0),
                (3, '{:>3s}', '0'),
                (2, '{:>2d}', 0),
                (1, None, None),
                (7, '{:>7.2f}', 0),
                (8, '{:>8.3f}', float(pz_bot)),
                (7, '{:>7.2f}', float(tz_bot)),
                (7, '{:>7.2f}', 0),
                (8, '{:>8.3f}', float(pz_top)),
                (7, '{:>7.2f}', float(tz_top))
                )
        else:
            '(g15.7,g10.4,g10.4,a3,i2,23x,(g7.2,g8.3,g7.2))'
            notes = (
                (15, '{:>15.7f}', float(pave)),
                (10, '{:>10.4f}', float(tave)),
                (10, '{:>10.4f}', 0),
                (3, '{:>3s}', '0'),
                (2, '{:>2d}', 0),
                (23, None, None),
                (7, '{:>7.2f}', 0),
                (8, '{:>8.3f}', float(pz_top)),
                (7, '{:>7.2f}', float(tz_top))
                )
        
    return notes


@write_record_string
def record_2_1_2(iform=0, wkl=None, wbroadl=None):
    '''
    Parameters
    ----------
    iform: column amount format flag. 0 or 1
           0: read read PAVE, WKL(M,L), WBROADL(L)
              in F10.4, E10.3, E10.3 formats (default)
           1: read PAVE, WKL(M,L), WBROADL(L) in E15.7 format
    wkl: column densities for 7 molecular species [molecules/cm**2]
    wbroadl: column density for broadening gases [molecules/cm**2]
             If iform=1, then wkl and wbroadl are in 8E15.7 format
    '''
    try:
        assert len(wkl) == 7
    except:
        print('wkl needs to be an iterable of length 7')

    if iform == 0:
        span, fmt = 10, '{:>10.3e}'
    elif iform == 1:
        span, fmt = 15, '{:>15.7e}'
    else:
        raise ValueError('iform must be either 0 or 1')

    wkl = [float(density) if density is not None else density
           for density in wkl]
    wbroadl = float(wbroadl) if wbroadl is not None else wbroadl
    notes = [(span, fmt, density) for density in wkl]
    notes.append((span, fmt, wbroadl))
    return tuple(notes)
    

@write_record_string
def record_2_1_3(nmol=7, wkl=None, iform=0):
    '''
    Parameters
    ----------
    iform: column amount format flag. 0 or 1
           0: read read PAVE, WKL(M,L), WBROADL(L)
              in F10.4, E10.3, E10.3 formats (default)
           1: read PAVE, WKL(M,L), WBROADL(L) in E15.7 format
    wkl: column densities for additional molecules
    '''
    if nmol <= 7:
        print('nmol is not greater than 7. Nothing to do.')
    else:
        num_molecules = nmol - 7
        try:
            assert len(wkl) == num_molecules
        except:
            print('Expecting density of {} molecule(s) \
            on top of the first 7'.format(num_molecules))
            print('Please make sure that wkl \
            is an iterable of length {}'.format(num_molecules))

        if iform == 0:
            span, fmt = 10, '{:>10.3f}'
        elif iform == 1:
            span, fmt = 15, '{:>15.7f}'
        else:
            raise ValueError('iform must be either 0 or 1')

        return tuple((span, fmt, density) for density in wkl)



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


def record_3_3_B(heights=None):
    Nrow, fmtspec = 8, '{:>10.3f}'
    


    notes_rows = (
        ((Nrow, fmtspec, value) for value in row) 
        for row in itertools.zip_longest(*(Nrow * [iter(heights)]))
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
    

def write_input_rrtm(ds=None, aerosol=False, iatm=0):
    '''
    Writes INPUT_RRTM for RRTMG column model
    Parameters
    ----------
    ds: xarray.Dataset containing data variables required by RRTMG-SW column model,
        such as pressure, temperature and molecule densities.
    aerosol: True or False.  True to include aerosol effects
    iatm: flag for RRTATM. 1 for yes. 
    '''
    content = collections.deque([])

    # record 1.1
    cxid = 'CXID'
    content.append(record_1_1(CXID=cxid))

    # record 1.2
    iaer = 10 if aerosol else 0
    iatm = iatm
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
    juldat = ds['juldat'].values #int(ds.coords['time'].values[0] % 365)
    sza = ds['sza'].values
    isolvar = 0.
    solvar = None
    content.append(record_1_2_1(juldat=juldat,
                                sza=sza,
                                isolvar=isolvar,
                                solvar=solvar))

    # record 1.4
    iemis = 0
    ireflect = 0
    semiss = None
    content.append(record_1_4(IEMIS=iemis,
                              IREFLECT=ireflect,
                              SEMISS=semiss))
    
    if iatm == 0:
        # record 2.1
        iform = 1
        nlayrs = ds.dims['lev']
        nmol = 7
        content.append(record_2_1(iform=iform,
                                  nlayrs=nlayrs,
                                  nmol=nmol))
        
        for l, lev in enumerate(range(ds.dims['lev'])[::-1]):
            # record 2.1.1
            pave = ds['layer_pressure'].isel(lev=lev)
            pz_bot = ds['level_pressure'].isel(ilev=lev+1)
            pz_top = ds['level_pressure'].isel(ilev=lev)

            tave = ds['layer_temperature'].isel(lev=lev)
            tz_bot = ds['level_temperature'].isel(ilev=lev+1)
            tz_top = ds['level_temperature'].isel(ilev=lev)

            if l == 0:
                is_surface_layer = True
            else:
                is_surface_layer = False
                
            content.append(
                record_2_1_1(iform=iform, is_surface_layer=is_surface_layer,
                             pave=pave, pz_bot=pz_bot, pz_top=pz_top,
                             tave=tave, tz_bot=tz_bot, tz_top=tz_top))

            # record 2.1.2
            names_mols = ['h2o', 'co2', 'o3', 'n2o', 'co', 'ch4', 'o2']   
            wkl = [ds['layer_coldens_' + name].isel(lev=lev)
                   for name in names_mols]
            content.append(record_2_1_2(iform=iform, wkl=wkl, wbroadl=0))
            
            # record 2.1.3
            # Densities of molecules in addition to the 7 in record 2.1.2
            

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
        hbound = 1e-2 * ds['PS']
        htoa = ds['level_pressure'].isel(ilev=0)
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
            if ibmax < 0:
                name = 'level_pressure'
            else:
                name = 'altitude'

            heights = (ds[name][::-1][: abs(ibmax)].values)            

            content.append(record_3_3_B(heights=heights))
            
        if model == 0:
            # record 3.4
            immax = - ds.dims['ilev']
            hmod = 'user-specified'
            content.append(record_3_4(IMMAX=immax, HMOD=hmod))

            # record 3.5 to 3.6
            for i in range(ds.dims['ilev'])[::-1]:
                content.append(
                    record_3_5(nmol=nmol,
                               zm=1e-3 * ds['level_altitude'].isel(ilev=i),
                               pm=ds['level_pressure'].isel(ilev=i),
                               tm=ds['level_temperature'].isel(ilev=i),
                               jcharp='A',
                               jchart='A',
                               jchar_h2o='C',
                               jchar_co2='A',
                               jchar_o3='A',
                               jchar_n2o='A',
                               jchar_co='A',
                               jchar_ch4='A',
                               jchar_o2='C'))
                
                content.append(
                    record_3_6(nmol=nmol,
                               h2o=1e3 * ds['level_mmr_h2o'].isel(ilev=i),
                               co2=1e6 * ds['level_vmr_co2'].isel(ilev=i),
                               o3=1e6  * ds['level_vmr_o3'].isel(ilev=i),
                               n2o=1e6 * ds['level_vmr_n2o'].isel(ilev=i),
                               co=1e6  * ds['level_vmr_co'].isel(ilev=i),
                               ch4=1e6 * ds['level_vmr_ch4'].isel(ilev=i),
                               o2=1e3 * ds['level_mmr_o2'].isel(ilev=i)))

    with open('INPUT_RRTM', mode='w', encoding='utf-8') as file:
        file.write('\n'.join(content))
    
        
def write_in_aer_rrtm(ds):
    '''
    Writes IN_AER_RRTM file for a column in ds.

    Parameters
    ----------
    ds: xarray.Dataset containing variables needed for including
        aerosol effects, at some `time`, `latitude` and `longitude`
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
        aod = ds['tauxar'].sel(lev=lev).values
        content.append(record_a2_1_1(iaod=iaod, lay=lay, aod=aod))
        
    # record A2.2 for all layers
    for lev in ds.coords['lev'][::-1]:
        ssa = ds['wa'].sel(lev=lev).values
        content.append(record_a2_2(issa=issa, ssa=ssa))
    
    # record A2.3 for all layers
    for lev in ds.coords['lev'][::-1]:
        phase = ds['ga'].sel(lev=lev).values
        content.append(record_a2_3(ipha=ipha, phase=phase))

    with open('IN_AER_RRTM_temp', mode='w', encoding='utf-8') as file:
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
