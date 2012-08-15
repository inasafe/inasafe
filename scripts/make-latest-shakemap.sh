#!/bin/bash
export QGISPATH=/usr/local/qgis-master/
export PYTHONPATH=/usr/local/qgis-master/share/qgis/python/:`pwd`
python realtime/make_map.py

