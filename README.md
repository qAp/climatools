# Climatools

This library lets you:
1. Run a selection of atmosphere radiation models.
2. Store, organize and retrieve results of each run in MongoDB.
3. Visualize and tabulate results in the most common formats.
4. Update parameter tables in parameterized atmosphere radiation model.

## Running the atmosphere radiation models
`Climatools` provides utilities for running several atmosphere radiation, or radiative transfer, models.
### lblnew-bestfit
This is a line-by-line model, but alongside the line-by-line calculation, it also uses a parameterized method, so it outputs two sets of results: line-by-line and k-distribution parameterization.  Optionally, it can also compute absorption coefficients for the k-distribution parameterization at specified temperature and pressures.

The [run_lblnew-bestfit.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/run_lblnew-bestfit.ipynb) notebook demonstrates how to run `lblnew-best`, store the results in MongoDB, execute the [analysis notebook](https://nbviewer.jupyter.org/github/qAp/analysis_-_new_kdist_param/blob/master/lblnew/h2o/conc_None/band03b_wn_620_720/nv_1000/dv_0.001/ng_6/g_ascending_k_descending/refPTs_P_600_T_250/ng_refs_6/ng_adju_0/getabsth_auto/absth_dlogN_uniform/klin_1e-24/atmpro_mls/wgt_k_1/wgt_0.8_0.8_0.8_0.6_0.6_0.9/wgt_flux_1/w_diffuse_1.66_1.66_1.66_1.55_1.5_1.66/option_compute_ktable_0/option_compute_btable_0/crd_5014a19/results.ipynb).  

Things to note:
* Suppose its program files (Fortran) are in the directory `path/to/lblnew_bestfit`, then, before running it, you need to set `DIR_SRC` in `climatools/climatools/lblnew/setup_bestfit.py` to `path/to/lblnew_besfit`.
* Setting `option_compute_ktable` to `True`, the model will compute large k-tables for the k-distribution method, which takes a long time.  This is normally reserved for the best-fit parameter values only.


The following atmosphere radiation models can be run, their results analysed, or their parameters updated:  
* lblnew-bestfit-lw
* lblnew-overlap-lw
* lblnew-bestfit-sw
* lblnew-overlap-sw
* cliradnew-lw
* cliradnew-sw

Please see their respective Wiki pages for more details.


