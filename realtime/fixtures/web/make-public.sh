#!/bin/bash

#Search for available quakes and make sure they are listed in public

mkdir -p /home/web/quake/public/
cp -r /home/timlinux/dev/python/inasafe-realtime/realtime/fixtures/web/resource/ /home/web/quake/public/
cd /home/web/quake
for FILE in `find shakemaps-extracted -name *.pdf`
do 
  BASE=`basename $FILE .pdf`
  DEST=public/$BASE.pdf
  if [ ! -f $DEST ]
  then 
    cp -a $FILE $DEST
    #echo "Copying $BASE"
  fi
done

for FILE in `find shakemaps-extracted -name *.png`
do 
  BASE=`basename $FILE .png`
  DEST=public/$BASE.png
  if [ ! -f $DEST ]
  then 
    cp -a $FILE $DEST
    #echo "Copying $BASE"
  fi
done
