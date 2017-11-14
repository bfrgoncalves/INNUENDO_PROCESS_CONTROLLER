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
#File 1
echo $6
#File 2
echo $7

cd $1

if [ ! -d "data" ]; then
	mkdir data
fi

ln -s $6 ${1}/data
ln -s $7 ${1}/data
nextflow run $2 --projectId=$3  --pipelineId=$4 --platformHTTP=$5 -profile oneida &
