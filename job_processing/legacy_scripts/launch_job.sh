#!/bin/sh

echo $1
echo $2
echo $3
echo $4
echo $5

OLD=ARRAY_STRING
USER_D=USER_DIR
FILESTOTRANSFER=FILES_TO_TRANSFER
SLURMCPUS=SLURMCPUS

cat job_processing/sbatch_innuca.template | sed "s#$OLD#$1#1" > sbatch_$4_1.sh
cat sbatch_$4_1.sh | sed "s#$FILESTOTRANSFER#$2#1" > sbatch_$4_2.sh
cat sbatch_$4_2.sh | sed "s#$SLURMCPUS#$5#1" > sbatch_$4_3.sh
cat sbatch_$4_3.sh | sed "s#$USER_D#$3#1" > sbatch_$4.sh

rm sbatch_$4_*.sh

sbatch sbatch_$4.sh