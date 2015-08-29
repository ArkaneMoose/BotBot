#!/bin/bash

while [ 1 ]
do
    python3 source/main.py $@
    if [ $? -ne 0 ]; then
        sleep 10
    fi
done
