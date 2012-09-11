#!/bin/bash
# A simple bash script to make it easy to run a single test
# Note it assumes QGIS is in /usr/local
echo "To use:"
echo "$0 <packagename.modulename.testname>"
echo "e.g."
echo "$0 safe_qgis.test_utilities"
export QGISPATH=/usr/local/
export PYTHONPATH=/usr/local/share/qgis/python/:`pwd`:$PYTHONPATH
export QGIS_DEBUG=0;
export QGIS_LOG_FILE=/dev/null;
export QGIS_DEBUG_FILE=/dev/null;
nosetests -v --with-id --with-coverage $1
