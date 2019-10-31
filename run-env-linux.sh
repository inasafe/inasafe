#!/bin/bash

QGIS_PREFIX_PATH=/usr
if [ -n "$1" ]; then
    QGIS_PREFIX_PATH=$1
fi

echo $QGIS_PREFIX_PATH


export QGIS_PREFIX_PATH=$QGIS_PREFIX_PATH
export QGIS_PATH=$QGIS_PREFIX_PATH
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:~/.local/share/QGIS/QGIS3/profiles/default/python/plugins:${PYTHONPATH}

echo "QGIS PATH: $QGIS_PREFIX_PATH"
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log

export INASAFE_WORK_DIR=/tmp/inasafe
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id
export INASAFE_REALTIME_REST_URL=http://localhost:8000/realtime/api/v1/
export INASAFE_REALTIME_REST_USER=test@realtime.inasafe.org
export INASAFE_REALTIME_REST_PASSWORD=t3st4ccount
export INASAFE_REALTIME_REST_LOGIN_URL=http://localhost:8000/realtime/api-auth/login/

# The following line enables remote logging to sentry and may reveal
# IP address / host name / file system paths (which could include your user
# name)
export INASAFE_SENTRY=1

echo "This script is intended to be sourced to set up your shell to"
echo "use a QGIS 3 built in $QGIS_PREFIX_PATH"
echo
echo "To use it do:"
echo "source $BASH_SOURCE /your/optional/install/path"
echo
echo "Then use the make file supplied here e.g. make guitest"
