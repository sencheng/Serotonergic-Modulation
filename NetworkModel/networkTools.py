
################################################################################
# -- Tools for simulating networks of spiking neurons using the NEST simulator
################################################################################

import numpy as np; import pylab as pl; import time, os, sys
from imp import reload
import defaultParams; reload(defaultParams); from defaultParams import *;
import nest

# --- NEST initialization
def _nest_start_(n_cores=n_cores):
    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": dt,
                        "print_time": False,
                        "overwrite_files": True,
                        'local_num_threads': n_cores})
    nest.set_verbosity("M_WARNING")

# --- Get simulation time of the network
def _simulation_time_():
    return nest.GetStatus([0])[0]['time']

# --- Define nest-compatible "Connect"
bNestUseConvergentConnect = "ConvergentConnect" in dir(nest)

def ConvConnect(arg0, arg1, syn_spec='static_synapse', *args):
    if bNestUseConvergentConnect:
        return nest.ConvergentConnect(arg0, arg1, model=syn_spec)
    else:
        return nest.Connect(arg0, arg1, syn_spec=syn_spec)

def DivConnect(arg0, arg1, syn_spec='static_synapse', *args):
    if bNestUseConvergentConnect:
        return nest.DivergentConnect(arg0, arg1, model=syn_spec)
    else:
        return nest.Connect(arg0, arg1, syn_spec=syn_spec)


# --- Making neurons
def _make_neurons_(N, neuron_model="iaf_cond_alpha", myparams={}):
    nest.SetDefaults(neuron_model, neuron_params_default)
    neurons = nest.Create(neuron_model, N)
    if myparams != {}:
        for nn in range(N):
            for kk in myparams.keys():
                nest.SetStatus([neurons[nn]], {kk:myparams[kk][nn]})
    return neurons

# --- Generating (poisson) inputs and setting their firing rates
def _poisson_inp_(N):
    poisson_inp = nest.Create("poisson_generator", N)
    return poisson_inp

def _set_rate_(neurons, rates):
    for ii, nn in enumerate(neurons):
        nest.SetStatus([nn], {'rate':rates[ii]})

# --- Copy to a parrot neuron (mirroring every spike)
def _copy_to_parrots_(pre_pop):
    parrots = nest.Create('parrot_neuron', len(pre_pop))
    nest.Connect(pre_pop, parrots, conn_spec='one_to_one')
    return parrots

# --- Recording and reading spikes and voltages
def _recording_spikes_(neurons, start=0., stop=np.inf, to_file=False, to_memory=True):
    spikes = nest.Create("spike_detector", 1)
    nest.SetStatus(spikes, {"withtime":True,
                        "label":'spike-det',
                        "to_file":to_file,
                        "to_memory":to_memory,
                        "start": start,
                        "stop": stop})

    ConvConnect(neurons, spikes)
    return spikes

def _recording_gin_(neurons, start=0., stop=np.inf, to_file=False, to_memory=True):
    mm = nest.Create("multimeter", 1)
    nest.SetStatus(mm, {"record_from": ["g_in", "g_ex"],
                        "withtime":True,
                        "label":'current',
                        "to_file":to_file,
                        "to_memory":to_memory,
                        "start": start,
                        "stop": stop})

    ConvConnect(mm, neurons)
    return mm

def _recording_voltages_(neurons, start=0., stop=np.inf):
    voltages = nest.Create("voltmeter")
    nest.SetStatus(voltages, {"withtime":True,
                            "label":'volt-meter',
                            "to_file":False,
                            "to_memory":True,
                            "start": start,
                            "stop": stop})
    DivConnect(voltages, neurons)
    return voltages

def _reading_spikes_(spikes):
    spike_data = nest.GetStatus(spikes)[0]['events']
    return spike_data

def _reading_currents_(currs):
    return nest.GetStatus(currs)[0]['events']

def _reading_voltages_(voltages):
    voltage_data = nest.GetStatus(voltages)[0]['events']
    return voltage_data

# --- Connect
def _connect_(xx, yy, ww, dd=delay_default):
    nest.Connect(xx, yy, syn_spec = {'weight':ww, 'delay':dd})

# --- Connect population A to population B with weight matrix W
def _connect_pops_(pre_pop, post_pop, weight, syn_model='static'):
    # for ii, nn in enumerate(pre_pop):
        # ww = weight[ii]
    dd = dt + delay_default*np.ones_like(weight.T)
    # nest.DivergentConnect([nn], post_pop, weight=ww.tolist(), delay=dd.tolist())
    syn_dict = {"weight": weight.T, "delay": dd}
    nest.Connect(pre_pop, post_pop, syn_spec=syn_dict)

# --- Run the simulation for the duration of T (ms)
def _run_simulation_(T):
    nest.Simulate(T)

################################################################################
################################################################################
################################################################################
