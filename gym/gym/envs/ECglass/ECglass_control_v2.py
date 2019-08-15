import gym
from gym import spaces, logger
from gym.utils import seeding
import pandas as pd
import numpy as np
from itertools import chain
import json
import os


# import modin.pandas as pd

class EcGlassEnv_v2(gym.Env):
    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.df_obs = pd.read_csv(self.path + '/assets/observations_v2.csv')
        self.df_env = pd.read_csv(self.path + '/assets/env_v2.csv')
        low = np.array([-90, 0, 0, 0, 0])
        high = np.array([90, 360, 1500, 1000, 1])
        self.action_space = spaces.Discrete(64)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # self.dgp_threshold = 0.45
        self.dmin = 0.2
        self.dmax = 0.36
        self.pmin = -1
        self.pmax = 1
        self.lmin = 300
        self.lmax = 3000
        self.qmax = 3.351
        self.qsmax = 2.917
        self.seed()
        self.state = None
        self.observation = None
        self.count = 0
        self.total_reward = 0
        self.total_reward_min = 3188
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        self.r5 = 0
        self.results = pd.DataFrame(columns=['observation', 'state', 'action', 'reward'])

    def getState(self, observation, action):

        filtered = self.df_env[
            (self.df_env['altitude'] == observation[0]) & (self.df_env['azimuth'] == observation[1]) & (
                    self.df_env['dir'] == observation[2]) & (
                    self.df_env['diff'] == observation[3]) & (self.df_env['Occupancy'] == observation[4]) & (
                    self.df_env['action'] == action)]
        return list(chain.from_iterable(filtered.iloc[:, 5:18].values))

    def action_mapping(self, action):
        with open(self.path + '/assets/action_mapping.json') as f:
            dict = json.load(f)
        zeros = dict[str(action)].count('0')
        ones = dict[str(action)].count('1')
        twos = dict[str(action)].count('2')
        threes = dict[str(action)].count('3')
        # return ((2 / 3) * zeros + (1 / 3) * ones + (1 / 5) * twos)
        return [zeros, ones, twos, threes]

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        self.observation = self.df_obs.iloc[self.count, :].tolist()
        # print(self.observation)
        self.state = self.getState(self.observation, action)
        # print(self.state)
        qh, qc = self.state[10:12]
        qs = self.state[12]
        total_p = 0
        reward5 = 0
        reward4 = 0
        reward1 = 0
        reward2 = 0
        reward3 = 0
        lmax_reward = 9
        pmax_reward = 4
        if self.observation[4] > 0:

            # glare
            for d in self.state[0:4]:
                if d <= self.dmax:
                    reward1 += (d / self.dmin) - 1
                else:
                    reward1 += -(d / self.dmin)

            # daylight availability.
            for l in self.state[4:6]:
                if l <= self.lmax:
                    reward2 += (l / self.lmin) - 1
                else:
                    reward2 += -(l / self.lmin)
            reward2 = reward2 / lmax_reward

            # Thermal comfort
            for p in self.state[6:10]:
                reward3 += 1 - abs(p)
                total_p += p
            reward3 = reward3 / pmax_reward

            # Energy load
            reward4 = -(qh + 1.5 * qc) / self.qmax

            # solar load
            if total_p / 4 > 1:
                reward5 = -(qs / self.qsmax)
            elif total_p / 4 < -1:
                reward5 = (qs / self.qsmax)

            reward = (reward1 + reward2 + reward3 + reward4 + reward5)
        else:

            for p in self.state[6:10]:
                total_p += p

            # Energy load
            reward4 = -(qh + 1.5 * qc) / self.qmax

            # solar load
            if total_p / 4 > 1:
                reward5 = -(qs / self.qsmax)
            elif total_p / 4 < -1:
                reward5 = (qs / self.qsmax)

            reward = (reward4 + reward5)

        done = False
        self.count = self.count + 1
        if self.count == 8759:
            done = True
            self.count = 0
            if self.total_reward >= self.total_reward_min:
                self.results.to_csv(
                    'results_' + str(self.total_reward) + '.csv')
                self.total_reward_min = self.total_reward
            self.results = pd.DataFrame()
            self.r1 = 0
            self.r2 = 0
            self.r3 = 0
            self.r4 = 0
            self.r5 = 0
            self.total_reward = 0

        self.total_reward += reward
        self.r1 += reward1
        self.r2 += reward2
        self.r3 += reward3
        self.r4 += reward4
        self.r5 += reward5


        self.results = self.results.append(
            {'observation': self.observation, 'state': self.state, 'action': action, 'reward': reward},
            ignore_index=True)

        # print (self.observation, self.state)
        return self.observation, reward, done, {'reward1': self.r1, 'reward2': self.r2, 'reward3': self.r3,
                                                'reward4': self.r4, 'reward5': self.r5}

    def reset(self):
        self.observation = self.df_obs.iloc[0, :].tolist()
        return self.observation
