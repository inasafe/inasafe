#!/bin/bash

# We should call this from inasafe root:
# e.g. scripts/realtime/make-latest-shakemap.sh /home/realtime/shakemaps
echo "Execute this script after sourcing with correct env."

if [ -n "$1" ];
then
    xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $1
else
    echo "No shakemaps directory passed."
    echo "USAGE: make-latest-shakemaps.sh <shakemaps_directory>"
fi

