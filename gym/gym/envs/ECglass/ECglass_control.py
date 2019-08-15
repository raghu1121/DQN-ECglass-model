import gym
from gym import spaces, logger
from gym.utils import seeding
import pandas as pd
import numpy as np
from itertools import chain
import json
import os


# import modin.pandas as pd

class EcGlassEnv(gym.Env):
    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.df = pd.read_csv(self.path + '/assets/observations.csv')
        self.df_env = pd.read_csv(self.path + '/assets/env.csv')
        low = np.array([0, -180, 0, 0])
        high = np.array([90, 180, 1500, 1000])
        self.action_space = spaces.Discrete(64)
        self.observation_space = spaces.Box(low, high)
        self.dgp_threshold = 0.45
        self.seed()
        self.state = None
        self.observation = None
        self.count = 0
        self.count1 = 0
        self.count2 = 0
        self.count3 = 0
        self.count4 = 0
        self.count5 = 0
        self.count6 = 0
        self.min = 92
        self.results = pd.DataFrame(columns=['self.observation', 'self.state', 'action', 'reward'])

    def getState(self, observation, action):

        filtered = self.df[
            (self.df['altitude'] == observation[0]) & (self.df['azimuth'] == observation[1]) & (
                    self.df['dir'] == observation[2]) & (
                    self.df['diff'] == observation[3]) & (self.df['action'] == action)]
        return list(chain.from_iterable(filtered.iloc[:, 4:8].values))

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

        self.observation = self.df_env.iloc[self.count, :].values
        self.state = self.getState(self.observation, action)
        # reward = 0
        # for v in self.state:
        #     # if (v >= 0.2 and v < 0.35):
        #     #     reward = reward + 2
        #     # elif (v >= 0.35 and v < 0.4):
        #     #     reward = reward
        #     # elif (v >= 0.4 and v < 0.45):
        #     #     reward = reward - 1
        #     # elif v >= 0.45:
        #     #     reward = reward - 2
        #     # else:
        #     #     reward = reward + 1
        #
        #     if (v >= 0.2 and v < 0.36):
        #         reward = reward + 3
        #     elif (v > 0.36 and v < 0.4):
        #         reward = reward - 2
        #     elif (v >= 0.4 and v < 0.45):
        #         reward = reward - 4
        #     elif v >= 0.45:
        #         reward = reward - 6
        #     else:
        #         reward = reward
        #
        # n = self.action_mapping(action)
        #
        # d1, d2, d3, d4 = self.state
        #
        # if d1 > 0.36 or d2 > 0.36 or d3 > 0.36 or d4 > 0.36:
        #     reward = reward - n[0] - (2 / 3) * n[1] - (1 / 3) * n[2] + n[3]
        #
        # elif d1 < 0.2 or d2 < 0.2 or d3 < 0.2 or d4 < 0.2:
        #     reward = reward + n[0] - (1 / 3) * n[1] - (2 / 3) * n[2] - n[3]
        #
        # else:
        #     reward = reward - (1 / 6) * n[1] - (1 / 3) * n[2] - (2 / 3) * n[3]
        #
        # reward = (reward / 12)
        # # reward = (reward / 8)
        # done = False
        # self.count = self.count + 1
        # if self.count == 3499:
        #     done = True
        #     print('********************')
        #     print('********************')
        #     # print('Count<0.5: ' + str(self.count1), '| Count=0.5: ' + str(self.count3), '| Count=0.625 :' + str(self.count4),
        #     #       '| Count=0.75 :' + str(self.count5), '| Count=0.875 :' + str(self.count6), '| Count=1 :' + str(self.count2))
        #     print('Count(r<1): ' + str(self.count1),
        #           # '| Count=0.5: ' + str(self.count3),
        #           # '| Count=7/12 :' + str(self.count4),
        #           # '| Count=8/12 :' + str(self.count5), '| Count=10/12 :' + str(self.count6),
        #           '| Count(r=1) :' + str(self.count2))
        #     print('********************')
        #     # if self.count1 < self.min:
        #     #     self.min = self.count1
        #     #     # print (self.results)
        #     #     self.results.to_csv('results_' + str(self.count1) + '.csv')
        #     self.count = 0
        #     self.count1 = 0
        #     self.count2 = 0
        #     # self.count3 = 0
        #     # self.count4 = 0
        #     # self.count5 = 0
        #     # self.count6 = 0
        #     # self.results = pd.DataFrame()
        #
        # if reward < 1:
        #     self.count1 = self.count1 + 1
        # # elif reward == 0.5:
        # #     self.count3 = self.count3 + 1
        # # elif reward == 0.625:
        # #     self.count4 = self.count4 + 1
        # # elif reward == 0.75:
        # #     self.count5 = self.count5 + 1
        # # elif reward == 0.875:
        # #     self.count6 = self.count6 + 1
        # # elif reward == (7/12):
        # #     self.count4 = self.count4 + 1
        # # elif reward == (8/12):
        # #     self.count5 = self.count5 + 1
        # # elif reward == (10/12):
        # #     self.count6 = self.count6 + 1
        # else:
        #     self.count2 = self.count2 + 1
        # # self.results = self.results.append(
        # #     {'self.observation': self.observation, 'self.state': self.state, 'action': action, 'reward': reward},
        # #     ignore_index=True)
        #
        # return self.observation + self.state, reward, done, {'Count(r<1)': str(self.count1),
        #                                                      'Count(r=1)': str(self.count2)}
        # Reward/Penalty for Glare
        reward1 = 0
        for v in self.state:
            if (v >= 0.2 and v < 0.36):
                reward1 = reward1 + 3
            elif (v >= 0.36 and v < 0.4):
                reward1 = reward1 - 2
            elif (v >= 0.4 and v < 0.45):
                reward1 = reward1 - 4
            elif v >= 0.45:
                reward1 = reward1 - 6
            else:
                reward1 = reward1
        reward1 = (reward1 / 12)

        #Penalty for lowlighting, and for using dark (lowlit) or clear (glare) states of EC glass.

        reward2=0
        n = self.action_mapping(action)

        d1, d2, d3, d4 = self.state

        if d1 >= 0.36 or d2 >= 0.36 or d3 >= 0.36 or d4 >= 0.36:

            reward2 = (1 / max([d1, d2, d3, d4]) - (1 / 0.36)) - (0.672 * n[0] + 0.198 * n[1] + 0.064 * n[2] - 0.011 * n[3]) / (
                        3 * 0.672)

        elif d1 < 0.2 or d2 < 0.2 or d3 < 0.2 or d4 < 0.2:

            reward2 = ((1 / 0.2) - (1 / min([d1, d2, d3, d4]))) + (0.672 * n[0] - 0.198 * n[1] - 0.064 * n[2] - 0.011 * n[3]) / (
                        3 * 0.672)
        else:

            reward2 = 2 - (((1 / d1) + (1 / d2) + (1 / d3) + (1 / d4)) / (4 * ((1 / 0.2) - (1 / 0.36)))) + (
                        0.672 * n[0] + 0.198 * n[1] + 0.064 * n[2] + 0.011 * n[3]) / (3 * 0.672)



        reward=reward1+reward2/2
        #reward=reward/2
        done = False
        self.count = self.count + 1
        if self.count == 3499:
            done = True
            print('********************')
            print('********************')

            print('Count(r<0): ' + str(self.count1),
                  '| Count(0<r<1): ' + str(self.count3),
                  '| Count(r>1) :' + str(self.count2))
            print('********************')
            if self.count1 <= self.min:
                    self.min = self.count1
                    # print (self.results)
                    self.results.to_csv('results_' + str(self.count1) +'_' + str(self.count3) +'_' + str(self.count2)+'.csv')
            self.count = 0
            self.count1 = 0
            self.count2 = 0
            self.count3 = 0
            self.results = pd.DataFrame()

        if reward < 0:
            self.count1 = self.count1 + 1
        elif reward > 0 and reward < 1:
            self.count3 = self.count3 + 1

        else:
            self.count2 = self.count2 + 1
        self.results = self.results.append(
            {'self.observation': self.observation, 'self.state': self.state, 'action': action, 'reward': reward},
            ignore_index=True)
        return self.observation + self.state, reward, done, {'Count(r<0)': self.count1,'Count(0<r<1)': self.count3,
                                                             'Count(r>1)': self.count2}
    def reset(self):
        self.observation = self.df_env.iloc[0, :].values
        return self.observation
