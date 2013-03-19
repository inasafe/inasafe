#!/bin/bash

# Based off the script from QGIS by Tim Sutton and Richard Duivenvoorde

# Name of the dir containing static files
STATIC=_static
# Path to the documentation root relative to script execution dir
DOCROOT=docs
# Path from execution dir of this script to docs sources (could be just
# '' depending on how your sphinx project is set up).
SOURCE=source

pushd .
cd $DOCROOT

SPHINXBUILD=`which sphinx-build`

# GENERATE PDF AND HTML FOR FOLLOWING LOCALES (EN IS ALWAYS GENERATED)
LOCALES='id'

if [ $1 ]; then
  LOCALES=$1
fi

BUILDDIR=build
# be sure to remove an old build dir
rm -rf ${BUILDDIR}
mkdir -p ${BUILDDIR}

# output dirs
PDFDIR=`pwd`/output/pdf
HTMLDIR=`pwd`/output/html
mkdir -p ${PDFDIR}
mkdir -p ${HTMLDIR}

VERSION=`cat source/conf.py | grep "version = '.*'" | grep -o "[0-9]\.[0-9]"`

if [[ $1 = "en" ]]; then
  echo "Not running localization for English."
else
  for LOCALE in ${LOCALES}
  do
    for POFILE in `find i18n/${LOCALE}/LC_MESSAGES/ -type f -name '*.po'`
    do
      MOFILE=`echo ${POFILE} | sed -e 's,\.po,\.mo,'`
      # Compile the translated strings
      echo "Compiling messages to ${MOFILE}"
      msgfmt --statistics -o ${MOFILE} ${POFILE}
    done
  done
fi

# We need to flush the build dir or the translations dont come through
rm -rf ${BUILDDIR}
mkdir ${BUILDDIR}
#Add english to the list and generated docs
LOCALES+=' en'

if [ $1 ]; then
  LOCALES=$1
fi

for LOCALE in ${LOCALES}
# Compile the html docs for this locale
do
  # cleanup all images for the other locale
  rm -rf source/static
  mkdir -p source/static
  # copy english (base) resources to the static dir
  cp -r resources/en/* source/static
  # now overwrite possible available (localised) resources over the english ones
  cp -r resources/${LOCALE}/* source/static

  #################################
  #
  #        HTML Generation
  #
  #################################

  # Now prepare the index-[locale] template which is a manually translated,
  # unique per locale page that gets copied to index.html for the doc
  # generation process.
  cp templates/index-${LOCALE}.html templates/index.html

  echo "Building HTML for locale '${LOCALE}'..."
  ${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b html source ${HTMLDIR}/${LOCALE}

  # Remove the static html copy again
  rm templates/index.html

  #################################
  #
  #         PDF Generation
  #
  #################################
  # experimental sphinxbuild using rst2pdf...
  #${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b pdf source ${BUILDDIR}/latex/${LOCALE}

  # Traditional using texi2pdf....
  # Compile the latex docs for that locale
  ${SPHINXBUILD} -d ${BUILDDIR}/doctrees -D language=${LOCALE} -b latex source ${BUILDDIR}/latex/${LOCALE}
  # Compile the pdf docs for that locale
  # we use texi2pdf since latexpdf target is not available via
  # sphinx-build which we need to use since we need to pass language flag
  pushd .
  cp resources/InaSAFE_footer.png ${BUILDDIR}/latex/${LOCALE}/
  cd ${BUILDDIR}/latex/${LOCALE}/
  # Manipulate our latex a little - first add a standard footer
  
  FOOTER1="\usepackage{wallpaper}"
  FOOTER2="\LRCornerWallPaper{1}{InaSAFE_footer.png}"
  
  # need to build 3x to have proper toc and index
  texi2pdf --quiet InaSAFE-Documentation.tex
  texi2pdf --quiet InaSAFE-Documentation.tex
  texi2pdf --quiet InaSAFE-Documentation.tex
  mv InaSAFE-Documentation.pdf ${PDFDIR}/InaSAFE-${VERSION}-Documentation-${LOCALE}.pdf
  popd
done

rm -rf source/static
#rm -rf ${BUILDDIR}

popd
