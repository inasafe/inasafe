#!/bin/bash
# A simple bash script to make it easy to run a single test
# Note it assumes QGIS is in /usr/local
echo "To use:"
echo "$0 <packagename.modulename>"
echo "e.g."
echo "$0 gui.test_is_utilities"
export QGISPATH=/usr/local/
export PYTHONPATH=/usr/local/share/qgis/python/:`pwd`
nosetests -v --with-id --with-coverage $1
