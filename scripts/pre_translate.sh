#!/bin/bash
LOCALES='af id de'

if [ $1 ]; then
  LOCALES=$1
fi


# Create / update the translation catalogue - this will generate the master .pot files
sphinx-build -b gettext . i18n/pot/

# Now iteratively update the locale specific .po files with any new strings needed translation
for LOCALE in ${LOCALES}
do
  echo "Updating translation catalog for ${LOCALE}:"
  echo "------------------------------------"
  mkdir -p i18n/${LOCALE}/LC_MESSAGES
  mkdir -p _static_${LOCALE}
  for FILE in `ls i18n/pot`
  do
    POTFILE=i18n/pot/${FILE}
    POFILE=i18n/${LOCALE}/LC_MESSAGES/`basename ${POTFILE} .pot`.po
    if [ -f $POFILE ];
    then
      echo "Updating strings for ${POFILE}"
      msgmerge -U ${POFILE} ${POTFILE}
    else
      echo "Creating ${POFILE}"
      cp ${POTFILE} ${POFILE} 
    fi
  done
done
