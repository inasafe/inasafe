#!/bin/bash

export QGISPATH=/usr/local/qgis-master/
export PYTHONPATH=/usr/local/qgis-master/share/qgis/python/:`pwd`
if test -z "$1"
then
  # latest event
  python realtime/make_map.py
else
  # User defined event
  python realtime/make_map.py $1
fi


