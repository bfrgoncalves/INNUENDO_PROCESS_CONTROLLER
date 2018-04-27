#!/bin/sh

#SBATCH -s
#SBATCH --partition=nextflow
#SBATCH --mem-per-cpu=400


#Path to user job dir
echo $1
#File location
echo $2
#File 1
echo $3
#File 2
echo $4
#nextflow profile
echo $5

cd $1

if [ ! -d "data" ]; then
	mkdir data
fi

ln -s $3 ${1}/data/sample_1.fastq.gz
ln -s $4 ${1}/data/sample_2.fastq.gz

echo -e "\nincludeConfig 'platform.config'" >> nextflow.config

srun nextflow run $2 -profile $5 -resume > nextflow_log.txt 2>&1
