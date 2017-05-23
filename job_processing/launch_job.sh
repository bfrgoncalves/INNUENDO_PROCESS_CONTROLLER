#!/bin/bash

echo $1
echo $2
echo $3
echo $4
echo $5

OLD=ARRAY_STRING
TASKNUMBER=NUMBEROFTASKS
TOTALTASKSPERNODE=TASKSPERNODE
USER_D=USER_DIR
FILESTOTRANSFER=FILES_TO_TRANSFER

cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_innuca.sh
cat sbatch_innuca.sh | sed "s#$TASKNUMBER#$2#1" > sbatch_innuca_1.sh
cat sbatch_innuca_1.sh | sed "s#$TOTALTASKSPERNODE#$3#1" > sbatch_innuca_2.sh
cat sbatch_innuca_2.sh | sed "s#$FILESTOTRANSFER#$4#1" > sbatch_innuca_3.sh
cat sbatch_innuca_3.sh | sed "s#$USER_D#$5#1" > sbatch_innuca.sh

rm sbatch_innuca_*.sh

sbatch sbatch_innuca.sh
#sbatch --array=0-$2 --ntasks=1 --cpus-per-task=1 sbatch_innuca.sh