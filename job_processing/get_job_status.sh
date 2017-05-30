#get job ids by current running step
squeue --job $1 -s | sed "1d" | sed "s/ \+/\t/g" | cut -f2,6