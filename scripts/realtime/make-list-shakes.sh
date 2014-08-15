#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-list-shakes.sh
source run-env-realtime.sh

xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --list


