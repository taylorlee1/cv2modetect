#! /bin/bash

#interface=wlx000f0032c9d5
#interface=wlxe8de27182514
interface=wlan0

while [ 1 ]; do
    if ping -c 1 185.27.134.11; then
        echo OK
    else
        echo KO
        ifdown $interface
        ifup  $interface
    fi
    sleep 60 
done

