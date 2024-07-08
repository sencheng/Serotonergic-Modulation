import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from imp import reload
import defaultParams; reload(defaultParams); from defaultParams import *
import searchParams; reload(searchParams); from searchParams import *
from analysis  import simdata


filename = 'sim_res_Be1.00_Bi-3.00'
dir_name = ''  # Set the directory name based on the simulation output
out_filename = f'{do_for_experiment_type}.pkl'

if not os.path.exists(os.path.join(data_dir, dir_name, filename)):
    raise FileNotFoundError(f'Path does not exist, please look it up in {data_dir}')

data = simdata(os.path.join(data_dir, dir_name, filename))
output = {}
for stim in nn_stim_rng:
    print('stim = {}'.format(stim))
    output[stim] = data._get_ind_fr_pert(stim, dt=1.)
output['triggers'] = {'transient': 1000.,
                      'spont': 2000.,
                      'activated': 3000.,
                      'evoked': 3500.}
with open(out_filename, 'wb') as fl:
    pickle.dump(output, fl)
