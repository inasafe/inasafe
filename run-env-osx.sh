#!/bin/bash

# To use this file do
#
# source runshell-osx.sh
#
# Tim Sutton, June 2013

# Assume brew insstalled deps
export PATH=$PATH:/usr/local/bin/
export PYTHONPATH=/usr/local/lib/python2.7/site-packages/
#export PATH=$PATH:/usr/local/Cellar/pyqt/4.10.3/bin
#export PYTHONPATH=$PYTHONPATH:/usr/local/Cellar/pyqt/4.10.3/lib/python2.7/site-packages/:/usr/local/Cellar/sip/4.15.4/lib/python2.7/site-packages/
#export PATH=$PATH:/usr/local/Cellar/gdal/1.10.1/bin/


QGISPATH=/Applications/QGIS.app
export QGIS_PREFIX_PATH=${QGISPATH}/contents/MacOS
echo "QGIS PATH: $QGIS_PREFIX_PATH"
PYTHONPATH=${PYTHONPATH}:"${QGISPATH}/Contents/Resources/python"
PYTHONPATH=${PYTHONPATH}:'/Library/Frameworks/GDAL.framework/Versions/1.10/Python/2.7/site-packages'
export PYTHONPATH

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log

export INASAFE_WORK_DIR=/tmp/inasafe
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id

echo "PYTHON PATH: $PYTHONPATH"


