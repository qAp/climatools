# Climatools

This library lets you:
1. Run a selection of atmosphere radiation models.
2. Store, organize and retrieve results of each run in MongoDB.
3. Visualize and tabulate results in the most common formats.
4. Update parameter tables in parameterized atmosphere radiation model.

## Running the atmosphere radiation models
`Climatools` provides utilities for running several atmosphere radiation, or radiative transfer, models.

### lblnew-bestfit
This computes the radiation for a single absorber and spectral band, e.g. (h2o, band 2).  It outputs results using two methods: line-by-line and k-distribution parameterization.

The [run_lblnew-bestfit.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/run_lblnew-bestfit.ipynb) notebook demonstrates how to run `lblnew-best`, store the results in MongoDB, execute the [analysis notebook](https://nbviewer.jupyter.org/github/qAp/analysis_-_new_kdist_param/blob/master/lblnew/h2o/conc_None/band03b_wn_620_720/nv_1000/dv_0.001/ng_6/g_ascending_k_descending/refPTs_P_600_T_250/ng_refs_6/ng_adju_0/getabsth_auto/absth_dlogN_uniform/klin_1e-24/atmpro_mls/wgt_k_1/wgt_0.8_0.8_0.8_0.6_0.6_0.9/wgt_flux_1/w_diffuse_1.66_1.66_1.66_1.55_1.5_1.66/option_compute_ktable_0/option_compute_btable_0/crd_5014a19/results.ipynb).  

Things to note:
* This model is primarily used to tune the k-distribution parameterization method model.
* The input parameter `commitnumber` can be any arbitrary string, used to identify the model run, useful when two runs have the same set of input parameter values but different versions of the code.
* Suppose its program files (Fortran) are in the directory `path/to/lblnew_bestfit`, then, before running it, you need to set `DIR_SRC` in `climatools/climatools/lblnew/setup_bestfit.py` to `path/to/lblnew_besfit`.
* Setting `option_compute_ktable` to `True`, the model will compute large k-tables for the k-distribution method, which takes a long time.  This is normally reserved for the best-fit parameter values only, where one intends to export the k-tables to the `clirad-lw` model.

### lblnew-overlap
This computes radiation for a single spectral band with multiple absorbers. e.g. (band 3a, [h2o, o3]).  It outputs results using two methods: *line-by-line* and *k-distribution parameterization*.  The [run_lblnew-overlap.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/run_lblnew-overlap.ipynb) notebook demonstrates how to run it, store the results in MongoDB, execute the [analysis notebook](https://nbviewer.jupyter.org/github/qAp/analysis_-_new_kdist_param/blob/master/lblnew/h2o_atmpro_co2_0_o3_0_n2o_6.4e-07_ch4_1.8e-06_o2_0/band07_wn_1215_1380/nv_1000/dv_0.001/crd_a22ab94/atmpro_mls/results_overlap.ipynb).

Things to note:
* This model is primarily used to verify the accuracy of parameterized method relative to the line-by-line method.

### clirad-lw
This computes radiation for any selection of spectral bands and absorbers. e.g. ([band 1, band 7], [h2o, n2o]).  It outputs results using the *k-distribution parameterization* method.  The [run_cliradlw.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/run_cliradlw.ipynb) demonstrates how to run it, store the results in MongoDB and run the [analysis notebook](https://nbviewer.jupyter.org/github/qAp/analysis_-_new_kdist_param/blob/master/clirad/h2o_saw_n2o_3.2e-07_ch4_1.8e-06/band_9/atmpro_saw/cliradlw_1013f91/results_cliradlw.ipynb).

## Results summary
[Here](https://nbviewer.jupyter.org/github/qAp/analysis_-_new_kdist_param/blob/master/clirad_weblinks_latest.ipynb) are the most update-to-date results from `clirad-lw` for all considered combinations of spectral bands and absorbers.  The results of `clirad-lw` are compared with the *line-by-line* results from `lblnew-bestfit`.

## Updating `clirad-lw` model parameters
To update the k-distribution parameterization model `clirad-lw`'s model parameters, use the functions in `climatools.lblnew.export`.  Notebooks [get_kdist_bestfits_F77.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/get_kdist_bestfits_F77.ipynb) and [get_kdist_ktable_F77.ipynb](https://nbviewer.jupyter.org/github/qAp/climatools/blob/master/climatools/notebooks/get_kdist_ktable_F77.ipynb) allow the user to update all the parameters of `clirad-lw`.


