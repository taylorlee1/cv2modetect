#! /bin/bash

if [ "$#" -lt "1" ]; then
    echo "need an arg"
    exit 3
fi
echo "$1"

options="-c:v libx264 -preset fast -profile:v high -level 4.2"
options="-c:v libx264 -preset fast -profile:v baseline -level 3.0"
options="-c:v libx264 -preset fast" # ugh, none of the above really work well.

#if mv $1 $1.tmp; then
#    if ffmpeg -y -i $1.tmp $options $1; then
#        rm -f $1.tmp
#    fi
#fi
