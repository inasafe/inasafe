#!/bin/bash
#set -x
LOCALE=$1
POFILES=$2
PODIR=i18n/${LOCALE}/LC_MESSAGES
POPATH=${PODIR}/riab.po

# double brackets deal gracefully if path has spaces
if [[ ! -f $POPATH ]]
then
  mkdir -p $PODIR
  xgettext -d ${LOCALE} -o ${POPATH} ${POFILES}
else
  xgettext -j -d ${LOCALE} -o ${POPATH} ${POFILES}
fi
#set +x