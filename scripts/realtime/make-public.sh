#!/bin/bash

if [ -n "$1" ] && [ -n "$2" ];
then
  SHAKEMAPS_EXTRACT_DIR="$1"
  WEB_DIR="$2"
else
  echo "No shakemaps extracted directory and web directory passed."
  echo "USAGE: make-public.sh <shakemaps_extracted_directory> <target_web_dir>"
  exit
fi

mkdir -p ${WEB_DIR}
cd ${WEB_DIR}

LOCALES='en id'
for LOCALE in ${LOCALES}
do
  mkdir -p ${LOCALE}
  cp -r ${WEB_DIR}/resource/ ${WEB_DIR}/${LOCALE}/
  for FILE in `find ${SHAKEMAPS_EXTRACT_DIR} -name *-${LOCALE}.pdf`
  do
    BASE=`basename $FILE .pdf`
    DEST=${LOCALE}/${BASE}.pdf
    if [ ! -f $DEST ]
    then
      cp -a ${FILE} ${DEST}
    fi
  done

  for FILE in `find ${SHAKEMAPS_EXTRACT_DIR} -name *-${LOCALE}.png`
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
