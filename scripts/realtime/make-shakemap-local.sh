#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-shakemap-local.sh
source run-env-realtime.sh

xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_local_map.py


