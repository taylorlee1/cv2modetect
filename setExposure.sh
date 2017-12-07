#! /bin/bash

if [ "$1" == "day" ]; then

    echo day
    uvcdynctrl -v -d video0 --set='Exposure, Auto' 1
    uvcdynctrl -v -d video0 --set='Exposure (Absolute)' 30
    uvcdynctrl -v -d video0 --set='Exposure, Auto Priority' 0

elif [ "$1" == "night" ]; then
    echo night
    uvcdynctrl -v -d video0 --set='Exposure, Auto' 3
    #uvcdynctrl -v -d video0 --set='Exposure (Absolute)' 30


else
    echo no arg
fi


uvcdynctrl -v -d video0 --get='Exposure, Auto'
uvcdynctrl -v -d video0 --get='Exposure (Absolute)'
uvcdynctrl -v -d video0 --get='Exposure, Auto Priority' 0
