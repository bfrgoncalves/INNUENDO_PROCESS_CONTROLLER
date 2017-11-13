#!/bin/sh

#Path to user job dir
echo $1
#File location
echo $2
#Project id
echo $3
#Pipeline id
echo $4
#Post URL
echo $5
#Current dir
echo$6

cd $1
nextflow run $2 --projectId=$3  --pipelineId=$4 --platformHTTP=$5 -profile slurm
cd $6