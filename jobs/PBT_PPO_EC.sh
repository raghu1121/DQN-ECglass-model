#!/bin/bash

#SBATCH -J PBT_PPO_EC
#SBATCH -o PBT_PPO_EC-%j.out
#SBATCH -e PBT_PPO_EC-%j.err
#SBATCH -N 1
#SBATCH -n 24
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc



python ./../PBT_PPO_EC.py

echo "Executing on $HOSTNAME"

sleep 5
