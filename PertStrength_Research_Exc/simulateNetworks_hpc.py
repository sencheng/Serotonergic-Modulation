################################################################################
# -- Simulating Exc-Inh spiking networks in response to inhibitory perturbation
################################################################################

import time, os, sys, pickle
from imp import reload
import defaultParams; reload(defaultParams); from defaultParams import *;
import searchParams; reload(searchParams); from searchParams import *;
import networkTools; reload(networkTools); import networkTools as net_tools
import nest
import copy

cwd = os.getcwd()

t_init = time.time()

################################################################################
#### functions

# -- rectification
def _rect_(xx): return xx*(xx>0)

# -- generates the weight matrix
def _mycon_(N1, N2, B12, B12_std, pr=1.):
    zb = np.random.binomial(1, pr, (N1,N2))
    zw = np.sign(B12) * _rect_(np.random.normal(abs(B12),abs(B12_std),(N1,N2)))
    zz = zb* zw
    return zz

def _guasconn_(N1, N2, B12, conn_std, pr=1.):
    
    '''
    This function is very similar the "_mycon_". The reason I added this function
    is that the sparse connections in "_mycon_" are created using a binomial
    process. Changing the variance in binomial process requires changing "n, p",
    which consequently changes the total number of input connections and thus
    lead to a different network behavior. To overcome this limitation, I used 
    a Guassian process instead of the binomial one, which enables me to change
    the variance while keeping the total number of incoming connections almost
    fixed.
    '''
    
    zb = np.zeros((N1, N2))
    num_in = np.random.normal(N1*pr, conn_std, N2)
    num_in[num_in<0] = 0
    num_in_i = num_in.astype(int)
    
    for n2 in range(N2):
        rp = np.random.permutation(N1)[:num_in_i[n2]]
        zb[rp, n2] = 1
    
    zw = np.sign(B12) * _rect_(np.random.normal(abs(B12),abs(B12/5),(N1,N2)))
    zz = zb * zw
    return zz

