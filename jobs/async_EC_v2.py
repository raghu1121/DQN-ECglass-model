
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import ray
from ray.tune import grid_search, run_experiments
from ray.tune.schedulers import AsyncHyperBandScheduler
import ray.tune as tune
import numpy as np

def on_episode_start(info):
    episode = info["episode"]
    print("episode {} started".format(episode.episode_id))
    episode.user_data["reward1"] = []
    episode.user_data["reward2"] = []
    episode.user_data["reward3"] = []
    episode.user_data["reward4"] = []
    episode.user_data["reward5"] = []


def on_episode_step(info):
    episode = info["episode"]
    dict =episode.last_info_for()
    if not dict is None:

        episode.user_data["reward1"].append(dict["reward1"])
        episode.user_data["reward2"].append(dict["reward2"])
        episode.user_data["reward3"].append(dict["reward3"])
        episode.user_data["reward4"].append(dict["reward4"])
        episode.user_data["reward5"].append(dict["reward5"])



def on_episode_end(info):
    episode = info["episode"]
    reward1 = np.mean(episode.user_data["reward1"])
    reward2 = np.mean(episode.user_data["reward2"])
    reward3 = np.mean(episode.user_data["reward3"])
    reward4 = np.mean(episode.user_data["reward4"])
    reward5 = np.mean(episode.user_data["reward5"])

    print("episode {} ended with length {}, reward1 {} , reward2 {}, reward3 {}, reward4 {}, reward5 {}".format(
        episode.episode_id, episode.length, reward1,reward2,reward3,reward4,reward5))
    episode.custom_metrics["reward1"] = reward1
    episode.custom_metrics["reward2"] = reward2
    episode.custom_metrics["reward3"] = reward3
    episode.custom_metrics["reward4"] = reward4
    episode.custom_metrics["reward5"] = reward5



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test", action="store_true", help="Finish quickly for testing")
    args, _ = parser.parse_known_args()
    ray.init()

    # asynchronous hyperband early stopping, configured with
    # `episode_reward_max` as the
    # objective and `training_iteration` as the time unit,
    # which is automatically filled by Tune.
    ahb = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        reward_attr="episode_reward_max",
        grace_period=10,
        max_t=100

    )

    run_experiments(
        {
            "asynchyperband_EC_dqn_v2_1": {
                "run": 'DQN',
                "env":'ECglass-v2',
                "stop": {
                    "timesteps_total": 8760000,
                    # "training_iteration": 1 if args.smoke_test else 99999
                },
                "num_samples": 8,

                "resources_per_trial": {
                    "cpu": 0.5,
                    "gpu": 0.1
                },
                "config": {
                    "hiddens":tune.grid_search([[4096,2048],[2048,1024],[2048,2048]]),
                    "callbacks": {
                        "on_episode_start": tune.function(on_episode_start),
                        "on_episode_step": tune.function(on_episode_step),
                        "on_episode_end": tune.function(on_episode_end),
                    },
                    "learning_starts": 64,
                    "buffer_size": 1000000,
                    "exploration_fraction": 1,
                    "train_batch_size":tune.grid_search([250,200]),
                    "gamma":0,
                    "exploration_final_eps":tune.grid_search([0.03,0.01,0.02]),
                    #"exploration_final_eps": 0.05,
                    #"num_workers": 2,
                    "lr": tune.grid_search([0.000001,0.00005,0.00001,0.0005]),
                    "target_network_update_freq":tune.grid_search([18000,25000]),
                    "timesteps_per_iteration": 8760,
                    "schedule_max_timesteps": 7000000

                },
                "checkpoint_freq": 1,
                "local_dir": "/scratch/kalyanam/ray_results"
            }
        },
        scheduler=ahb)