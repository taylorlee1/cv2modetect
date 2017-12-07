#! /bin/bash

while [ 1 ]; do
    s=$(ps -ef | egrep mocap.py | egrep -cv grep )
    #echo $s

    if [ "$s" -gt "0" ]; then
        echo $(date) mocap ok
    else
        echo run mocap
        ./run.sh 
    fi

    sleep 15
done


