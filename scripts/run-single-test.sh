#!/bin/bash
# A simple bash script to make it easy to run a single test
# Note it defaults to QGIS in /usr/local
echo "To use:"
echo "$0 packagename.modulename [/path/to/qgis]"
echo "e.g."
echo "$0 safe_qgis.test_utilities /usr/local"
qgispath=${2-'/usr/local/'}
echo "Setting QGISPATH to $qgispath..."
export QGISPATH=$qgispath
export PYTHONPATH=$QGISPATH/share/qgis/python/:`pwd`:$PYTHONPATH
export QGIS_DEBUG=0;
export QGIS_LOG_FILE=/dev/null;
export QGIS_DEBUG_FILE=/dev/null;
nosetests -v --with-id --with-coverage $1
