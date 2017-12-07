#! /bin/bash

#uvcdynctrl -v -d video0
#uvcdynctrl -v -d video0 -h
#uvcdynctrl -l
#uvcdynctrl -v 
#uvcdynctrl -v  -c
uvcdynctrl -v -d video0 --get='Focus, Auto'
#uvcdynctrl -v --get='Focus, Auto'
uvcdynctrl -v -d video0 --set='Focus, Auto' 0
#uvcdynctrl -v --get='Focus, Auto'

uvcdynctrl -v -d video0 --get='Focus, Auto'
uvcdynctrl -v -d video0 --get='Focus (absolute)'
uvcdynctrl -v -d video0 --set='Focus (absolute)' 0
uvcdynctrl -v -d video0 --get='Focus (absolute)'


uvcdynctrl -v -d video0 --get='Zoom, Absolute'
uvcdynctrl -v -d video0 --set='Zoom, Absolute' 400
uvcdynctrl -v -d video0 --get='Zoom, Absolute'
