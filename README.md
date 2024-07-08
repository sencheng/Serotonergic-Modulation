**Description**

This repository contains a balanced network of inhibitory and excitatory neurons adapted from "Sadeh, Sadra, et al. 
"Assessing the role of inhibition in stabilizing neocortical networks requires large-scale perturbation of the 
inhibitory population." Journal of Neuroscience 37.49 (2017): 12050-12067." and shared under
https://figshare.com/articles/Inhibitory_Stabilized_Network_models/4823212.
Model neurons here are spiking from the integrate-and-fire family. 
We used this work to model and investigate the impact of activating 5HT2A receptors in the excitatory, 
inhibitory population as well as both populations simultaneously.

**Requirements**

For running the codes here, you need to have Python (v 3.8.10) installed. In addition, you need particular python packages that exist in the *requirements.txt*. You can directly use this .txt file along with *pip* to install all necessary packages at once using `pip install -r requirements.txt`.

In addition, you need to have NEST (v 2.20.1) installed. Instructions regarding installation of NEST and its source code you can find under https://nest-simulator.readthedocs.io/en/v2.20.1/.

**How to generate figures for the related publication**

Please checkout to the branches below and follow the instructions to run simulations and generate the figures, 
which are presented in the manuscript:

For *Figure 5* please checkout to `simexp/NetworkModel`

For *Extended Data Fig. 9 panel a* please checkout to `simexp/PertStrength_Research_Exc`

For *Extended Data Fig. 9 panel b* please checkout to `simexp/PertStrength_Research_Inh`

For *Extended Data Fig. 11 panel a* please checkout to `simexp/BaselineFr_SystemicAct_DisruptBalance_Spontaneous`

For *Extended Data Fig. 11 panel b* please checkout to `simexp/BaselineFr_SystemicAct_DisruptBalance_Evoked`