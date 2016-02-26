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



