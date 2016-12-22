#!/bin/bash
echo $1
OLD=JOB_PARAMETERS
cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_innuca.sh

sbatch sbatch_innuca.sh