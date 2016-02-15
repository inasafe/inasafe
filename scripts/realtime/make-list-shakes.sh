#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-list-shakes.sh
echo "Execute this script after sourcing with correct env."

xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/earthquake/make_map.py /home/realtime/shakemaps --list


