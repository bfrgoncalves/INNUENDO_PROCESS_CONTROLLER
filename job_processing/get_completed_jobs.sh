#get completed jobs by id
sacct -b -j 584 | tail -n +3 | sed "s/ \+/\t/g" | cut -f 1,2