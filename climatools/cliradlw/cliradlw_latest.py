from IPython import display
import re
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

def get_df(ds=None, atmpro=None):
    return (ds.sel(pressure=[ds.pressure.min(), tropopause_pressures()[atmpro], ds.pressure.max()], method='nearest')
            .to_dataframe().set_index('level', append=True)[['flug', 'fldg', 'fnetg']])

def show_flux_tables(dlbl=None, dcli=None, atmpro=None):
    igg = 10
    fcrd = get_df(dlbl.crd_flux.sum('g') if 'g' in dlbl.crd_flux.dims else dlbl.crd_flux, atmpro=atmpro)
    fwgt = get_df((dlbl.wgt_flux.sum('g') if 'g' in dlbl.wgt_flux.dims else dlbl.wgt_flux).sel(igg=igg), atmpro=atmpro)
    fcli = get_df(dcli.wgt_flux.sel(i=1).sum('band'), atmpro=atmpro)
    df = pd.concat([fcrd, fwgt, fcli, fcli - fcrd], axis=1,
                   keys=['CRD', f'WGT igg={igg}', 'CLIRAD', f'CLIRAD - CRD'])
    display.display(df.round(4))
    
def show_title(dlbl=None, dcli=None, idanchor=None):
    band, molecule, atmpro = [dcli.param.get(p) for p in ('band', 'molecule', 'atmpro')]
    title = f'#### {band} {molecule} {atmpro}'
    if idanchor:
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
        if pd.isna(df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")]):
            df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = html_hrefanchor
        else:
            df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = str(df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")]) + ' ' + html_hrefanchor
    except KeyError:
        df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = html_hrefanchor

def remove_href(idanchor=None, df=None, dlbl=None, dcli=None):
    band, molecule, atmpro = [dcli.param.get(p) for p in ('band', 'molecule', 'atmpro')]
    band_lblnew = '[' + ','.join(mapband_new2old()[b] for b in band) + ']'
    try:
        if not pd.isna(df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")]):
            df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")] = re.sub(f'<a [^ <a]*>{atmpro}</a>', '', df.loc[f"{molecule}", (f"{band_lblnew}", f"{band}")]).strip()
    except KeyError:
        pass

def show_results(dlbl=None, dcli=None, idanchor=None, atmpro=None):
    display.display(display.Markdown('-----------------------------'))
    ida = show_title(dlbl=dlbl, dcli=dcli, idanchor=idanchor)
    # Parameters
    show_parameters(dlbl=dlbl, dcli=dcli)
    # Plot cooling rate profiles
    show_cools(dlbl=dlbl, dcli=dcli)
    # Show flux table
    show_flux_tables(dlbl=dlbl, dcli=dcli, atmpro=atmpro)
    display.display(display.Markdown('_____'))
    return ida
