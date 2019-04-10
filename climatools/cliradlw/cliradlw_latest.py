from IPython import display
from bokeh.io import show
from bokeh.palettes import all_palettes
from bokeh.layouts import gridplot
from ..lblnew.bestfit_params import *
from ..atm import *
from ..plot.plot import *






    
def pltdata_cool(dlbl=None, dcli=None):
    colors = all_palettes['Set1'][4]
    igg = 10
    cool_cli = dcli.wgt_cool['coolrg'].sel(i=1).sum('band')
    cool_crd = dlbl.crd_cool['coolrg']
    cool_crd = cool_crd.sum('g') if 'g' in cool_crd.dims else cool_crd
    cool_wgt_igg = dlbl.wgt_cool['coolrg'].sel(igg=igg)
    cool_wgt_igg = cool_wgt_igg.sum('g') if 'g' in cool_wgt_igg.dims else cool_wgt_igg
    data = [{'label':'CLIRAD', 'srs':cool_cli,
             'line_dash':'dashed', 'line_width':5,
             'color':colors[0], 'alpha':.6},
            {'label':'CRD', 'srs':cool_crd,
             'line_dash':'solid', 'line_width':1.5,
             'marker':'circle', 'marker_size':5,
             'color':colors[2], 'alpha':1},
            {'label':f'WGT igg={igg}', 'srs':cool_wgt_igg,
             'line_dash':'solid', 'line_width':8,
             'color':colors[3], 'alpha':.3}]
    return data



def pltdata_diffcool(dlbl=None, dcli=None):
    colors = all_palettes['Set1'][4]
    igg = 10
    cool_cli = dcli.wgt_cool['coolrg'].sel(i=1).sum('band')
    cool_crd = dlbl.crd_cool['coolrg']
    cool_crd = cool_crd.sum('g') if 'g' in cool_crd.dims else cool_crd
    cool_wgt_igg = dlbl.wgt_cool['coolrg'].sel(igg=igg)
    cool_wgt_igg = cool_wgt_igg.sum('g') if 'g' in cool_wgt_igg.dims else cool_wgt_igg
    data = [{'label':'CLIRAD - CRD', 'srs':cool_cli - cool_crd,
             'line_dash':'dashed', 'line_width':5,
             'color':colors[0], 'alpha':.6},
            {'label':f'WGT igg={igg} - CRD', 'srs':cool_wgt_igg - cool_crd,
             'line_dash':'solid', 'line_width':8,
             'color':colors[3], 'alpha':.3}]
    return data



def show_parameters(dlbl=None, dcli=None):
    gs = dlbl.param['molecule'].keys() if isinstance(dlbl.param['molecule'], dict) else [dlbl.param['molecule']]
    ps_cliradfit = {f"({g}, {dlbl.param['band']})": kdist_params(molecule=g, band=dlbl.param['band']) for g in gs}
    fitparams = pd.DataFrame({molgas: pd.Series(p) for molgas, p in ps_cliradfit.items()})
    runparams = pd.concat([pd.Series(dcli.param), pd.Series(dlbl.param)], axis=1, sort=True, keys=['CLIRAD', 'LBLNEW'])
    display.display(pd.concat([runparams, fitparams], axis=1, sort=True, keys=['Run parameters', 'Fit parameters']).fillna('-'))    



def show_cools(dlbl=None, dcli=None):
    plotdata = pltdata_cool(dlbl=dlbl, dcli=dcli)
    diffdata = pltdata_diffcool(dlbl=dlbl, dcli=dcli)
    fig_liny = plt_vert_profile_bokeh(pltdata=plotdata, y_axis_type='linear', prange=(50, 1050))
    fig_logy = plt_vert_profile_bokeh(pltdata=plotdata, y_axis_type='log', prange=(.01, 200))
    fig_diff = plt_vert_profile_bokeh(pltdata=diffdata, y_axis_type='log', prange=(.01, 200))
    show(gridplot(fig_liny, fig_logy, fig_diff, ncols=3, plot_height=500))    
    


def show_title(dlbl=None, dcli=None, add_idanchor=False):
    band, molecule, atmpro = [dcli.param.get(p) for p in ('band', 'molecule', 'atmpro')]
    title = f'{band} {molecule} {atmpro}'
    if add_idanchor:
        idanchor = ''.join(list(np.random.choice(range(9), 11).astype(str)))
        html_idanchor = f'''<a id="{idanchor}"></a>'''
        display.display(display.Markdown(html_idanchor))
        display.display(display.Markdown(title))
        return idanchor
    else:
        display.display(display.Markdown(title))



def show_href(idanchor=None, df=None, dlbl=None, dcli=None):
    band, molecule, atmpro = [dcli.param.get(p) for p in ('band', 'molecule', 'atmpro')]
    band_lblnew = '[' + ','.join(mapband_new2old()[b] for b in band) + ']'
    html_hrefanchor = f'''<a href="#{idanchor}">{atmpro}</a>'''
    try:
        df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] + (' ' + html_hrefanchor)
    except KeyError:
        df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = html_hrefanchor



def show_results(dlbl=None, dcli=None, add_idanchor=None):
    display.display(display.Markdown('-----------------------------'))
    ida = show_title(dlbl=dlbl, dcli=dcli, add_idanchor=add_idanchor)
    # Parameters
    show_parameters(dlbl=dlbl, dcli=dcli)
    # Plot cooling rate profiles
    show_cools(dlbl=dlbl, dcli=dcli)
    display.display(display.Markdown('--------------------------'))
    return ida
