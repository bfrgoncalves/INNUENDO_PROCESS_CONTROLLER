#!/bin/bash

echo $1
echo $2

OLD=ARRAY_STRING
cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_innuca.sh
#cat job_processing/sbatch_innuca.sh | sed "s#NUMBER_OF_TASKS#$2#1" > sbatch_innuca.sh

sbatch sbatch_innuca.sh --array=0-$2%1