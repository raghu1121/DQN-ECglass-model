# RL_model
Reinforcement  learning model for EC glass
This repo contains the scripts related to the control of EC glass with Reinforcement learning approach.


The environment creation for EC glass is in a seperate repo, where DGP values(glare perception based on the state 
of the environment) are extracted from HDRs(34 Million) to rl_preprocessing folder for preprocessing and postprocessing.

The actual model of DQN including with variants such as Dueling and Prioritized experience replay are configured, tuned in 
cluster with DGX and V100 GPUs. They can be found in the Jobs folder


The Open AI GYM environment is adapted for EC glass environment with suitable initializations and step() function wih rewards. This can found
in the GYM folder.
