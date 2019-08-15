#!/bin/bash

#SBATCH -J PPO_async_EC
#SBATCH -o PPO_async_EC-%j.out
#SBATCH -e PPO_async_EC-%j.err
#SBATCH -N 1
#SBATCH -n 24
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc

python ./../PPO_async_EC.py

echo "Executing on $HOSTNAME"

sleep 5
