#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-shakemap.sh
echo "Execute this script after sourcing with correct env."

if test -z "$1"
then
  # latest event
  python realtime/earthquake/make_map.py
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/earthquake/make_map.py /home/realtime/shakemaps
else
  # User defined event
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/earthquake/make_map.py /home/realtime/shakemaps $1
fi


