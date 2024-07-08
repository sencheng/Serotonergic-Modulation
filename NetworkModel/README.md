**This branch generates *Fig. 5*, which is presented in "Gain control of sensory input across polysynaptic circuitries in visual cortex
by a single G protein-coupled receptor type (5-HT2A)".**

**Steps to run simulations and generate figures:**

1. Set `data_dir` variable in `defaultParams.py` to determine the location, in which the raw data and figures will be stored.
2. Determine the type of experiment, which you want to generate the data for via variable `do_for_experiment_type`.
3. Run `python simulateNetworks_hpc.py`. Given the default parameters set (`searchParams.py` & `defaultParams.py`) this 
simulation requires a couple of hours to finish. We enable parallel simulation for 
independent subsets of the entire given parameter set. The total number of independent subsets (*N*) can be get via 
`python searchParams.py` and can be used as in `bash run_multiple_sims.sh 0 N`.
4. Run `python rawdata_wrapper.py` to concatenate the data generated from various parameter subsets.
5. Run `python figures_hpc.py` to generate average firing rates, gain and conductance.
6. Run `python export_data.py` to generate data in a simplified format. For this update `dir_name` to the
directory, for which the simplified data should be generated. 
