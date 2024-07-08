################################################################################
# -- Default set of parameters
################################################################################

from defaultParams import *

fr_chg_factor = np.array([1.0])
E_extra_stim_factor = np.array([1.0])
EEconn_chg_factor = np.arange(0.5, 4.1, 0.5)
EIconn_chg_factor = np.array([1.0])
IIconn_chg_factor = np.array([1.0])
bkg_chg_factor    = np.array([3.])
evoked_fr_chg_factor = np.array([20.])/10
C_rng = np.arange(1, 20.1, 1).astype(int)  # Different model instances.
EE_probchg_comb, EI_probchg_comb, II_condchg_comb, E_extra_comb, bkg_chg_comb, evfr_chg_comb = \
    np.meshgrid(EEconn_chg_factor, EIconn_chg_factor, IIconn_chg_factor, E_extra_stim_factor, bkg_chg_factor, evoked_fr_chg_factor)

E_pert_frac = 1.0

print("Total number of independent subsets are {}".format(EE_probchg_comb.size*C_rng.size))
