#!/bin/bash
log_dir="LOG"
mkdir $log_dir

LO_BND=$(($1))
UP_BND=$(($2-1))
for (( sim=$LO_BND; sim<=$UP_BND; sim++))
do
    echo $sim
    rm "$log_dir/$sim.out" "$log_dir/$sim.err"
    python simulateNetworks_hpc.py $sim $2 $3>"$log_dir/$sim.out" 2>"$log_dir/$sim.err" &
done
