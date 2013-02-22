#!/bin/bash

export QGIS_PREFIX_PATH=/usr/local/qgis-realtime/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib

python realtime/update_latest_report.py