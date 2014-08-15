#!/bin/bash

# This file contains all the environments needed for realtime

QGIS_PREFIX_PATH=/usr
if [ -n "$1" ]; then
    QGIS_PREFIX_PATH=$1
fi

echo $QGIS_PREFIX_PATH


export QGIS_PREFIX_PATH=$QGIS_PREFIX_PATH
export QGIS_PATH=$QGIS_PREFIX_PATH
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:${PYTHONPATH}

echo "QGIS PATH: $QGIS_PREFIX_PATH"
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/home/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/home/realtime/logs/qgis-debug.log

export PATH=${QGIS_PREFIX_PATH}/bin:$PATH

export INASAFE_WORK_DIR=/home/realtime
export INASAFE_LOCALE=id

# The following line enables remote logging to sentry and may reveal
# IP address / host name / file system paths (which could include your user
# name)
export INASAFE_SENTRY=1

echo "This script is intended to be sourced to set up your shell to"
echo "use a QGIS in $QGIS_PREFIX_PATH"
echo
echo "To use it do:"
echo "source $BASH_SOURCE /your/optional/install/path"
echo
echo "Then use the make file supplied here e.g. make guitest"