# -- runs a network simulation with a defined inh perturbation
bw = 50.
def myRun(rr1, rr2, dc1, dc2, W, rng_c, Tstim=Tstim, Tblank=Tblank, Ntrials=Ntrials, bw = bw, \
            rec_conn={'EtoE':1, 'EtoI':1, 'ItoE':1, 'ItoI':1}, nn_stim=0, evfr_chg_fac=1.0):

    SPD = {}; CURR = {}; POT = {}
    # -- simulating network for N-trials
    for tri in range(Ntrials*(rng_c-1), Ntrials*rng_c):
        print('')
        print('# -> trial # ', tri+1)
        # -- restart the simulator
        net_tools._nest_start_()
        init_seed = np.random.randint(1, 1234, n_cores)
        print('init_seed = ', init_seed)
        nest.SetStatus([0],[{'rng_seeds':init_seed.tolist()}])

        # -- exc & inh neurons
        if 'aeif' in cell_type:
            exc_neurons = net_tools._make_neurons_(NE, neuron_model=cell_type, \
            myparams={'b':NE*[0.], 'a':NE*[0.]})
            inh_neurons = net_tools._make_neurons_(NI, neuron_model=cell_type, \
            myparams={'b':NE*[0.],'a':NE*[0.]})
        else:
            exc_neurons = net_tools._make_neurons_(NE, neuron_model=cell_type)
            inh_neurons = net_tools._make_neurons_(NI, neuron_model=cell_type)
        '''     
        np.random.seed(tri+1)
        
        p_conn = 0.15
        W_EtoE = _mycon_(NE, NE, Bee, Bee/5, p_conn*EE_probchg_comb[ij1])
        W_EtoI = _mycon_(NE, NI, Bei, Bei/5, p_conn*EI_probchg_comb[ij1])
        W_ItoE = _mycon_(NI, NE, Bie, Bie/5, 1.)
        W_ItoI = _mycon_(NI, NI, Bii, Bii/5, 1.)
        '''
        W_EtoE, W_EtoI, W_ItoE, W_ItoI = W[0], W[1], W[2], W[3]
        all_neurons = exc_neurons + inh_neurons

        # -- recurrent connectivity
        if rec_conn['EtoE']:
            net_tools._connect_pops_(exc_neurons, exc_neurons, W_EtoE)
        if rec_conn['EtoI']:
            net_tools._connect_pops_(exc_neurons, inh_neurons, W_EtoI)
        if rec_conn['ItoE']:
            net_tools._connect_pops_(inh_neurons, exc_neurons, W_ItoE)
        if rec_conn['ItoI']:
            net_tools._connect_pops_(inh_neurons, inh_neurons, W_ItoI)
        
        pert_exc_id = int(nn_stim*NE/NI)
        if nn_stim == 0:
            rec_subset_exc = np.concatenate((exc_neurons[0:rec_from_n_neurons], exc_neurons[-rec_from_n_neurons:])).tolist()
        elif nn_stim < NI:
            rec_subset_exc = np.concatenate((exc_neurons[0:rec_from_n_neurons], exc_neurons[pert_exc_id:pert_exc_id+rec_from_n_neurons], exc_neurons[-rec_from_n_neurons:])).tolist()
        else:
            rec_subset_exc = np.concatenate((exc_neurons[0:rec_from_n_neurons], exc_neurons[-rec_from_n_neurons:])).tolist()
        # -- recording spike data
        spikes_all = net_tools._recording_spikes_(neurons=all_neurons)

        # -- recording inhibitory current data
        print(rec_subset_exc)
        if rec_from_cond:
            currents = net_tools._recording_gin_(neurons=rec_subset_exc)
            
        # -- recording voltages
        if rec_from_pot:
            voltages = net_tools._recording_voltages_(neurons=rec_subset_exc)
        # -- background input
        pos_inp_e = nest.Create("poisson_generator", N)
        pos_inp_i = nest.Create("poisson_generator", N)
        
        # -- external stimulus
        stim_inp = nest.Create("poisson_generator", N)
        
        # -- dc input
        dc_inp = nest.Create("dc_generator", N)

        for ii in range(N):
            nest.Connect([pos_inp_e[ii]], [all_neurons[ii]], \
            syn_spec = {'weight':Be_bkg, 'delay':delay_default})
            nest.Connect([pos_inp_i[ii]], [all_neurons[ii]], \
            syn_spec = {'weight':Bi_bkg, 'delay':delay_default})
            nest.Connect([dc_inp[ii]], [all_neurons[ii]])
        
        for ii in range(N):
            nest.Connect([stim_inp[ii]], [all_neurons[ii]], \
                         syn_spec = {'weight':Be_bkg, 'delay':delay_default})
        '''
        # -- simulating network for N-trials
        for tri in range(Ntrials):
            print('')
            print('# -> trial # ', tri+1)
        '''
        ## transient
        for ii in range(N):
            nest.SetStatus([pos_inp_e[ii]], {'rate':rr1[0][ii]})
            nest.SetStatus([pos_inp_i[ii]], {'rate':rr1[1][ii]})
            nest.SetStatus([dc_inp[ii]], {'amplitude':dc1[ii]})
        net_tools._run_simulation_(Ttrans)

        ## baseline
        for ii in range(N):
            nest.SetStatus([pos_inp_e[ii]], {'rate':rr1[0][ii]})
            nest.SetStatus([pos_inp_i[ii]], {'rate':rr1[1][ii]})
            nest.SetStatus([dc_inp[ii]], {'amplitude':dc1[ii]})
        net_tools._run_simulation_(Tblank)

        ## perturbing a subset of inh/exc
        for ii in range(N):
            nest.SetStatus([pos_inp_e[ii]], {'rate':rr2[0][ii]})
            nest.SetStatus([pos_inp_i[ii]], {'rate':rr2[1][ii]})
            nest.SetStatus([dc_inp[ii]], {'amplitude':dc2[ii]})
        net_tools._run_simulation_(Tstim)
        
        ## evoked
        if ev_arrange == 'nooverlap':
            sel_exc_ids = np.array(exc_neurons[-int(NE*ev_prop):])
            sel_inh_ids = np.array(inh_neurons[-int(NI*ev_prop):])
        elif ev_arrange == 'overlap':
            sel_exc_ids = np.array(exc_neurons[:int(NE*ev_prop)])
            sel_inh_ids = np.array(inh_neurons[:int(NI*ev_prop)])
        elif ev_arrange == 'random':
            sel_exc_ids = np.random.choice(exc_neurons, int(NE*ev_prop), replace=False)
            sel_inh_ids = np.random.choice(inh_neurons, int(NI*ev_prop), replace=False)
        elif ev_arrange == 'ov-noov':
            sel_exc_ids = np.array(exc_neurons[int(NE*ev_prop/2):int(NE*ev_prop*3/2)])
            sel_inh_ids = np.array(inh_neurons[int(NI*ev_prop/2):int(NI*ev_prop*3/2)])

        if (ev_pop == 'exc') | (ev_pop == 'both'):
            for ii in range(sel_exc_ids.size):
                nest.SetStatus([stim_inp[sel_exc_ids[ii]-1]], {'rate':evoked_input*evfr_chg_fac,
                                                             'start':Ttrans+Tblank+Tstim,
                                                             'stop':Ttrans+Tblank+Tstim+Tblank/2})
        if (ev_pop == 'inh') | (ev_pop == 'both'):
            for ii in range(sel_inh_ids.size):
                nest.SetStatus([stim_inp[sel_inh_ids[ii]-1]], {'rate':evoked_input*evfr_chg_fac,
                                                             'start':Ttrans+Tblank+Tstim,
                                                             'stop':Ttrans+Tblank+Tstim+Tblank/2})
        net_tools._run_simulation_(Tblank)

        # -- reading out spiking activity
        # spd = net_tools._reading_spikes_(spikes_all)
        SPD[tri] = net_tools._reading_spikes_(spikes_all)
        
        # -- reading out currents
        if rec_from_cond:
            # curr = net_tools._reading_currents_(currents_all)
            CURR[tri] = net_tools._reading_currents_(currents)
        if rec_from_pot:
            POT[tri] = net_tools._reading_voltages_(voltages)
        '''
        # -- computes the rates out of spike data in a given time interval
        def _rate_interval_(spikedata, T1, T2, bw=bw):
            tids = (spikedata['times']>T1) * (spikedata['times']<T2)
            rr = np.histogram2d(spikedata['times'][tids], spikedata['senders'][tids], \
                 range=((T1,T2),(1,N)), bins=(int((T2-T1)/bw),N))[0] / (bw/1e3)
            return rr
        '''
        rout_blank = np.zeros((Ntrials, int(Tblank / bw), N))
        rout_stim = np.zeros((Ntrials, int(Tstim / bw), N))
        '''
        for tri in range(Ntrials):
            Tblock = Tstim+Tblank+Ttrans
            rblk = _rate_interval_(spd, Tblock*tri+Ttrans, Tblock*tri+Ttrans+Tblank)
            rstm = _rate_interval_(spd, Tblock*tri+Ttrans+Tblank, Tblock*(tri+1))
            rout_blank[tri,:,:] = rblk
            rout_stim[tri,:,:] = rstm

        print('##########')
        print('## Mean firing rates {Exc | Inh (pert.) | Inh (non-pert.)}')
        print('## Before pert.: ', \
        np.round(rout_blank[:,:,0:NE].mean(),1), \
        np.round(rout_blank[:,:,NE:NE+nn_stim].mean(),1), \
        np.round(rout_blank[:,:,NE+nn_stim:].mean(),1) )
        print('## After pert.: ', \
        np.round(rout_stim[:,:,0:NE].mean(),1), \
        np.round(rout_stim[:,:,NE:NE+nn_stim].mean(),1), \
        np.round(rout_stim[:,:,NE+nn_stim:].mean(),1) )
        print('##########')
        '''
    if rec_from_cond & rec_from_pot:
        #return rout_blank, rout_stim, SPD, CURR
        return [], [], SPD, CURR, POT
    else:
        #return rout_blank, rout_stim, SPD
        return [], [], SPD

