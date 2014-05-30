#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log

export QGIS_PREFIX_PATH=/usr/local/qgis-2.2
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib

export INASAFE_WORK_DIR=/tmp/quake
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id


python realtime/make_local_map.py


