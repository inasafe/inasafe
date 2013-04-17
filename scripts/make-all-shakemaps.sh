#!/bin/bash

export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log

export QGIS_PREFIX_PATH=/usr/local/qgis-master/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib

export INASAFE_WORK_DIR=/home/web/quake
export INASAFE_POPULATION_PATH=`pwd`/realtime/fixtures/exposure/population.tif
export INASAFE_LOCALE=id

for FILE in `xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --list | grep -v inp | grep -v Proces`
do
  # FILE=`echo $FILE | sed 's/ftp:\/\/118.97.83.243\///g'`
  # FILE=`echo $FILE | sed 's/.out.zip//g'`
  # simple filter incase there another output except the event ids
  if [ 14 == ${#FILE} ] ; then
    echo "Running: $FILE"
    xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $FILE
  fi
done
exit
# Memory errors..
#xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --run-all



