#!/bin/bash
#$ -N compute_fst
#$ -o logs/compute_fst_$JOB_ID.out
#$ -e logs/compute_fst_$JOB_ID.err
#$ -cwd
#$ -l h_rt=10:00:00
#$ -l h_vmem=8G
#$ -l rocky

# Load Python module 
module purge
module load python/3.11.7-gcc-12.2.0

# Activate your virtual environment
source /data/scratch/bt24140/myenv/bin/activate

# Run the FST calculation Python script
python compute_fst.py
