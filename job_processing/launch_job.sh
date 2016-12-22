#!/bin/bash
cat job_processing/batch_innuca.template | sed -e 's/JOB_PARAMETERS/'$1'/' > sbatch_innuca.sh

sbatch sbatch_innuca.sh