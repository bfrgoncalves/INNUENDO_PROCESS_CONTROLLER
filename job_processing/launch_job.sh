#!/bin/bash

echo $1
echo $2
echo $3
echo $4

OLD=ARRAY_STRING
TASKNUMBER=NUMBEROFTASKS
USER_D=USER_DIR
FILESTOTRANSFER=FILES_TO_TRANSFER

cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_innuca.sh
cat sbatch_innuca.sh | sed "s#$TASKNUMBER#$2#1" > sbatch_innuca.sh

cat sbatch_innuca.sh | sed "s#$FILESTOTRANSFER#$3#1" > sbatch_innuca.sh
cat sbatch_innuca.sh | sed "s#$USER_D#$4#1" > sbatch_innuca.sh


sbatch sbatch_innuca.sh
#sbatch --array=0-$2 --ntasks=1 --cpus-per-task=1 sbatch_innuca.sh