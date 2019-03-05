import pymongo
from .cliradlw.utils import *
from .pymongo import *
from .dataset import *



class Param():
    def __init__(self, commitnumber=None, band=None, molecule=None,
                 atmpro=None, tsfc=None):
        self.commitnumber = commitnumber
        self.band, self.molecule = band, molecule
        self.atmpro, self.tsfc = atmpro, tsfc
        
    def pymongo_query(self): return make_query(vars(self))


class CliradnewLWParam(Param):
    model_name = 'cliradnew-lw'
    def __init__(self, **kwargs): super().__init__(**kwargs)

    def modeldata_pymongo(self, collection=None):
        if not collection:
            raise ValueError(('You need to specify a pymongo collection '
                              'containing cliradnew-lw model data.'))
        qry = self.pymongo_query()
        doc = collection.find_one(qry)
        return CliradnewLWModelData.from_mongodoc(doc)
        
    def __repr__(self):
        d = dict(commitnumber=self.commitnumber,
                 band=self.band, molecule=self.molecule,
                 atmpro=self.atmpro, tsfc=self.tsfc)
        return (f'{self.__class__}\n'
                + '\n'.join(sorted(f'{n}: {v}' for n, v in d.items())))

    

class LBLnewParam(Param):
    def __init__(self, dv=None, nv=None, **kwargs):
        self.dv, self.nv = dv, nv
        super().__init__(**kwargs)



class LBLnewOverlapParam(LBLnewParam):
    model_name = 'lblnew-overlap'
    def __init__(self, **kwargs): super().__init__(**kwargs)

    def modeldata_pymongo(self, collection=None):
        if not collection:
            raise ValueError(('You need to specify a pymongo collection '
                              'containing lblnew-overlap model data.'))
        qry = self.pymongo_query()
        doc = collection.find_one(qry)
        if not doc: print('Nothing found for:\n', qry)
        return LBLnewOverlapModelData.from_mongodoc(doc)        
    
    def __repr__(self):
        d = dict(commitnumber=self.commitnumber,
                 band=self.band, molecule=self.molecule,
                 atmpro=self.atmpro, tsfc=self.tsfc,
                 nv=self.nv, dv=self.dv)
        body = '\n'.join(sorted(f'{n}: {v}' for n, v in d.items()))
        return f'{self.__class__}\n{body}\n'
    

    
class LBLnewBestfitParam(LBLnewParam):
    model_name = 'lblnew-bestfit'
    def __init__(self, conc=None, klin=None, ng_adju=None, ng_refs=None,
                 option_compute_btable=None, option_compute_ktable=None,
                 option_wgt_flux=None, option_wgt_k=None, ref_pts=None,
                 vmax=None, vmin=None, w_diffuse=None, wgt=None, **kwargs):
        self.conc = conc
        self.vmin, self.vmax = vmin, vmax
        self.ng_refs, self.ref_pts = ng_refs, ref_pts
        self.ng_adju = ng_adju
        self.klin = klin
        self.option_wgt_k, self.option_wgt_flux = option_wgt_k, option_wgt_flux
        self.wgt, self.w_diffuse = wgt, w_diffuse
        self.option_compute_ktable = option_compute_ktable
        self.option_compute_btable = option_compute_btable
        super().__init__(**kwargs)

    def modeldata_pymongo(self, collection=None):
        if not collection:
            raise ValueError(('You need to specify a pymongo collection '
                              'containing lblnew-besfit model data.'))
        qry = self.pymongo_query()
        doc = collection.find_one(qry)
        return LBLnewBestfitModelData.from_mongodoc(doc)        

    def __repr__(self):
        d = dict(commitnumber=self.commitnumber,
                 band=self.band, molecule=self.molecule,
                 atmpro=self.atmpro, tsfc=self.tsfc,
                 nv=self.nv, dv=self.dv,
                 conc=self.conc,
                 vmin=self.vmin, vmax=self.vmax,
                 ng_refs=self.ng_refs, ref_pts=self.ref_pts, ng_adju = self.ng_adju,
                 klin=self.klin, option_wgt_k=self.option_wgt_k, option_wgt_flux=self.option_wgt_flux,
                 wgt=self.wgt, w_diffuse=self.w_diffuse,
                 option_compute_ktable=self.option_compute_ktable,
                 option_compute_btable=self.option_compute_btable)
        body = '\n'.join(sorted(f'{n}: {v}' for n, v in d.items()))
        return f'{self.__class__}\n{body}\n'
        
        
