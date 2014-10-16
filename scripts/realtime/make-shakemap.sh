#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-shakemap.sh
source run-env-realtime.sh

if test -z "$1"
then
  # latest event
  python realtime/make_map.py
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py
else
  # User defined event
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $1
fi


