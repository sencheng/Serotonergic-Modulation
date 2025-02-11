################################################################################
# -- Default set of parameters
################################################################################

import numpy as np; import pylab as pl; import time, sys, os
import matplotlib
from defaultParams import *

fr_chg_factor = np.array([1.0])#np.arange(0.5, 1, .1)
E_extra_stim_factor = np.array([1.0])#np.arange(0.2, .9, 0.9)#np.array([0.8])
EEconn_chg_factor = np.array([1.0])#np.arange(0.05, 0.51, 0.05)#np.arange(0.1, 0.51, 0.1)#n11rray([0.9])p.array([0.9])
EIconn_chg_factor = np.array([1.0])#np.arange(1., 4., 0.2)#np.array([2.0])
IIconn_chg_factor = np.array([1.0])#np.arange(1, 1.1, 0.2)
bkg_chg_factor    = np.array([3.])#np.arange(1.1, 1.21, 0.1)#np.array([1.0])#np.arange(1.05, 1.11, 0.05)
evoked_fr_chg_factor = np.array([20.])/10#np.array([24.])/50#np.array([24., 48., 96.])#np.arange(8., 24.1, 8)
C_rng = np.arange(1, 20.1, 1).astype(int)
EE_probchg_comb, EI_probchg_comb, II_condchg_comb, E_extra_comb, bkg_chg_comb, evfr_chg_comb = \
    np.meshgrid(EEconn_chg_factor, EIconn_chg_factor, IIconn_chg_factor, E_extra_stim_factor, bkg_chg_factor, evoked_fr_chg_factor)

#pert_comb = pert_comb.flatten()[job_id::num_jobs]

E_pert_frac = 1.0

print("Total number of parameter combinations covered = {}".format(EE_probchg_comb.size))
