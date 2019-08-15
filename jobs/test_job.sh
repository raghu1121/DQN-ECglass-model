#!/bin/bash

#SBATCH -J test_job
#SBATCH -o test_job-%j.out
#SBATCH -e test_job-%j.err
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mail-type=ALL
#SBATCH --account=TUK-Amlafoc
#SBATCH --gres=gpu:V100:1

python test.py

echo "Executing on $HOSTNAME"

sleep 5
