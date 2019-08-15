#!/bin/bash

#SBATCH -J Async_EC
#SBATCH -o Async_EC-%j.out
#SBATCH -e Async_EC-%j.err
#SBATCH -N 1
#SBATCH -n 24
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc
#SBATCH --gres=gpu:1,gpu_ccc:60


python ./../async_EC.py

echo "Executing on $HOSTNAME"

sleep 5
