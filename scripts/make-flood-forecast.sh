#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log
export QGIS_PREFIX_PATH=/usr/local/qgis-realtime/
# export PYTHONPATH=/usr/local/qgis-realtime/share/qgis/python/:`pwd`
export PYTHONPATH=~/Documents/inasafe/inasafe-dev:`pwd`
export LD_LIBRARY_PATH=/usr/local/qgis-realtime/lib

export INASAFE_LOCALE=id
cd /home/sunnii/Documents/inasafe/inasafe-dev/
xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_flood_forecast.py
