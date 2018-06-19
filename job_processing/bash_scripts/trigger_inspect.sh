#!/bin/sh

cd $1/jobs/$2-$3
flowcraft inspect -m broadcast -u $4 &

# Get pid of last process
echo "pid:"$!
