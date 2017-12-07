#! /bin/bash

uvcdynctrl -v -d video0 --get='Focus, Auto'
uvcdynctrl -v -d video0 --set='Focus, Auto' 1
uvcdynctrl -v -d video0 --get='Focus, Auto'


uvcdynctrl -v -d video0 --get='Zoom, Absolute'
uvcdynctrl -v -d video0 --set='Zoom, Absolute' 0
uvcdynctrl -v -d video0 --get='Zoom, Absolute'
