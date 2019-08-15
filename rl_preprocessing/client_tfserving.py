import requests
import json
import pandas as pd
import gym
env = gym.make("ECglass-v2")
rewards = 0
def get_action(obs):
    url = 'http://localhost:8501/v1/models/rl_model:predict'
    data = {
        "inputs": {
            "is_training": False,
            "observations": [
                obs
            ],
            "default_policy/eps:0": 0,
            "default_policy/stochastic:0": True
        }
    }
    post_fields = json.dumps(data)

    r = requests.post(url, data=post_fields)
    return (r.json()['outputs']['actions'][0])
obs = env.reset()
# obs =[23.55, 91.55, 506.0, 205.0, 1.0]
# print(get_action(obs))

# print(obs, reward, done, info)

df = pd.read_csv('observations_v2.csv')
for i,row in df.iterrows():
    # print(row.tolist(),get_action(row.tolist()))
    obs, reward, done, info = env.step(get_action(row.tolist()))
    print(obs,get_action(row.tolist()), reward, done, info)
    rewards += reward
    if done:
        print("Total reward:", rewards)