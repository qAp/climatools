import pymongo
from .cliradlw.utils import *
from .dataset import *



class Param():
    def __init__(self, commitnumber=None, band=None, molecule=None,
                 atmpro=None, tsfc=None):
        self.commitnumber = commitnumber
        self.band, self.molecule = band, molecule
        self.atmpro, self.tsfc = atmpro, tsfc



class CliradnewLWParam(Param):
    model_name = 'cliradnew-lw'
    def __init__(self, **kwargs): super().__init__(**kwargs)
        
    def to_lblnewparam(self, squeeze=False, dv=None, nv=None):
        '''

        '''
        if len(self.molecule == 1):
            # There is only one absorber.
            if squeeze == True:
                # Return lblnew-bestfit parameter
                band = mapband_new2old(self.band[0])
                
                return LBLnewBestfitParam
            else:
                # Return lblnew-overlap parameter
                return LBLnewOverlapParam
        else:
            # There is absorber overlapping
            return LBLnewOverlapParam

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
    def __init__(self, **kwargs): super().__init__(**kwargs)
    def __repr__(self):
        d = dict(commitnumber=self.commitnumber,
                 band=self.band, molecule=self.molecule,
                 atmpro=self.atmpro, tsfc=self.tsfc,
                 nv=self.nv, dv=self.dv)
        body = '\n'.join(sorted(f'{n}: {v}' for n, v in d.items()))
        return f'{self.__class__}\n{body}\n'
    

    
class LBLnewBestfitParam(LBLnewParam):
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
        
        
