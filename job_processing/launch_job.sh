#!/bin/bash

echo $1
echo $2
echo $3
echo $4

OLD=ARRAY_STRING
#PROCESSES=ARRAY_PROCESSES
#WORKFLOWS=ARRAY_WORKFLOWS
#OUTPUTS=ARRAY_OUTPUTS
#TASKNUMBER=NUMBEROFTASKS
#TOTALTASKSPERNODE=TASKSPERNODE
USER_D=USER_DIR
FILESTOTRANSFER=FILES_TO_TRANSFER

cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_innuca_$4_1.sh
#cat sbatch_innuca.sh | sed "s#$TASKNUMBER#$2#1" > sbatch_innuca_1.sh
#cat sbatch_innuca_1.sh | sed "s#$TOTALTASKSPERNODE#$3#1" > sbatch_innuca_2.sh
cat sbatch_innuca_$4_1.sh | sed "s#$FILESTOTRANSFER#$2#1" > sbatch_innuca_$4_2.sh
#cat sbatch_innuca_3.sh | sed "s#$PROCESSES#$6#1" > sbatch_innuca_4.sh
#cat sbatch_innuca_4.sh | sed "s#$WORKFLOWS#$7#1" > sbatch_innuca_5.sh
#cat sbatch_innuca_5.sh | sed "s#$OUTPUTS#$8#1" > sbatch_innuca_6.sh
cat sbatch_innuca_$4_2.sh | sed "s#$USER_D#$3#1" > sbatch_innuca_$4.sh

rm sbatch_innuca_$4_*.sh

sbatch sbatch_innuca_$4.sh
#sbatch --array=0-$2 --ntasks=1 --cpus-per-task=1 sbatch_innuca.sh