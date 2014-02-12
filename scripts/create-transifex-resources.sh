#!/bin/bash

# This script is used to register InaSAFE translatable resources with Transifex
# http://transifex.com
#
# Note that this script updates or creates entries in .tx/config file
#
# Tim Sutton, March 2013


#
# Sphinx documentation first
#

LOCALES=`ls docs/i18n`

#
# Now safe package
#
POFILE='safe/i18n/en/LC_MESSAGES/inasafe.po'
RESOURCE='safe/i18n/<lang>/LC_MESSAGES/inasafe.po'

tx set -t PO --auto-local -r inasafe-develop.safe \
  $RESOURCE \
  --source safe/i18n/en/LC_MESSAGES/inasafe.po \
  --source-lang en --execute

for LOCALE in $LOCALES
do
  LOCALEFILE=`echo $POFILE | sed "s/\/en\//\/$LOCALE\//g"`
  tx set -r $RESOURCE -l $LOCALE  "$LOCALEFILE"
done

#
# Now safe_qgis package
#

TSFILE='safe_qgis/i18n/inasafe_en.ts'
RESOURCE='safe_qgis/i18n/inasafe_<lang>.ts'

tx set -t QT --auto-local -r inasafe-develop.safe_qgis \
  $RESOURCE \
  --source-lang en \
  --source $TSFILE \
  --execute

for LOCALE in $LOCALES
do
  LOCALEFILE=`echo $TSFILE | sed "s/\_en/\_$LOCALE/g"`
  tx set -r $RESOURCE -l $LOCALE  "$LOCALEFILE"
done

#Print out a listing of all registered resources
tx status

# Push all the resources to the tx server
tx push -s
