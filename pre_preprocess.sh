#!/bin/bash

for file in dataset/sequences/*/labels/*.label
do 
    seq=$(echo $file | grep -o '/[0-9]*/' | cut -d'/' -f2)
    num=$(echo $file | grep -o '[0-9]*\.label' | cut -d'.' -f1)
    python3 filter_pc.py $seq $num
done