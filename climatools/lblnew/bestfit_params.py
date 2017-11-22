

from ..clirad import info as clirad

'''
This file contains the parameters that have been
empirically determined to be the best k-distribution
parameters for 'lblnew.f'.  
'''


def kdist_params(molecule=None, band=None):

    allowed_molecules = ('h2o', 'co2', 'o3', 'n2o', 'ch4', 'o2')
    allowed_bands = clirad.wavenumber_bands(region='lw').keys()

    if molecule not in allowed_molecules:
        raise ValueError('Input molecule not identified.')

    if band not in allowed_bands:
        raise ValueError('Input spectral band not identified.')

    if molecule == 'h2o':
        if band == '1':
            ng_refs = [3, 2, 5]
            ref_pts = [(1, 250), (30, 250), (300, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(.3, .3, .3), (.3, .3), (.3, .6, .6, .6, .6)]
            w_diffuse = [(1.6, 1.8, 1.8), 
                         (1.8, 1.7), (1.6, 1.4, 1.4, 1.7, 1.8)]
        elif band == '2':
            ng_refs = [2, 2, 6]
            ref_pts = [(1, 250), (10, 250), (500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(.4, .4), (.4, .4), (.4, .4, .4, .4, .4, .7)]
            w_diffuse = [(1.66, 1.66), (1.66, 1.66), 
                         (1.66, 1.66, 1.66, 1.66, 1.66, 1.66)]
        elif band == '3a':
            ng_refs = [7]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(.7, .7, .7, .5, .5, .5, .5)]
            w_diffuse = [(1.9, 1.7, 1.4, 1.4, 1.4, 1.55, 1.6)]
        elif band == '3b':
            ng_refs = [6]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 1e-24
            wgt = [(.8, .8, .8, .6, .6, .9)]
            w_diffuse = [(1.66, 1.66, 1.66, 1.66, 1.66, 1.66)]
        elif band == '3c':
            ng_refs = [5]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 5e-25
            wgt = [(.5, .5, .6, .7, .9)]
            w_diffuse = [(1.55, 1.6, 1.66, 1.66, 1.8)]
        elif band == '4':
            ng_refs = [3]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 1e-24
            wgt = [(.5, .55, .85)]
            w_diffuse = [(1.66, 1.66, 1.85)]
        elif band == '5':
            ng_refs = [3]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 1e-24
            wgt = [(.5, .55, .9)]
            w_diffuse = [(1.66, 1.66, 1.8)]
        elif band == '6':
            ng_refs = [4]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 5e-25
            wgt = [(.3, .45, .6, .95)]
            w_diffuse = [(1.66, 1.66, 1.7, 1.8)]
        elif band == '7':
            ng_refs = [7]
            ref_pts = [(600, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(.5, .5, .5, .5, .5, .5, .9)]
            w_diffuse = [(2, 1.6, 1.6, 1.6, 1.6, 1.6, 1.8)]
        elif band == '8':
            ng_refs = [3, 2, 3]
            ref_pts = [(1, 250), (10, 250), (500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(.55, .55, .85), (.85, .85), (0, .3, .55)]
            w_diffuse = [(1.66, 1.66, 1.66), (1.66, 1.66),
                         (1.66, 1.66, 1.66)]
        elif band == '9':
            ng_refs = [5]
            ref_pts = [(500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 1e-24
            wgt = [(.4, .4, .5, .6, .9)]
            w_diffuse = [(1.66, 1.66, 1.66, 1.66, 1.66)]
        

    elif molecule == 'co2':
        if band == '1':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '2':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '3a':
            ng_refs = [3, 2, 4]
            ref_pts = [(1, 250), (10, 250), (500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 6.375563e-24
            wgt = [(.7, .3, .7), (.7, .6), (.4, .5, .8, .95)]
            w_diffuse = [(1.6, 1.6, 1.7), (1.75, 1.75),
                         (1.55, 1.55, 1.6, 1.85)]
        elif band == '3b':
            ng_refs = [5, 2]
            ref_pts = [(1, 250), (10, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 0
            wgt = [(0, .6, .5, .7, .8), (.8, .7)]
            w_diffuse = [(1.66, 1.66, 1.66, 1.66, 1.66), (1.66, 1.66)]
        elif band == '3c':
            ng_refs = [3, 2, 4]
            ref_pts = [(1, 250), (10, 250), (500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 6.375563e-24
            wgt = [(.6, .4, .7), (.7, .5), (.3, .4, .85, .95)]
            w_diffuse = [(1.7, 1.6, 1.8), (1.8, 1.7), (1.5, 1.6, 1.7, 1.8)]
        elif band == '4':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '5':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '6':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '7':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '8':
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        elif band == '9':
            ng_refs = [3, 3]
            ref_pts = [(1, 250), (50, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 6.5e-24
            wgt = [(.7, .7, .7), (.7, .7, .8)]
            w_diffuse = [(1.66, 1.66, 1.66), (1.66, 1.66, 1.8)]
    elif molecule == 'o3':
        if band == '5':
            ng_refs = [2, 5]
            ref_pts = [(1, 250), (50, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 2e-20
            wgt = [(.35, .6), (.5, .55, .7, .9, 1.)]
            w_diffuse = [(1.6, 1.75), (1.55, 1.66, 1.7, 1.75, 1.8)]
        elif band == '9':
            ng_refs = [2, 5]
            ref_pts = [(1, 250), (50, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 2e-20
            wgt = [(.3, .4), (.5, .6, .7, .85, .9)]
            w_diffuse = [(1.55, 1.55), (1.55, 1.55, 1.55, 1.55, 1.8)]
        else:
            raise ValueError('{} {} best-fit not available'.format(molecule, band))

    elif molecule == 'n2o':
        if band == '7':
            ng_refs = [2, 2]
            ref_pts = [(1, 250), (500, 250)]
            option_wgt_flux = 2
            option_wgt_k = 1
            klin = 2.22e-20
            wgt = [(.6, .6), (.7, .9)]
            w_diffuse = [(1.8, 1.66), (1.5, 1.8)]
        else:
            raise ValueError('{} {} best-fit not available'.format(molecule, band))
        
    elif molecule == 'ch4':
        raise ValueError('{} {} best-fit not available'.format(molecule, band))
    elif molecule == 'o2':
        raise ValueError('{} {} best-fit not available'.format(molecule, band))

    return {'ng_refs': ng_refs,
            'ref_pts': ref_pts,
            'option_wgt_flux': option_wgt_flux,
            'option_wgt_k': option_wgt_k,
            'klin': klin,
            'wgt': wgt,
            'w_diffuse': w_diffuse}
