#!/bin/bash

#Search for available quakes and make sure they are listed in public
#set -x

mkdir -p /home/web/quake/public/
cd /home/web/quake
LOCALES='en id'
for LOCALE in $LOCALES
do
  mkdir -p public/${LOCALE}
  cp -r ${HOME}/dev/python/inasafe-realtime/realtime/fixtures/web/resource/ /home/web/quake/public/${LOCALE}/
  for FILE in `find shakemaps-extracted -name *-${LOCALE}.pdf`
  do 
    BASE=`basename $FILE .pdf`
    DEST=public/${LOCALE}/$BASE.pdf
    if [ ! -f $DEST ]
    then 
      cp -a $FILE $DEST
      #echo "Copying $BASE"
    fi
  done

  for FILE in `find shakemaps-extracted -name *-${LOCALE}.png`
  do 
    BASE=`basename $FILE .png`
    DEST=public/${LOCALE}/$BASE.png
    if [ ! -f $DEST ]
    then 
      cp -a $FILE $DEST
      #echo "Copying $BASE"
    fi
  done
done
