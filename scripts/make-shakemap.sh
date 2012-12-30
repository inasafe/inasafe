#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log
export QGIS_PREFIX_PATH=/usr/local/qgis-master/
export PYTHONPATH=/usr/local/qgis-master/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=/usr/local/qgis-master/lib
export INASAFE_LOCALE=id

if test -z "$1"
then
  # latest event
  python realtime/make_map.py
else
  # User defined event
  python realtime/make_map.py $1
fi


