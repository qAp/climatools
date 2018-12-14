
import io
import pandas as pd
import xarray as xr



def load_output_file(path_csv):
    '''
    Load output file to xarray.Dataset.  
    The output file can be from either lblnew
    or clirad, as long as it's .csv and multi-index
    format.
    
    Parameters
    ----------
    path_csv: str
              Path to the .csv file to be loaded.
    ds: xarray.Dataset
        Data in the input file in the form of an xarray.Dataset.
    '''
    toindex = ['i', 'band', 'pressure', 'igg', 'g']    
    df = pd.read_csv(path_csv, sep=r'\s+')
    df = df.set_index([i for i in toindex if i in df.columns])
    df = df.rename(columns={'sfu': 'flug', 'sfd': 'fldg', 'fnet': 'fnetg',
                            'coolr': 'coolrg'})
    ds = xr.Dataset.from_dataframe(df)

    for l in ('level', 'layer'):
        if l in ds.data_vars:
            if len(ds[l].dims) > 1:
                surface = {d: 0 for d in ds.dims if d != 'pressure'}
                coord_level = ds[l][surface]
                ds.coords[l] = ('pressure', coord_level)
            else:
                ds.coords[l] = ('pressure', ds[l])
    return ds



class CliradnewLWModelData():
    def __init__(self, param, wgt_flux, wgt_cool):
        self.param, self.wgt_flux, self.wgt_cool = param, wgt_flux, wgt_cool
    
    @classmethod
    def from_mongodoc(cls, doc):
        param = doc['param']
        wgt_flux = load_output_file(io.StringIO(doc['output_flux']))
        wgt_cool = load_output_file(io.StringIO(doc['output_coolr']))
        return cls(param, wgt_flux, wgt_cool)



class LBLnewModelData():
    def __init__(self, param, wgt_flux, wgt_cool, crd_flux, crd_cool):
        self.param = param
        self.wgt_flux, self.wgt_cool = wgt_flux, wgt_cool
        self.crd_flux, self.crd_cool = crd_flux, crd_cool



class LBLnewBestfitModelData(LBLnewModelData):
    def __init__(self, param, 
                 wgt_flux, wgt_cool, crd_flux, crd_cool, dgdgs, abscom):
        self.dgdgs = dgdgs
        self.abscom = abscom
        super().__init__(param, wgt_flux, wgt_cool, crd_flux, crd_cool)

    @classmethod
    def from_mongodoc(cls, doc):
        param = doc['param']
        wgt_flux = load_output_file(io.StringIO(doc['output_wfluxg']))
        wgt_cool = load_output_file(io.StringIO(doc['output_wcoolrg']))
        crd_flux = load_output_file(io.StringIO(doc['output_fluxg']))
        crd_cool = load_output_file(io.StringIO(doc['output_coolrg']))
        dgdgs = pd.read_csv(io.StringIO(doc['dgdgs']), sep=r'\s+')
        abscom = pd.read_csv(io.StringIO(doc['abscom']), sep=r'\s+')
        return LBLnewBestfitModelData(param, wgt_flux, wgt_cool, crd_flux, crd_cool, dgdgs, abscom)



class LBLnewOverlapModelData(LBLnewModelData):
    @classmethod
    def from_mongodoc(cls, doc):
        param = doc['param']
        wgt_flux = load_output_file(io.StringIO(doc['output_wflux']))
        wgt_cool = load_output_file(io.StringIO(doc['output_wcoolr']))
        crd_flux = load_output_file(io.StringIO(doc['output_flux']))
        crd_cool = load_output_file(io.StringIO(doc['output_coolr']))
        return cls(param, wgt_flux, wgt_cool, crd_flux, crd_cool)
        




        
    
        
        
        
