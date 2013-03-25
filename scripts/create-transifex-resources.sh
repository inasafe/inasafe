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

for ITEM in user-docs developer-docs tutorial-docs
do
  for POFILE in `find docs/i18n/en/LC_MESSAGES/${ITEM}/ -type f -name '*.po'`
  do
    # get the po file replacing 'en' with '<lang>'
    GENERICFILE=`echo $POFILE | sed 's/\/en\//\/<lang>\//g' | sed 's/\/\//\//g'`
    echo $GENERICFILE
    # Get the filename only part of the po file so we can use that
    # name when registering the resource
    BASE=`basename $GENERICFILE .po`
    BASE=`echo $BASE | sed 's/_/-/g' | sed 's/ /-/g'`
    RESOURCE=inasafe.${ITEM}-$BASE
    # Register each po file as a transifex resource (an individual translatable file)
    #set -x
    tx set -t PO --auto-local -r $RESOURCE \
      "$GENERICFILE" \
      --source-lang en \
      --execute
    #set +x
    # Now register the language translations for the localised po file against
    # this resource.
    for LOCALE in $LOCALES
    do
        LOCALEFILE=`echo $POFILE | sed "s/\/en\//\/$LOCALE\//g"`
        tx set -r $RESOURCE -l $LOCALE  "$LOCALEFILE" 
    done 
    # When we are done in this block we should have created a section in the
    # .tx/config file that looks like this:
    #
    #
    #	[inasafe.user-docs-faq]
    #	file_filter = docs/i18n/<lang>/LC_MESSAGES/user-docs/faq.po
    #	source_file = docs/i18n/en/LC_MESSAGES/user-docs/faq.po
    #	source_lang = en
    #	trans.id = docs/i18n/id/LC_MESSAGES/user-docs/faq.po
    #	type = PO
  done
done
#
# Now safe package
#
POFILE='safe/i18n/en/LC_MESSAGES/inasafe.po'
RESOURCE='safe/i18n/<lang>/LC_MESSAGES/inasafe.po'

tx set -t PO --auto-local -r inasafe.safe \
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

tx set -t QT --auto-local -r inasafe.safe_qgis \
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
