#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-shakemap.sh
echo "Execute this script after sourcing with correct env."

echo "Process latest Flood event"

xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/flood/make_map.py \
	${INASAFE_WORK_DIR}/floodmaps
