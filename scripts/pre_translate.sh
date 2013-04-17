#!/bin/bash
# Path to the documentation root relative to script execution dir
DOCROOT=docs
# Path from execution dir of this script to docs sources (could be just
# '' depending on how your sphinx project is set up).
SOURCE=source
# Name of the dir containing static files
STATIC=static

LOCALES='id'

if [ $1 ]; then
  LOCALES=$1
fi

pushd .
cd $DOCROOT

# Create / update the translation catalogue - this will generate the master .pot files
mkdir -p i18n/pot
# Create a (temporary) static directory in source to hold all (localised ) static content
mkdir -p source/static

# copy english resources to static to be able to do a proper sphinx-build
cp -r resources/en/* source/static/

BUILDDIR=build
# be sure to remove an old build dir
rm -rf ${BUILDDIR}
mkdir ${BUILDDIR}

# Create / update the translation catalogue - this will generate the master
# .pot files
sphinx-build -d ${BUILDDIR}/doctrees -b gettext $SOURCE i18n/pot/

# Now iteratively update the locale specific .po files with any new strings
# needed translation
for LOCALE in ${LOCALES}
do
  echo "Updating translation catalog for ${LOCALE}:"
  echo "------------------------------------"
  mkdir -p i18n/${LOCALE}/LC_MESSAGES
  # cleanup images from static (different locales can have different localized images)
  rm -rf source/static/*
  # Clone the en resources and then overwrite with any localised versions of the same files.
  cp -r resources/en/* source/static/
  PODIR=resources/${LOCALE}
  if [ -d $PODIR ];
  then
    cp -r ${PODIR}/* source/static/
  fi

  # Merge or copy all the updated pot files over to locale specific po files
  for FILE in `find i18n/pot/ -type f`
  do
    POTFILE=${FILE}
    POFILE=`echo ${POTFILE} | sed -e 's,\.pot,\.po,' | sed -e 's,pot,'${LOCALE}'/LC_MESSAGES,'`
    if [ -f $POFILE ];
    then
      echo "Updating strings for ${POFILE}"
      msgmerge -U ${POFILE} ${POTFILE}
    else
      echo "Creating ${POFILE}"
      mkdir -p `echo $(dirname ${POFILE})`
      cp ${POTFILE} ${POFILE}
    fi
  done
done

# Now get rid of temporary POT files
rm -rf i18n/pot
rm -rf source/static

popd
