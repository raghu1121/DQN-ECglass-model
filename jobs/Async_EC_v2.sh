#!/bin/bash

#SBATCH -J Async_EC_v2
#SBATCH -o Async_EC_v2-%j.out
#SBATCH -e Async_EC_v2-%j.err
#SBATCH -N 1
#SBATCH -n 10
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc
#SBATCH --gres=gpu:V100:1


python async_EC_v2.py

echo "Executing on $HOSTNAME"

sleep 5
