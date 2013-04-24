#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log

export QGIS_PREFIX_PATH=/usr/local/qgis-master/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib

export INASAFE_WORK_DIR=/home/web/quake
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id


if test -z "$1"
then
  # latest event
  python realtime/make_map.py
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py
else
  # User defined event
  xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $1
fi


