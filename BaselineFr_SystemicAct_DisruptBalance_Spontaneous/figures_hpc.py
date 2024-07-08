#!/usr/bin/env python3

################################################################################
# -- Preprocessing and analysis of the simulation results
################################################################################

import numpy as np; import pylab as pl; import os, pickle
import matplotlib.pyplot as plt
import json
from scipy.interpolate import interp1d
from scipy.stats import linregress
from scipy import odr
from imp import reload
import defaultParams; reload(defaultParams); from defaultParams import *
import searchParams; reload(searchParams); from searchParams import *
# from figureNumInput import simdata, frchg_vs_EtoI,propposfrchg, frchg, significant_proportions
from analysis import simdata
from sklearn.linear_model import LinearRegression
import copy

RESULT_DIFF_DICT = {}
GAIN_DIFF_DICT = {}
for ee_fac in EEconn_chg_factor:
    RESULT_DIFF_DICT[ee_fac] = {}
    GAIN_DIFF_DICT[ee_fac] = {}

def create_fig_subdir(path, dir_name):
        
        dir_path = os.path.join(path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        
        return dir_path

def boxoff(ax):
    
    """
    Removes the top and right spines of the axes given as inputs, similar to
    boxoff function of MATLAB. Nothing is returned and it works through reference.
    
    Args:
        Axis or array of axes returned for example from plt.subplots().
    """
    
    if len(ax.shape)>1:
        for i in range(ax.shape[0]):            
            for j in range(ax.shape[1]):
                ax[i, j].spines['top'].set_visible(False)
                ax[i, j].spines['right'].set_visible(False)
    else:
        for i in range(ax.shape[0]):
            ax[i].spines['top'].set_visible(False)
            ax[i].spines['right'].set_visible(False)

def to_square_plots(ax):
    
    """
    Make the aspect ratio of xy-axis of a given axes to one, so that they appear
    in square shape.
    
    Args:
        Axis or array of axes returned for example from plt.subplots().
    """

    if len(ax.shape)>1:
        for i in range(ax.shape[0]):            
            for j in range(ax.shape[1]):
                ratio = ax[i, j].get_data_ratio()
                ax[i, j].set_aspect(1.0/ratio)
    else:
        for i in range(ax.shape[0]):
            ratio = ax[i].get_data_ratio()
            ax[i].set_aspect(1.0/ratio)

def get_active_ids(simdata_obj, nn_stim):
    base_interval = [Ttrans+Tblank, Ttrans+Tblank+Tstim]
    evoked_interval = [Ttrans+Tblank+Tstim, Ttrans+Tblank+2*Tstim]
    active_ids = simdata_obj.ids_active_neurons[0]['exc']-1
    return active_ids
def compute_evoked_response(simdata_obj, nn_stim, active_ids):
    base_interval = [Ttrans+Tblank, Ttrans+Tblank+Tstim]
    evoked_interval = [Ttrans+Tblank+Tstim, Ttrans+Tblank+2*Tstim]
    fr_e_base = simdata_obj.get_fr(nn_stim, base_interval)[0].mean(axis=1) #extractig the excitatory population
    fr_e_evoked = simdata_obj.get_fr(nn_stim, evoked_interval)[0].mean(axis=1) #extractig the excitatory population
    return fr_e_evoked[active_ids]-fr_e_base[active_ids], fr_e_base[active_ids], fr_e_evoked[active_ids]

def linear_regression(X, y):
    linear_model = LinearRegression()
    linear_model.fit(X.reshape(-1, 1), y)
    return linear_model.coef_, linear_model.intercept_

def linear_function(pars, x):
        return pars[0]*x + pars[1]

def linear_reg_odr(X, y):
    function = odr.Model(linear_function)
    data  = odr.Data(X, y)
    model = odr.ODR(data, function, beta0=[1., 0.])
    return model.run()

def run_for_each_parset(E_factor, I_factor,
                        Be, Bi, sim_suffix, file_name, file, stim_rate, write_evoked_resp=True):
    cwd = os.getcwd()
    fig_path = os.path.join(fig_dir, fig_initial+sim_suffix)
    os.makedirs(fig_path, exist_ok=True)
    #data_dir = cwd#"/local/mohammad/mnt/sen-cluster/projects/5HT2A/inhibition-stabilized-network-of-spiking-neurons"

    '''
    Analysis directories
    '''

    avg_plots  = "Average_FiringRates_Difference_basecrit"
    avg_plots_subpop = "IncDec_"+avg_plots
    activ_vs_evoked = "Relationship_Activated_vs_Evoked"
    mem_pot_plots = "Membrane_Potentials"
    mem_pot_tr_plots = "Membrane_Potentials_SingleTrial"
    cond_plots = "Conductances"
    cond_tr_plots = "Conductances_SingleTrial"
    gain_plots = "Gains"
    input_rates_plots = "InputRates"

    evoked_response_ctrl = np.zeros((nn_stim_rng.size-1))
    evoked_response_act  = np.zeros((nn_stim_rng.size-1))

    print('\nConductances {} {}'.format(Be, Bi))
    fig_ev, ax_ev = plt.subplots(nrows=3, ncols=nn_stim_rng.size)
    os.chdir(os.path.join(data_dir, res_dir + sim_suffix))
    sim_name = file_name.format(Be, Bi)
    print('Reading {} ...\n'.format(sim_name))
    analyze = simdata(file_name.format(Be, Bi))

    avg_plots_fig = create_fig_subdir(fig_path, avg_plots)
    avg_plots_dec_fig = create_fig_subdir(fig_path, avg_plots + '/dec')
    avg_plots_inc_fig = create_fig_subdir(fig_path, avg_plots + '/inc')
    avg_plots_neu_fig = create_fig_subdir(fig_path, avg_plots + '/neu')
    mem_pot_fig = create_fig_subdir(fig_path, mem_pot_plots)
    gain_fig = create_fig_subdir(fig_path, gain_plots)
    activ_vs_evoked_fig = create_fig_subdir(fig_path, activ_vs_evoked)
    mem_pot_tr_fig = create_fig_subdir(fig_path, mem_pot_tr_plots)
    cond_fig = create_fig_subdir(fig_path, cond_plots)
    cond_tr_fig = create_fig_subdir(fig_path, cond_tr_plots)
    inp_rate_fig = create_fig_subdir(fig_path, input_rates_plots)

    analyze.select_neurons(nn_stim_rng[0], [analyze.trans_interval[0],
                                            analyze.stim_interval[1]], 0.5)
    # analyze.select_neurons(nn_stim_rng[0], analyze.evoke_interval, 2.)
    fr_exc, fr_inh = analyze.get_pop_fr(dt=10.)
    basefrchg_exc, basefrchg_inh = analyze.get_baseline_change()
    RESULT_DIFF_DICT[E_factor][I_factor] = {"exc": basefrchg_exc, "inh": basefrchg_inh}
    gainchg_exc, gainchg_inh = analyze.get_gain_for_plot()
    GAIN_DIFF_DICT[E_factor][I_factor] = {"exc": gainchg_exc, "inh": gainchg_inh}
    ev_exc, ev_inh = analyze.get_gain()
    analyze.get_inc_dec_ids([[analyze.base_interval[0], analyze.base_interval[1]],
                             [analyze.stim_interval[0], analyze.stim_interval[1]]])
    analyze.get_pop_fr_incdec()
    fig_avg_fr, ax_avg_fr = plt.subplots(nrows=1, ncols=nn_stim_rng.size,
                                         sharex=True, sharey=True)
    fig_avg_dec_fr, ax_avg_dec_fr = plt.subplots(nrows=1, ncols=nn_stim_rng.size,
                                                 sharex=True, sharey=True)
    fig_avg_inc_fr, ax_avg_inc_fr = plt.subplots(nrows=1, ncols=nn_stim_rng.size,
                                                 sharex=True, sharey=True)
    fig_avg_neu_fr, ax_avg_neu_fr = plt.subplots(nrows=1, ncols=nn_stim_rng.size,
                                                 sharex=True, sharey=True)
    fig_pot, ax_pot = plt.subplots(nrows=nn_stim_rng.size, ncols=4,
                                   sharex=True, sharey=True,
                                   figsize=(15, 15))
    fig_anti, ax_anti = plt.subplots(ncols=2, sharex=True)
    fig_pot_tr, ax_pot_tr = plt.subplots(nrows=nn_stim_rng.size, ncols=4,
                                        sharex=True, sharey=True,
                                        figsize=(15, 15))
    fig_cond, ax_cond = plt.subplots(nrows=nn_stim_rng.size, ncols=4,
                                   sharex=True, sharey=True,
                                   figsize=(15, 15))
    fig_cond_tr, ax_cond_tr = plt.subplots(nrows=nn_stim_rng.size, ncols=4,
                                           sharex=True, sharey=True,
                                           figsize=(15, 15))
    fig_inp_rate, ax_inp_rate = plt.subplots(nrows=1, ncols=2)
    analyze.plot_pop_fr(ax_avg_fr)
    analyze.plot_subpop_fr(ax_avg_inc_fr, dec_inc='inc')
    analyze.plot_subpop_fr(ax_avg_dec_fr, dec_inc='dec')
    analyze.plot_subpop_fr(ax_avg_neu_fr, dec_inc='neu')
    # analyze.plot_ind_mem_pots(ax_pot)
    # analyze.plot_avg_mem_pots(ax_pot)
    # analyze.plot_trbytr_ind_mem_pots(ax_pot_tr)
    analyze.plot_activated_vs_evoked_rel(ax_anti)
    # analyze.plot_ind_conds(ax_cond)
    # analyze.plot_avg_conds(ax_cond)
    # analyze.plot_trbytr_ind_conds(ax_cond_tr)
    # analyze.plot_input_rate_dist(0, analyze.stim_interval, ax_inp_rate)

    fig_avg_fr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_avg_fr.tight_layout()
    fig_avg_fr.savefig(os.path.join(avg_plots_fig,
                                    "avgfr-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))
    fig_avg_dec_fr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_avg_dec_fr.tight_layout()
    fig_avg_dec_fr.savefig(os.path.join(avg_plots_dec_fig,
                                    "avgfr-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))
    fig_avg_inc_fr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_avg_inc_fr.tight_layout()
    fig_avg_inc_fr.savefig(os.path.join(avg_plots_inc_fig,
                                    "avgfr-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))
    fig_avg_neu_fr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_avg_neu_fr.tight_layout()
    fig_avg_neu_fr.savefig(os.path.join(avg_plots_neu_fig,
                                    "avgfr-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))
    fig_pot.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_pot.tight_layout()
    fig_pot.savefig(os.path.join(mem_pot_fig,
                                 "mempot-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    fig_anti.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_anti.tight_layout()
    fig_anti.savefig(os.path.join(activ_vs_evoked_fig,
                                 "corr-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    fig_pot_tr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_pot_tr.tight_layout()
    fig_pot_tr.savefig(os.path.join(mem_pot_tr_fig,
                                 "mempot-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    fig_cond.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_cond.tight_layout()
    fig_cond.savefig(os.path.join(cond_fig,
                                 "cond-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    fig_cond_tr.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_cond_tr.tight_layout()
    fig_cond_tr.savefig(os.path.join(cond_tr_fig,
                                     "cond-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    fig_inp_rate.suptitle("Be={:.2f}, Bi={:.2f}".format(Be, Bi))
    fig_inp_rate.tight_layout()
    fig_inp_rate.savefig(os.path.join(inp_rate_fig,
                                     "inprate-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)))

    plt.close(fig_avg_fr)
    plt.close(fig_avg_inc_fr)
    plt.close(fig_avg_dec_fr)
    plt.close(fig_avg_neu_fr)
    plt.close(fig_pot)
    plt.close(fig_pot_tr)
    plt.close(fig_anti)
    plt.close(fig_inp_rate)

    fig_ev, ax_ev = plt.subplots(nrows=1, ncols=nn_stim_rng.size,
                                 sharex=True,
                                 sharey=True)
    #ctrl = []
    #act = []
    keys = stim_rate
    for ii in range(nn_stim_rng.size-1):
        evoked_response_ctrl[ii] = ev_exc[nn_stim_rng[0]].mean()
        evoked_response_act[ii]  = ev_exc[nn_stim_rng[ii+1]].mean()
        ctrl = evoked_response_ctrl[ii]/evoked_response_ctrl[ii]
        act  = evoked_response_act[ii]/evoked_response_ctrl[ii]
        ax_ev[ii].plot(keys/1000, ctrl, 'o-', color='black', label='control')
        ax_ev[ii].plot(keys/1000, act, 'o-', color='grey', label='activated')
        ax_ev[ii].set_title("pert={:.0f}%".format(nn_stim_rng[ii+1]/NI*100))
        ax_ev[0].set_ylabel(r'$\Delta FR$')
        ax_ev[nn_stim_rng.size//2].set_xlabel('Evoked inputs (KHz)')
        ax_ev[-1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        to_square_plots(ax_ev)
        boxoff(ax_ev)
        fig_ev.savefig(os.path.join(gain_fig,
                                    "scatter-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)),
                                     format="pdf")
    plt.close(fig_ev)
    os.chdir(cwd)
    return evoked_response_ctrl, evoked_response_act

def plot_gain_modulation(evoked_responses):
    cwd = os.getcwd()
    fig_path = os.path.join(cwd, "evoked_responses_N{}_bkgfac{}_evprop{:.0f}_{:.0f}_{:.0f}".format(N,
                                                                                           bkg_chg_factor[0],
                                                                                           ev_prop*100,
                                                                                           r_stim_inh,
                                                                                           r_stim_exc))
    os.makedirs(fig_path, exist_ok=True)
    print(" Plotting gain modulation curves ...\n")
    keys = list(evoked_responses.keys())
    for ij1, Be in enumerate(Be_rng):
        for ij2, Bi in enumerate(Bi_rng):
            fig_ev, ax_ev = plt.subplots(nrows=1, ncols=nn_stim_rng.size-1,
                                         sharex=True,
                                         sharey=True)
            for ii, nn_stim in enumerate(nn_stim_rng[1:]):
                ctrl = []
                act = []
                for k in keys:
                    ctrl.append(evoked_responses[int(k)]['control'][ij1, ij2, ii]/
                                evoked_responses[int(k)]['control'][ij1, ij2, ii])
                    act.append(evoked_responses[int(k)]['activated'][ij1, ij2, ii]/
                               evoked_responses[int(k)]['control'][ij1, ij2, ii])
                ax_ev[ii].plot(np.array(keys)/1000, ctrl, 'o-', color='black', label='control')
                ax_ev[ii].plot(np.array(keys)/1000, act, 'o-', color='grey', label='activated')
                ax_ev[ii].set_title("pert={:.0f}%".format(nn_stim/NI*100))
            ax_ev[0].set_ylabel(r'$\Delta FR$')
            ax_ev[nn_stim_rng.size//2].set_xlabel('Evoked inputs (KHz)')
            ax_ev[-1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
            to_square_plots(ax_ev)
            boxoff(ax_ev)
            fig_ev.savefig(os.path.join(fig_path,
                                        "scatter-Be{:.2f}-Bi{:.2f}.pdf".format(Be, Bi)),
                                         format="pdf")
            plt.close(fig_ev)
if __name__=='__main__':

    if len(sys.argv) == 1:
        job_id = 0; num_jobs = 1
    else:
        job_id = int(sys.argv[1])
        num_jobs = int(sys.argv[2])


    file_name = 'sim_res_Be{:.2f}_Bi{:.2f}'
    # if os.path.isfile('evoked_responses.dat'):
    #     f =  open('evoked_responses.dat', 'a')
    # else:
    #     f =  open('evoked_responses.dat', 'a')
    #     f.write("g_e\tg_i\tpert\tevoked_fr\ttrial\tscenario\tfr_change\n")
    f = None
    ctrl_act_evoked_frs = {}

    Be_rng_comb, Bi_rng_comb, EE_probchg_comb, EI_probchg_comb, II_condchg_comb, E_extra_comb, bkg_chg_comb, evfr_chg_comb = np.meshgrid(Be_rng, Bi_rng, EEconn_chg_factor, EIconn_chg_factor, IIconn_chg_factor, E_extra_stim_factor, bkg_chg_factor, evoked_fr_chg_factor)

    Be_rng_comb = Be_rng_comb.flatten()[job_id::num_jobs]
    Bi_rng_comb = Bi_rng_comb.flatten()[job_id::num_jobs]
    EE_probchg_comb = EE_probchg_comb.flatten()[job_id::num_jobs]
    EI_probchg_comb = EI_probchg_comb.flatten()[job_id::num_jobs]
    II_condchg_comb = II_condchg_comb.flatten()[job_id::num_jobs]
    #fr_chg_comb = fr_chg_comb.flatten()[job_id::num_jobs]
    E_extra_comb = E_extra_comb.flatten()[job_id::num_jobs]
    bkg_chg_comb = bkg_chg_comb.flatten()[job_id::num_jobs]
    evfr_chg_comb = evfr_chg_comb.flatten()[job_id::num_jobs]

    if pert_type == 'spike':
        stim_inh, stim_exc = r_stim_inh, r_stim_exc
    else:
        stim_inh, stim_exc = I_stim_inh, I_stim_exc

    for ij1 in range(EE_probchg_comb.size):

        sim_suffix_comp = sim_suffix.format(EE_probchg_comb[ij1], EI_probchg_comb[ij1], ev_arrange, pert_type, N, evfr_chg_comb[ij1]*100, ev_prop*100, ev_pop, C_rng.size, Ntrials, stim_inh/1.e3, stim_exc/1.e3, r_act_inh*EI_probchg_comb[ij1], r_act_exc*EE_probchg_comb[ij1], II_scale, bkg_chg_comb[ij1], p_ItoI)
        run_for_each_parset(EE_probchg_comb[ij1], EI_probchg_comb[ij1],
                            Be_rng_comb[ij1], Bi_rng_comb[ij1], sim_suffix_comp, file_name, f, evfr_chg_comb[ij1]*100, True)
        #ctrl, act = run_for_each_parset(sim_suffix, file_name, f, True)
        #single_dict = {"control": ctrl, "activated": act}
        #ctrl_act_evoked_frs[evfr_chg_comb[ij1]*100] = single_dict

    #plot_gain_modulation(ctrl_act_evoked_frs)
    # with open('final_data.pickle', 'wb') as handle:
    #     pickle.dump(ctrl_act_evoked_frs, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(os.path.join(data_dir, "diff_data"), "wb") as fl:
        pickle.dump(RESULT_DIFF_DICT, fl)
    with open(os.path.join(data_dir, "gain_data"), "wb") as fl:
        pickle.dump(GAIN_DIFF_DICT, fl)
