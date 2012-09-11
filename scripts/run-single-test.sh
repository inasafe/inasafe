#!/bin/bash
# A simple bash script to make it easy to run a single test
# Note it assumes QGIS is in /usr/local
echo "To use:"
echo "$0 <packagename.modulename.testname>"
echo "e.g."
echo "$0 gui.test_is_utilities"
export QGISPATH=/usr/local/qgis-master
export PYTHONPATH=/usr/local/qgis-master/share/qgis/python/:`pwd`:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/qgis-master/lib
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log
nosetests -v $1
