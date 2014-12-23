#!/bin/bash

#Search for available quakes and make sure they are listed in public
#set -x
REALTIME_DIR=/home/realtime
WEB_DIR=${REALTIME_DIR}/web

mkdir -p ${WEB_DIR}
cd ${WEB_DIR}

LOCALES='en id'
for LOCALE in ${LOCALES}
do
  mkdir -p ${LOCALE}
  cp -r ${WEB_DIR}/resource/ ${WEB_DIR}/${LOCALE}/
  for FILE in `find ${REALTIME_DIR}/shakemaps-extracted -name *-${LOCALE}.pdf`
  do
    BASE=`basename $FILE .pdf`
    DEST=${LOCALE}/${BASE}.pdf
    if [ ! -f $DEST ]
    then
      cp -a ${FILE} ${DEST}
    fi
  done

  for FILE in `find ${REALTIME_DIR}/shakemaps-extracted -name *-${LOCALE}.png`
  do
    BASE=`basename $FILE .png`
    DEST=${LOCALE}/${BASE}.png
    if [ ! -f ${DEST} ]
    then
      cp -a ${FILE} ${DEST}
      #echo "Copying $BASE"
    fi
  done
done
