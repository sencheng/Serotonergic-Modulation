"""
This file generates plots used in Extended Data Fig. 9.
"""

import os
import pickle
from matplotlib import pyplot as plt

from searchParams import *
from defaultParams import *

processing_perturbed_pop = 'inh'

# path to the file where `diff_data` exists. This file is generated after running `figures_hpc.py`
PATH = f'/work/mohammad/5HT2A/simdata/research-pert-strength/{processing_perturbed_pop}'
FILENAME = 'diff_data'

with open(os.path.join(PATH, FILENAME), 'rb') as fl:
    data = pickle.load(fl)

red_cm = list(zip(np.linspace(0.4, 1., nn_stim_rng.size),
                  np.zeros(nn_stim_rng.size),
                  np.zeros(nn_stim_rng.size)))
blue_cm = list(zip(np.zeros(nn_stim_rng.size),
                   np.zeros(nn_stim_rng.size),
                   np.linspace(0.4, 1., nn_stim_rng.size)))
pop_ind_map = {'exc': 0, 'inh': 1}
pop_cm_map = {'exc': red_cm, 'inh': blue_cm}
colors_intensity = np.linspace(0.2, 1.0, nn_stim_rng.size)
fig, ax = plt.subplots(ncols=2)
if processing_perturbed_pop == 'exc':
    init_key = EIconn_chg_factor[0]
elif processing_perturbed_pop == 'inh':
    init_key = EEconn_chg_factor[0]
else:
    raise f'Invalid processing population {processing_perturbed_pop}'

firing_rate_changes = {'inh': {0: {}, 25: {}, 50: {}, 75: {}, 100: {}},
                       'exc': {0: {}, 25: {}, 50: {}, 75: {}, 100: {}}}
coefficients = {'inh': 100, 'exc': 50}

if processing_perturbed_pop == 'exc':
    for factor_ind, ee_coef in enumerate(EEconn_chg_factor):
        exc_inh = data[ee_coef][init_key]
        for pop, pert_fr_map in exc_inh.items():
            for pert, fr_chg in pert_fr_map.items():
                firing_rate_changes[pop][int(pert*100/40)][ee_coef] = fr_chg

if processing_perturbed_pop == 'inh':
    for factor_ind, ei_coef in enumerate(EIconn_chg_factor):
        exc_inh = data[init_key][ei_coef]
        for pop, pert_fr_map in exc_inh.items():
            for pert, fr_chg in pert_fr_map.items():
                firing_rate_changes[pop][int(pert*100/40)][ei_coef] = fr_chg

for pop in ['exc', 'inh']:
    cnt = 0
    for pert, stim_fr_map in firing_rate_changes[pop].items():
        ax[pop_ind_map[pop]].plot(np.array(list(stim_fr_map.keys())) * coefficients[processing_perturbed_pop],
                                  list(stim_fr_map.values()),
                                  color=pop_cm_map[pop][cnt],
                                  label=f'{pert} %',
                                  marker='o')
        cnt += 1
    ax[0].legend()
    ax[1].legend()
ax[0].set_ylabel(r'$\Delta FR$')
ax[0].set_xlabel('Perturbation strength (Hz)')
ax[1].set_xlabel('Perturbation strength (Hz)')
ax[0].set_title('Excitatory population')
ax[1].set_title('Inhibitory population')
fig.tight_layout()
fig.savefig(f'pert-strength-{processing_perturbed_pop}-norm.png')
fig.savefig(f'pert-strength-{processing_perturbed_pop}-norm.pdf')
fig.savefig(f'pert-strength-{processing_perturbed_pop}-norm.svg')
print(firing_rate_changes)