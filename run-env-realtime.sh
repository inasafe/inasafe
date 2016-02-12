#!/bin/bash

# This file contains all the environments needed for realtime

QGIS_PREFIX_PATH=/usr

echo $QGIS_PREFIX_PATH


export QGIS_PREFIX_PATH=$QGIS_PREFIX_PATH
export QGIS_PATH=$QGIS_PREFIX_PATH
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:${PYTHONPATH}


echo "QGIS PATH: $QGIS_PREFIX_PATH"
echo "PYTHONPATH: $PYTHONPATH"
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/realtime/logs/qgis-debug.log

export PATH=${QGIS_PREFIX_PATH}/bin:$PATH

export INASAFE_WORK_DIR=/tmp/realtime
export INASAFE_LOCALE=id
# if the parameter is set in production mode, do not overwrite the variable
# if it is not, we can put test variable here
if [ -z "$INASAFE_REALTIME_REST_URL" ];
then
# allow overrides using native environment
    export INASAFE_REALTIME_REST_URL=http://realtime-test:8000/realtime/api/v1/
    export INASAFE_REALTIME_SHAKEMAP_HOOK_URL="$INASAFE_REALTIME_REST_URL"indicator/notify_shakemap_push
    export INASAFE_REALTIME_REST_USER=test@realtime.inasafe.org
    export INASAFE_REALTIME_REST_PASSWORD=t3st4ccount
    export INASAFE_REALTIME_REST_LOGIN_URL=http://realtime-test:8000/realtime/api-auth/login/
fi

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
