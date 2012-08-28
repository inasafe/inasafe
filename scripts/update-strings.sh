#!/bin/bash
#set -x
LOCALE=$1
PODIR=safe/i18n/${LOCALE}/LC_MESSAGES
POPATH=${PODIR}/inasafe.po

# Keep the current field separator
oIFS=$IFS
POFILES=$(egrep -r "import ugettext" . | cut -f 1 -d ':' | grep 'py$' | sort | uniq | tr '\n' ' ')
#echo $POFILES
# double brackets deal gracefully if path has spaces
if [[ ! -f $POPATH ]]
then
  mkdir -p $PODIR
  xgettext -d ${LOCALE} -o ${POPATH} ${POFILES}
else
  xgettext -j -d ${LOCALE} -o ${POPATH} ${POFILES}
fi
#set +x

# Spit out files that need to be edited
echo "$POPATH"