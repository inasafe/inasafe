#!/bin/bash

QGISPATH=/Applications/QGIS-Realtime.app

export QGIS_PREFIX_PATH=${QGISPATH}/contents/MacOS

echo "QGIS PATH: $QGIS_PREFIX_PATH"

PYTHONPATH=${PYTHONPATH}:"${QGISPATH}/Contents/Resources/python"
PYTHONPATH=${PYTHONPATH}:'/Library/Frameworks/GDAL.framework/Versions/1.9/Python/2.7/site-packages'
export PYTHONPATH

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log


export INASAFE_WORK_DIR=/tmp/quake
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id

echo "PYTHON PATH: $PYTHONPATH"

nosetests realtime

