#!/bin/bash

#SBATCH -J Async_EC_v2_1
#SBATCH -o Async_EC_v2_1-%j.out
#SBATCH -e Async_EC_v2_1-%j.err
#SBATCH -N 1
#SBATCH -n 12
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc
#SBATCH --gres=gpu:V100:1


python async_EC_v2_1.py

echo "Executing on $HOSTNAME"

sleep 5
