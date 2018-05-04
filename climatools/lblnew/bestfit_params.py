

from ..clirad import info as clirad

'''
This file contains the parameters that have been
empirically determined to be the best k-distribution
parameters for 'lblnew.f'.  
'''


def kdist_params(molecule=None, band=None):
    '''
    Returns a set of parameters that are considered best-fit
    values.  It should uniquely identify the lblnew-bestfit
    run that produced the best-fit results and the needed data-tables
    for clirad-lw.

    This set of parameters allows lblnew-overlap and clirad-lw to be
    updated with the best-fit values or data-tables corresponding to
    the best-fit values.
    '''
    allowed_molecules = ('h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2')
    allowed_bands = clirad.wavenumber_bands(region='lw').keys()

    if molecule not in allowed_molecules:
        raise ValueError('Input molecule not identified.')

    if band not in allowed_bands:
        raise ValueError('Input spectral band not identified.')

    if molecule == 'h2o':
        if band == '1':
            # h2o band1

            # crd Git commit 
            commitnumber = '443e4ac'

            # Spectral info
            vmin, vmax = 20, 340
            dv = .001
            nv = 1000

            # k-distribution parameterization
            ref_pts = [(1, 250), (30, 250), (300, 250)]
            ng_refs = [3, 3, 6]
            ng_adju = [0, 0, 0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.2, .2, .2), (.2, .2, .2), 
                   (.2, .2, .65, .65, .65, .65)]

            # Flux calculation-related
            w_diffuse = [(1.66, 1.66, 1.66), (1.66, 1.66, 1.66),
                         (1.66, 1.66, 1.5, 1.5, 1.5, 1.5)]
            option_wgt_flux = 1

            # Atmosphere profile
            atmpro = 'mls'
            tsfc = 294
            conc = None

            # Data-table calculations
            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '2':
            # h2o band2

            commitnumber = '443e4ac'

            vmin, vmax = 340, 540
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (10, 250), (500, 250)]
            ng_refs = [2, 3, 6]
            ng_adju = [-2, -2, 0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.6, .6), (.6, .6, .6), 
                   (.6, .6, .6, .6, .6, .6)]

            w_diffuse = [(1.66, 1.66), (1.8, 1.8, 1.8),
                         (1.8, 1.66, 1.45, 1.45, 1.45, 1.45)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '3a':   
            # h2o band3a
            
            commitnumber = '443e4ac'

            vmin, vmax = 540, 620
            dv = .001
            nv = 1000

            ref_pts = [(10, 250), (600, 250)]
            ng_refs = [2, 6]
            ng_adju = [0, 0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.7, .7), (.7, .5, .5, .5, .5, .5)]

            w_diffuse = [(1.9, 1.7), (1.4, 1.4, 1.4, 1.55, 1.6, 1.66)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '3b':

            # h2o band3b

            commitnumber = '443e4ac'

            vmin, vmax = 620, 720
            dv = .001
            nv = 1000

            ref_pts = [(600, 250)]
            ng_refs = [6]
            ng_adju = [0]
            klin = 1e-24
            option_wgt_k = 1
            wgt = [(.8, .8, .8, .6, .6, .9)]

            w_diffuse = [(1.66, 1.66, 1.66, 1.55, 1.5, 1.66)]
            option_wgt_flux = 1

            atmpro = 'trp'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '3c':

            # h2o band3c

            commitnumber = '443e4ac'

            vmin, vmax = 720, 800
            dv = .001
            nv = 1000
            ref_pts = [(600, 250)]
            ng_refs = [5]
            ng_adju = [0]
            klin = 5e-25
            option_wgt_k = 1
            wgt = [(.5, .5, .6, .7, .9)]

            w_diffuse = [(1.55, 1.6, 1.66, 1.66, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '4':
            # h2o band4

            commitnumber = '443e4ac'

            vmin, vmax = 800, 980
            dv = .001
            nv = 1000

            ref_pts = [(600, 250)]
            ng_refs = [3]
            ng_adju = [0]
            klin = 1e-24
            option_wgt_k = 1
            wgt = [(.5, .55, .85)]

            w_diffuse = [(1.66, 1.66, 1.85)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '5':

            # h2o band5

            commitnumber = '443e4ac'

            vmin, vmax = 980, 1100
            dv = .001
            nv = 1000

            ref_pts = [(600, 250)]
            ng_refs = [3]
            ng_adju = [0]
            klin = 1e-24
            option_wgt_k = 1
            wgt = [(.5, .55, .9)]

            w_diffuse = [(1.66, 1.66, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '6':

            # h2o band6

            commitnumber = '443e4ac'

            vmin, vmax = 1100, 1215
            dv = .001
            nv = 1000

            ref_pts = [(600, 250)]
            ng_refs = [4]
            ng_adju = [0]
            klin = 5e-25
            option_wgt_k = 1
            wgt = [(.3, .45, .6, .95)]

            w_diffuse = [(1.66, 1.66, 1.7, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '7':

            # h2o band7

            commitnumber = '443e4ac'

            vmin, vmax = 1215, 1380
            dv = .001
            nv = 1000

            ref_pts = [(600, 250)]
            ng_refs = [7]
            ng_adju = [0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.5, .5, .5, .5, .5, .5, .9)]

            w_diffuse = [(2, 1.6, 1.6, 1.6, 1.6, 1.6, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '8':

            # h2o band8

            commitnumber = '443e4ac'

            vmin, vmax = 1380, 1900
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (10, 250), (500, 250)]
            ng_refs = [3, 2, 3]
            ng_adju = [0, -1, 0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.55, .55, .85), (.85, .85), (0, .3, .55)]

            w_diffuse = [(1.66, 1.66, 1.66), (1.66, 1.66), (1.66, 1.66, 1.66)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '9':

            # h2o band9

            commitnumber = '443e4ac'

            vmin, vmax = 1900, 3000
            dv = .001
            nv = 1000

            ref_pts = [(500, 250)]
            ng_refs = [5]
            ng_adju = [0]
            klin = 1e-24
            option_wgt_k = 1
            wgt = [(.4, .4, .5, .55, .85)]

            w_diffuse = [(1.66, 1.66, 1.66, 1.66, 1.66)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

    elif molecule == 'co2':
        if band == '1':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '2':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '3a':

            # co2 band3a

            commitnumber = '443e4ac'

            vmin, vmax = 540, 620
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (10, 250), (500, 250)]
            ng_refs = [3, 2, 4]
            ng_adju = [0, 0, 0]
            klin = 6.375563e-24
            option_wgt_k = 1
            wgt = [(.7, .3, .7), (.7, .6), (.4, .5, .8, .95)]

            w_diffuse = [(1.6, 1.6, 1.7), (1.75, 1.75), 
                         (1.55, 1.55, 1.6, 1.85)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '3b':

            # co2 band3b

            commitnumber = '443e4ac'

            vmin, vmax = 620, 720
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (10, 250)]
            ng_refs = [5, 2]
            ng_adju = [0, 0]
            klin = 0
            option_wgt_k = 1
            wgt = [(0, .6, .5, .7, .8), (.8, .7)]

            w_diffuse = [(1.66, 1.66, 1.66, 1.66, 1.66), (1.66, 1.66)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1


        elif band == '3c':

            # co2 band3c

            commitnumber = '443e4ac'

            vmin, vmax = 720, 800
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (10, 250), (500, 250)]
            ng_refs = [3, 2, 4]
            ng_adju = [0, 0, 0]
            klin = 6.375563e-24
            option_wgt_k = 1
            wgt = [(0.6, 0.4, 0.7), (0.7, 0.4), (0.3, 0.4, 0.85, 0.90)]

            w_diffuse = [(1.7, 1.6, 1.8), (1.8, 1.7), (1.5, 1.6, 1.7, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '4':

            # co2 band4

            commitnumber = '443e4ac'

            vmin, vmax = 800, 980
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (500, 250)]
            ng_refs = [1, 2]
            ng_adju = [0, 0]
            klin = 6.5e-24
            option_wgt_k = 1
            wgt = [(.75,), (.75, .95)]

            w_diffuse = [(1.75,), (1.66, 1.90)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '5':

            # co2 band5

            commitnumber = '443e4ac'

            vmin, vmax = 980, 1100
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (500, 250)]
            ng_refs = [1, 2]
            ng_adju = [0, 0]
            klin = 6.5e-24
            option_wgt_k = 1
            wgt = [(.75,), (.75, .95)]

            w_diffuse = [(1.75,), (1.66, 1.90)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '6':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '7':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '8':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '9':

            # co2 band9

            commitnumber = '443e4ac'

            vmin, vmax = 1900, 3000
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (50, 250)]
            ng_refs = [3, 3]
            ng_adju = [0, 0]
            klin = 6.5e-24
            option_wgt_k = 1
            wgt = [(.7, .8, .7), (.8, .7, .8)]

            w_diffuse = [(1.66, 1.66, 1.75), (1.75, 1.6, 1.85)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 400e-6

            option_compute_btable = 0
            option_compute_ktable = 1


    elif molecule == 'o3':
        if band == '5':

            # o3 band5

            commitnumber = '443e4ac'

            vmin, vmax = 980, 1100
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (50, 250)]
            ng_refs = [2, 5]
            ng_adju = [0, 0]
            klin = 2e-20
            option_wgt_k = 1
            wgt = [(.35, .6), (.5, .55, .7, .9, 1.)]

            w_diffuse = [(1.6, 1.75), (1.55, 1.66, 1.7, 1.75, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1


        elif band == '9':

            # o3 band9

            commitnumber = '443e4ac'

            vmin, vmax = 1900, 3000
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (50, 250)]
            ng_refs = [2, 5]
            ng_adju = [0, 0]
            klin = 2e-20
            option_wgt_k = 1
            wgt = [(.3, .4), (.5, .6, .7, .85, .9)]

            w_diffuse = [(1.55, 1.55), (1.55, 1.55, 1.55, 1.55, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = None

            option_compute_btable = 0
            option_compute_ktable = 1

        else:
            raise ValueError('{} {} best-fit not available'.format(molecule, band))

    elif molecule == 'n2o':
        if band == '3a':

            # n2o band3a

            commitnumber = '443e4ac'

            vmin, vmax = 540, 620
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (500, 250)]
            ng_refs = [1, 2]
            ng_adju = [0, 0]
            klin = 2.22e-20
            option_wgt_k = 1
            wgt = [(.9,), (.5, .95)]

            w_diffuse = [(1.8,), (1.66, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 3.2e-07

            option_compute_btable = 0
            option_compute_ktable = 1

        elif band == '7':

            # n2o band7

            commitnumber = '443e4ac'

            vmin, vmax = 1215, 1380
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (500, 250)]
            ng_refs = [2, 2]
            ng_adju = [0, 0]
            klin = 2.22e-20
            option_wgt_k = 1
            wgt = [(.6, .5), (.6, .9)]

            w_diffuse = [(1.8, 1.66), (1.6, 1.8)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 3.2e-07

            option_compute_btable = 0
            option_compute_ktable = 1

        else:
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        
    elif molecule == 'ch4':
        if band == '6':

            # ch4 band6

            commitnumber = '443e4ac'

            vmin, vmax = 1100, 1215
            dv = .005
            nv = 200

            ref_pts = [(500, 250)]
            ng_refs = [1]
            ng_adju = [0]
            klin = 0
            option_wgt_k = 1
            wgt = [(.85,)]

            w_diffuse = [(1.66,)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 1.8e-6

            option_compute_btable = 0
            option_compute_ktable = 0

        elif band == '7':

            # ch4 band7

            commitnumber = '443e4ac'

            vmin, vmax = 1215, 1380
            dv = .001
            nv = 1000

            ref_pts = [(1, 250), (500, 250)]
            ng_refs = [2, 3]
            ng_adju = [0, 0]
            klin = 2e-21
            option_wgt_k = 1
            wgt = [(.7, .7), (.4, .6, .75)]

            w_diffuse = [(1.66, 1.66), (1.66, 1.66, 1.66)]
            option_wgt_flux = 1

            atmpro = 'mls'
            tsfc = 294
            conc = 1.8e-6

            option_compute_btable = 0
            option_compute_ktable = 1

        else:
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
    elif molecule == 'o2':
        raise ValueError('{} {} best-fit not available'.format(molecule, band))

    return {'molecule': molecule,
            'band': band,
            'commitnumber': commitnumber,
            'vmin': vmin, 
            'vmax': vmax,
            'dv': dv, 
            'nv': nv,
            'ref_pts': ref_pts,
            'ng_refs': ng_refs,
            'ng_adju': ng_adju,
            'klin': klin,
            'option_wgt_k': option_wgt_k,
            'wgt': wgt,
            'w_diffuse': w_diffuse,
            'option_wgt_flux': option_wgt_flux,
            'atmpro': atmpro,
            'tsfc': tsfc,
            'conc': conc,
            'option_compute_btable': option_compute_btable,
            'option_compute_ktable': option_compute_ktable}
