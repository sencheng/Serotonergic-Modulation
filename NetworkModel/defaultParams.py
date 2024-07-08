################################################################################
# -- Default set of parameters
################################################################################

import numpy as np
import pylab as pl
import matplotlib

"""
'exc-only': fig 5, panel a
'inh-only': fig 5, panel b
'systemic-mean': fig 5, panel c
'systemic-fluctuation': fig 5, panel d & e
"""
experiment_types = ['exc-only', 'inh-only', 'systemic-mean', 'systemic-fluctuation']
do_for_experiment_type = 'exc-only'  # must be only one of the types above
if do_for_experiment_type not in experiment_types:
    raise ValueError(f'experiment type {do_for_experiment_type} is not defined!')

## the number of cores to be used for simulations
n_cores = 1

# define the NEST path if it's needed

# Result directory
res_dir = "SimulationFiles"
fig_initial = "Figures"
sim_suffix = "-LIF-rE{:.1f}-rI{:.1f}-{}-{}-N{}-EvFr{:.0f}-EvPr{:.0f}-EvPop{}-Nmodel{}-Ntr{}-I_pert{:.0f}-E_pert{:.0f}-I_act{:.2f}-E_act{:.2f}-II{:.1f}-bkgfac{:.2f}-II{:.2f}"
data_dir = f"/work/mohammad/5HT2A/simdata/fig5/{do_for_experiment_type}"
fig_dir = data_dir
# ------------- neuron params

# resting potential (mV)
Ur = -70.e-3
# reversal potential of exc. (mV)
Ue = 0.e-3
# reversal potential of inh. (mV)
Ui = -75.e-3
# threshold voltage (mV)
Uth = -50.e-3
# reset potential (mV)
Ureset = -60.e-3

# membrane capacitance (F)
C = 120e-12
# leak conductance (S)
Gl = 1. / 140e6
# sample Exc and Inh conductances (nS)
# Be, Bi = .1, -.2

# range of Exc and Inh conductances (nS)
Be_rng = np.array([1.0])  # np.array([0.1, 0.2])*10#np.array([.1, .15, .2, .25])#np.array([0.01, .05, .1, .15, .2, .25])
Bi_rng = np.array([-3.0])  # np.array([-.3, -.4, -.5, -.6, -.7, -.8])*10
# background rate (sp/s)
# params set for Be = 0.1
r_bkg_e = 973.
r_bkg_i = 223.

r_bkg_ca1 = 0.

r_stim_exc = 0.
r_stim_inh = 0.
r_act_inh = 0.
r_act_exc = 0.

if do_for_experiment_type == 'exc-only':
    r_act_exc = 50
if do_for_experiment_type == 'inh-only':
    r_act_inh = 100
if do_for_experiment_type == 'systemic-mean':
    r_act_exc = 50
    r_act_inh = 100
if do_for_experiment_type == 'systemic-fluctuation':
    r_stim_inh = 27218. - r_bkg_i
    r_stim_exc = 30526. - r_bkg_e

evoked_input = 100.
bkg_fr_scale = 0.6
bkg_chg_factor_dict = {-.2: 1.3 * bkg_fr_scale,
                       -.3: 1.7 * bkg_fr_scale,
                       -.4: 1.9 * bkg_fr_scale,
                       -.5: 2.0 * bkg_fr_scale,
                       -.6: 2.1 * bkg_fr_scale,
                       -.7: 2.2 * bkg_fr_scale,
                       -.8: 2.3 * bkg_fr_scale}
# Be_rng = np.array([0.5, 0.55])
# Bi_rng = np.array([-0.1, -0.2])

# background and stimulus conductances (nS)
Be_bkg = 1.
Bi_bkg = -3.
Be_stim = .1

# exc. synaptic time constant (s)
tau_e = 1.e-3
# inh. synaptic time constant (s)
tau_i = 1.e-3

# refractory time (s)
t_ref = 2e-3

# conductance-based alpha-synapses neuron model
neuron_params_default = \
    {'C_m': C * 1e12,
     'E_L': Ur * 1000.,
     'E_ex': Ue * 1000.,
     'E_in': Ui * 1000.,
     'I_e': 0.0,
     'V_m': Ur * 1000.,
     'V_reset': Ureset * 1000.,
     'V_th': Uth * 1000.,
     'g_L': Gl * 1e9,
     't_ref': t_ref * 1000.,
     'tau_syn_ex': tau_e * 1000.,
     'tau_syn_in': tau_i * 1000.}

# -- simulation params

# default synaptic delay (ms)
delay_default = .1

# time resolution of simulations (ms)
dt = .1

# proportion of stimulation
ev_prop = 1.
ev_pop = 'both'  # {'both', 'inh', 'exc'}
ev_arrange = 'random'  # {'overlap', 'nooverlap', 'random', 'ov-noov'}

# amplitude of background input (pA)
# amplitude of perturbation (pA)
I_bkg = 0.0
I_stim_inh = 0.0  # 2.
I_stim_exc = 0.0  # 1.5

# simulation_type = ['control', 'activated']

pert_type = 'spike'  # 'spike' # current or spike

# transitent time to discard the data (ms)
Ttrans = 1000.
# simulation time before perturbation (ms)
Tblank = 1000.
# simulation time of perturbation (ms)
Tstim = 1000.

# number of trials
Ntrials = 20
# rng_conn = np.arange(1, 10.1, 1).astype(int)
II_scale = 1.0
# C_rng = 2
# -- network params

# fraction of Inh neurons
frac = .2
# total population size (Exc + Inh)
N = 200
# size of Inh population
NI = int(frac * N)
# size of Exc population
NE = N - NI

p_ItoE = 1.0
p_ItoI = 1.0

# range of the size of Inh perturbations
nn_stim_rng = (np.array([0, .25, .5, .75, 1]) * NI).astype('int')
# nn_stim_rng = (np.array([0, .25, 0.5])*NI).astype('int')
# nn_stim_rng = (np.array([0.15, .4, .6, .8, .9])*NI).astype('int')

# single cell type
cell_type = 'iaf_cond_alpha'  # 'aeif_cond_alpha'

# record also from ...
rec_from_cond = True
rec_from_pot = True
rec_from_n_neurons = 5
# -- default settings for plotting figures
# (comment out for conventional Python format)
matplotlib.rc('font', serif='sans-serif')

# which time consuming analyses to include?
significance_test = False
normed_firing_rates = False

SIZE = 10
pl.rc('font', size=SIZE)  # controls default text sizes
pl.rc('axes', titlesize=SIZE)  # fontsize of the axes title
pl.rc('axes', labelsize=SIZE)  # fontsize of the x and y labels
pl.rc('xtick', labelsize=SIZE)  # fontsize of the tick labels
pl.rc('ytick', labelsize=SIZE)  # fontsize of the tick labels
pl.rc('legend', fontsize=SIZE)  # legend fontsize
pl.rc('figure', titlesize=SIZE)  # fontsize of the figure title


# half-frame axes
def HalfFrame(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

################################################################################
################################################################################
################################################################################
