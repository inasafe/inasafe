#!/bin/bash

# We should call this from inasafe root:
# i.e. scripts/realtime/make-all-shakemaps.sh
echo "Execute this script after sourcing with correct env."

for FILE in `xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $1 --list | grep -v inp | grep -v Proces`
do
  # FILE=`echo $FILE | sed 's/ftp:\/\/118.97.83.243\///g'`
  # FILE=`echo $FILE | sed 's/.out.zip//g'`
  # simple filter incase there another output except the event ids
  if [ 14 == ${#FILE} ] ; then
    echo "Running: $FILE"
    xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $1 $FILE
  fi
done
exit
# Memory errors..
#xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --run-all



