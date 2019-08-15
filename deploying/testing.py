from ray.rllib.agents.registry import get_agent_class
import numpy as np
import pickle

config={
    "num_workers": 0,
    "exploration_fraction": 0,
    "exploration_final_eps": 0
     }

cls = get_agent_class('DQN')
agent = cls(env='ECglass-v2',config=config)
agent.restore('/home/raghu/Documents/ray/python/ray/rllib/examples/serving/checkpoint_93/checkpoint-93')
# policy = agent.get_policy().set_epsilon(0.0)
# agent.train()
a_action = agent.compute_action( np.array([16.27,165.82,0,68,1.0]))
print(a_action)


