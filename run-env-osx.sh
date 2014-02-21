#!/bin/bash

# To use this file do
#
# source runshell-osx.sh
#
# Tim Sutton, June 2013

# Assume brew installed deps
export PATH=$PATH:/usr/local/bin/

SITES=`find /usr/local/ -name site-packages`
for SITE in $SITES
do
	PYTHONPATH=$PYTHONPATH:$SITE
done



QGISPATH=`find /usr/local/ -name QGIS.app`
export QGIS_PREFIX_PATH=${QGISPATH}/contents/MacOS
echo "QGIS PATH: $QGIS_PREFIX_PATH"
# Needed for importing processing plugin - assumes brew install
PYTHONPATH=$PYTHONPATH:${QGIS_PREFIX_PATH}//QGIS.app/Contents/Resources/python/plugins
export PYTHONPATH

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log

export INASAFE_WORK_DIR=/tmp/inasafe
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id

echo "PYTHON PATH: $PYTHONPATH"


