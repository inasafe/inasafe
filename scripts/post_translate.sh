#!/bin/bash

# Name of the dir containing static files
STATIC=_static
# Path to the documentation root relative to script execution dir
DOCROOT=docs
# Path from execution dir of this script to docs sources (could be just
# '' depending on how your sphinx project is set up).
SOURCE=source

pushd .
cd $DOCROOT/$SOURCE

LOCALES='af id de'

if [ $1 ]; then
  LOCALES=$1
fi

for LOCALE in $LOCALES
do
  for POFILE in `ls i18n/${LOCALE}/LC_MESSAGES/*.po`
  do
    MOFILE=i18n/${LOCALE}/LC_MESSAGES/`basename ${POFILE} .po`.mo
    # Compile the translated strings
    echo "Compiling messages to ${MOFILE}"
    msgfmt --statistics -o ${MOFILE} ${POFILE}
  done
done

# We need to flush the build dir or the translations dont come through
cd .. 
rm -rf build
# Add english to the list and generated docs
# TODO: Just extend $LOCALES rather for DRY
LOCALES='en af id de'

if [ $1 ]; then
  LOCALES=$1
fi

for LOCALE in ${LOCALES}
do
  # Compile the html docs for this locale
  #set -x
  rm -rf $SOURCE/$STATIC
  cp -r $SOURCE/${STATIC}_${LOCALE} $SOURCE/$STATIC
  echo "Building HTML for locale '${LOCALE}'..."
  sphinx-build -D language=${LOCALE} -b html $SOURCE build/html/${LOCALE}

  # Compile the latex docs for that locale
  sphinx-build -D language=${LOCALE} -b latex $SOURCE build/latex/${LOCALE}
  # Compile the pdf docs for that locale
  # we use texi2pdf since latexpdf target is not available via 
  # sphinx-build which we need to use since we need to pass language flag
  pushd .
  cd build/latex/${LOCALE}/
  texi2pdf --quiet  InaSAFEManual.tex
  mv InaSAFEManual.pdf InaSAFEManual-${LOCALE}.pdf
  popd
  rm -rf $STATIC
done

popd
