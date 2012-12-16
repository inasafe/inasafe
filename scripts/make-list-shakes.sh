#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log
export QGIS_PREFIX_PATH=/usr/local/qgis-master/
export PYTHONPATH=/usr/local/qgis-master/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=/usr/local/qgis-master/lib
export INASAFE_WORK_DIR=/home/web/quake
export INASAFE_POPULATION_PATH=/var/lib/jenkins/jobs/InaSAFE-Realtime/exposure/population.tif
xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --list