def simulate(job_id, num_jobs, sim_suffix):
    Be_rng_comb, Bi_rng_comb, EE_probchg_comb, EI_probchg_comb,\
        II_condchg_comb, E_extra_comb, bkg_chg_comb, C_rng_comb, evfr_chg_comb \
        = np.meshgrid(Be_rng, Bi_rng, EEconn_chg_factor, EIconn_chg_factor,
                      IIconn_chg_factor, E_extra_stim_factor, bkg_chg_factor, C_rng, evoked_fr_chg_factor)

    Be_rng_comb = Be_rng_comb.flatten()[job_id::num_jobs]
    Bi_rng_comb = Bi_rng_comb.flatten()[job_id::num_jobs]
    EE_probchg_comb = EE_probchg_comb.flatten()[job_id::num_jobs]
    EI_probchg_comb = EI_probchg_comb.flatten()[job_id::num_jobs]
    II_condchg_comb = II_condchg_comb.flatten()[job_id::num_jobs]
    #fr_chg_comb = fr_chg_comb.flatten()[job_id::num_jobs]
    E_extra_comb = E_extra_comb.flatten()[job_id::num_jobs]
    bkg_chg_comb = bkg_chg_comb.flatten()[job_id::num_jobs]
    C_rng_comb = C_rng_comb.flatten()[job_id::num_jobs]
    evfr_chg_comb = evfr_chg_comb.flatten()[job_id::num_jobs]
    #pert_comb = pert_comb.flatten()[job_id::num_jobs]
    #E_pert_frac = 1.0
    
    for ij1 in range(Be_rng_comb.size):
        
        Be, Bi = Be_rng_comb[ij1], Bi_rng_comb[ij1]
        Bee, Bei = Be, Be
        Bie, Bii = Bi, Bi*II_scale
        # print("\n\nInh. conductance = {:.2f}, background factor = {:.2f}\n\n".format(Bi, bkg_chg_factor_dict[Bi]))
    
        print('####################')
        print('### (Be, Bi, EvFr): ', Be, Bi, evfr_chg_comb[ij1])
        print('####################')
        sim_res = {}
        for nn_stim in nn_stim_rng:
    
            print('\n # -----> size of pert. inh: ', nn_stim)
            #nn_stim_inh = nn_stim_rng[1]
            
            # for rng_c in rng_conn:
            rng_c = C_rng_comb[ij1]
            np.random.seed(rng_c)
            print('Resetting random seed ...')
            # -- L23 recurrent connectivity
            p_conn = 0.15
            W_EtoE = _mycon_(NE, NE, Bee, Bee/5, p_conn)#*EE_probchg_comb[ij1])
            W_EtoI = _mycon_(NE, NI, Bei, Bei/5, p_conn)#*EI_probchg_comb[ij1])
            W_ItoE = _mycon_(NI, NE, Bie, Bie/5, p_ItoE)
            W_ItoI = _mycon_(NI, NI, Bii, Bii/5, p_ItoI)
            # -- running simulations
            #np.random.seed((C_rng_comb[ij1]+1)*2)
            r_extra = np.zeros(N)
            r_extra_inh = np.zeros(N)
            r_extra_exc = np.zeros(N)
            I_extra = np.zeros(N)
            np.random.seed(100)
            if pert_type == 'spike':
                stim_inh, stim_exc = r_stim_inh, r_stim_exc
            else:
                stim_inh, stim_exc = I_stim_inh, I_stim_exc
            
            if pert_type == 'spike':
                print("Perturbation type {}".format(pert_type))
                r_extra[NE:NE+nn_stim] = r_stim_inh#*np.random.uniform(0.8, 1.2, size=nn_stim)#np.random.normal(loc=1, scale=0.2, size=nn_stim)
                r_extra[0:int(nn_stim*NE/NI)] = r_stim_exc
                r_extra_inh[NE:NE+nn_stim] = r_stim_inh
                r_extra_inh[0:int(nn_stim*NE/NI)] = r_stim_inh
                r_extra_exc[NE:NE+nn_stim] = r_stim_exc + r_act_inh#*EI_probchg_comb[ij1]
                r_extra_exc[0:int(nn_stim*NE/NI)] = r_stim_exc + r_act_exc*EE_probchg_comb[ij1]
            elif pert_type == 'current':
                print("Perturbation type {}".format(pert_type))
                I_extra[NE:NE+nn_stim] = I_stim_inh
                I_extra[0:int(nn_stim*NE/NI)] = I_stim_exc
            else:
                print("Wrong perturbation type {}".format(pert_type))
                    
            #r_bkg_e = r_bkg*bkg_chg_comb[ij1]; r_bkg_i = r_bkg*bkg_chg_comb[ij1]
            # r_bkg_e = r_bkg*bkg_chg_factor_dict[Bi]
            # r_bkg_i = r_bkg*bkg_chg_factor_dict[Bi]
            rr1_e = np.hstack((r_bkg_e*np.ones(NE),
                               r_bkg_e*np.ones(NI)))
            rr1_i = np.hstack((r_bkg_i*np.ones(NE),
                               r_bkg_i*np.ones(NI)))
            rr1 = [rr1_e, rr1_i]
            rr2_e = rr1_e + r_extra_exc
            rr2_i = rr1_i + r_extra_inh
            rr2 = [rr2_e, rr2_i]
            
            I_bkg_e = I_bkg#*bkg_chg_comb[ij1]
            I_bkg_i = I_bkg#*bkg_chg_comb[ij1]
            dc1 = np.hstack((I_bkg_e*np.ones(NE), I_bkg_i*np.ones(NI)))
            dc2 = dc1 + I_extra
    
            tmp_out = myRun(rr1, rr2, dc1, dc2,
                            (W_EtoE, W_EtoI, W_ItoE, W_ItoI), rng_c,
                            nn_stim=nn_stim, evfr_chg_fac=evfr_chg_comb[ij1])
            # if rng_c == rng_conn[0]:
            if rec_from_cond & rec_from_pot:
                sim_res[nn_stim] = [tmp_out[0], tmp_out[1], {}, {}, {}]
            else:
                sim_res[nn_stim] = [tmp_out[0], tmp_out[1], {}]
            for tr in tmp_out[2].keys():
                sim_res[nn_stim][2][tr] = copy.copy(tmp_out[2][tr])
            if rec_from_cond & rec_from_pot:
                for tr in tmp_out[3].keys():
                    sim_res[nn_stim][3][tr] = copy.copy(tmp_out[3][tr])
                    sim_res[nn_stim][4][tr] = copy.copy(tmp_out[4][tr])
    
        sim_res['nn_stim_rng'], sim_res['Ntrials'] = nn_stim_rng, Ntrials
        sim_res['N'], sim_res['NE'], sim_res['NI'] = N, NE, NI
        sim_res['Tblank'], sim_res['Tstim'], sim_res['Ttrans'] = Tblank, Tstim, Ttrans
        sim_res['W_EtoE'], sim_res['W_EtoI'], sim_res['W_ItoE'], sim_res['W_ItoI'] = W_EtoE, W_EtoI, W_ItoE, W_ItoI
        
        # -- result path
        sim_suffix_comp = sim_suffix.format(EE_probchg_comb[ij1], EI_probchg_comb[ij1], ev_arrange, pert_type, N, evfr_chg_comb[ij1]*100, ev_prop*100, ev_pop, C_rng.size, Ntrials, stim_inh/1.e3, stim_exc/1.e3, r_act_inh*EI_probchg_comb[ij1], r_act_exc*EE_probchg_comb[ij1], II_scale, bkg_chg_comb[ij1], p_ItoI)
        # sim_suffix = "-{}-N{}-EvFr{:.0f}-EvPr{:.0f}-nummodel{}-Ntr{}-RNG{}-I_pert{:.0f}-E_pert{:.0f}-II{:.1f}-bkgfac{:.2f}".format(pert_type, N, evfr_chg_comb[ij1]*100, ev_prop*100, rng_conn.size, Ntrials, C_rng_comb[ij1], stim_inh, stim_exc, II_scale, bkg_chg_comb[ij1])
        res_path = os.path.join(data_dir, res_dir+sim_suffix_comp)
        if not os.path.exists(res_path): os.makedirs(res_path, exist_ok=True)
    
        os.chdir(res_path)
        sim_name = 'sim_res_Be{:.2f}_Bi{:.2f}_Mo{:d}'.format(Be, Bi, rng_c)
        fl = open(sim_name, 'wb'); pickle.dump(sim_res, fl); fl.close()
    
    t_end = time.time()
    print('took: ', np.round((t_end-t_init)/60), ' mins')

################################################################################

if len(sys.argv) == 1:
    job_id = 0; num_jobs = 1
else:
    job_id = int(sys.argv[1])
    num_jobs = int(sys.argv[2])
    
simulate(job_id, num_jobs, sim_suffix)

os.chdir(cwd)
