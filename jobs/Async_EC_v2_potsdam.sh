#!/bin/bash

#SBATCH -J Async_EC_v2_potsdam
#SBATCH -o Async_EC_v2_potsdam-%j.out
#SBATCH -e Async_EC_v2_potsdam-%j.err
#SBATCH -N 1
#SBATCH -n 12
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc
#SBATCH --gres=gpu:V100:1

source activate ray
python async_EC_v2_potsdam.py

echo "Executing on $HOSTNAME"

sleep 5
