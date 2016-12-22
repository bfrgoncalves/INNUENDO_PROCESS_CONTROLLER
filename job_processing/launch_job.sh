#!/bin/bash
echo $1
cat job_processing/sbatch_innuca.template | sed 's/JOB_PARAMETERS/$1/' > sbatch_innuca.sh

sbatch sbatch_innuca.sh