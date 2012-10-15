#!/bin/bash
LOCALES=$*

# get newest .py file
NEWESTPY=0
PYTHONFILES=$(find . -name '*.py')
for PYTHONFILE in $PYTHONFILES
do
  PYTHONFILEMOD=$(stat -c %Y $PYTHONFILE)
  if [ $PYTHONFILEMOD -gt $NEWESTPY ]
  then
    NEWESTPY=$PYTHONFILEMOD
  fi
done

# Gettext translation stuff
# for .po files by applying xgettext command
for LOCALE in $LOCALES
do
  PODIR=safe/i18n/${LOCALE}/LC_MESSAGES
  POPATH=${PODIR}/inasafe.po

  # get modified date of .po file
  LASTMODPOTIME=$(stat -c %Y $POPATH)

  echo "Newst python file: $NEWESTPY Translation last update: $LASTMODPOTIME"
  # only proceed if the po file is older than the newst py file
  if [ $NEWESTPY -gt $LASTMODPOTIME ]
  then
    echo "Newest python file is newer than po file so updating strings"
    # Keep the current field separator
    oIFS=$IFS
    PYFILES=$(egrep -r "import ugettext" . | cut -f 1 -d ':' | grep 'py$' | sort | uniq | tr '\n' ' ')
    echo 'Scanning $PYFILE for new strings'
    #echo
    echo $PODIR
    echo $POPATH
    # double brackets deal gracefully if path has spaces
    if [[ ! -f $POPATH ]]
    then
      mkdir -p $PODIR
      xgettext -d ${LOCALE} -o ${POPATH} ${PYFILES}
    else
      xgettext -j -d ${LOCALE} -o ${POPATH} ${PYFILES}
      # force this to translate
      # -a all strings
      # -j update mode
      xgettext -a -j -d ${LOCALE} -o ${POPATH} safe/common/dynamic_translations.py
    fi

    # Spit out files that need to be edited
    echo "$POPATH"
  else
    echo "No need to update $POPATH because no python files has been updated since the last update translation."
  fi
done

# Qt translation stuff
# for .ts file
UPDATE=false
for LOCALE in $LOCALES
do
  TSFILE="safe_qgis/i18n/inasafe_"$LOCALE".ts"
  TSMODTIME=$(stat -c %Y $TSFILE)
  if [ $NEWESTPY -gt $TSMODTIME ]
  then
    UPDATE=true
    break
  fi
done

if [ $UPDATE == true ]
then
  cd safe_qgis
  pylupdate4 -noobsolete inasafe.pro
  cd ..
  echo "Please provide translations by editing the translation files below:"
  for LOCALE in $LOCALES
  do
    echo "safe_qgis/i18n/inasafe_"$LOCALE".ts"
  done
else
  echo "No need to edit any translation files (.ts) because no python files has been updated since the last update translation. "
fi

