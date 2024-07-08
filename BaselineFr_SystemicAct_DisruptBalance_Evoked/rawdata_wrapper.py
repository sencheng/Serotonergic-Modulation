import numpy as np
import pickle
import copy
import os
from imp import reload
import defaultParams; reload(defaultParams); from defaultParams import *
import searchParams; reload(searchParams); from searchParams import *

def _read_data(be, bi, res_path):
    sim_res = {}
    for rng_c in C_rng:
        sim_name = 'sim_res_Be{:.2f}_Bi{:.2f}_Mo{:d}'.format(be, bi, rng_c)
        if os.path.exists(os.path.join(res_path, sim_name)):
            print('\nLoading {} ...'.format(sim_name))
        else:
            print("The file does not exist, terminating ...")
        with open(os.path.join(res_path, sim_name), 'rb') as fl:
            tmp_out = pickle.load(fl)
        if rng_c == C_rng[0]:
            sim_res = copy.copy(tmp_out)
        for nn_stim in nn_stim_rng:
            for tr in tmp_out[nn_stim][3].keys():
                sim_res[nn_stim][2][tr] = copy.copy(tmp_out[nn_stim][2][tr])
                sim_res[nn_stim][3][tr] = copy.copy(tmp_out[nn_stim][3][tr])
                sim_res[nn_stim][4][tr] = copy.copy(tmp_out[nn_stim][4][tr])
    return sim_res

def _remove_data(res_path):
    for be in Be_rng:
        for bi in Bi_rng:
            for rng_c in C_rng:
                sim_name = 'sim_res_Be{:.2f}_Bi{:.2f}_Mo{:d}'.format(be, bi, rng_c)
                if os.path.exists(os.path.join(res_path, sim_name)):
                    print('\nDeleting {} ...'.format(sim_name))                    
                    os.remove(os.path.join(res_path, sim_name))
                else:
                  print("The file does not exist")
                

EE_probchg_comb, EI_probchg_comb, II_condchg_comb, E_extra_comb, bkg_chg_comb, evfr_chg_comb = np.meshgrid(EEconn_chg_factor, EIconn_chg_factor, IIconn_chg_factor, E_extra_stim_factor, bkg_chg_factor, evoked_fr_chg_factor)

EE_probchg_comb = EE_probchg_comb.flatten()
EI_probchg_comb = EI_probchg_comb.flatten()
II_condchg_comb = II_condchg_comb.flatten()
E_extra_comb = E_extra_comb.flatten()
bkg_chg_comb = bkg_chg_comb.flatten()
evfr_chg_comb = evfr_chg_comb.flatten()
print(evfr_chg_comb.size)
if pert_type == 'spike':
    stim_inh, stim_exc = r_stim_inh, r_stim_exc
else:
    stim_inh, stim_exc = I_stim_inh, I_stim_exc

for ij1 in range(evfr_chg_comb.size):
    sim_suffix_comp = sim_suffix.format(EE_probchg_comb[ij1], EI_probchg_comb[ij1], ev_arrange, pert_type, N, evfr_chg_comb[ij1]*100, ev_prop*100, ev_pop, C_rng.size, Ntrials, stim_inh/1.e3, stim_exc/1.e3, r_act_inh*EI_probchg_comb[ij1], r_act_exc*EE_probchg_comb[ij1], II_scale, bkg_chg_comb[ij1], p_ItoI)
    res_path = os.path.join(data_dir, res_dir+sim_suffix_comp)
    print('Processing path {}'.format(res_path))
    if not os.path.exists(res_path): print('Simulation data does not exist!')
    for be in Be_rng:
        for bi in Bi_rng:
            data = _read_data(be, bi, res_path)
            sim_name = 'sim_res_Be{:.2f}_Bi{:.2f}'.format(be, bi)
            print('\nWriting sim_res_Be{:.2f}_Bi{:.2f}'.format(be, bi))
            with open(os.path.join(res_path, sim_name), 'wb') as fl:
                pickle.dump(data, fl)
    _remove_data(res_path)
