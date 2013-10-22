#!/bin/bash
#Call make with local env set for hand build qgis master
export QGIS_PREFIX_PATH=/usr/local/qgis-2.0
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export PYTHONPATH=${QGIS_PREFIX_PATH}/qgis/python:${PYTHONPATH}
make $1
