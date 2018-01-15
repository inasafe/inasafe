#!/bin/bash
echo "Export the plugin to a zip with no .git folder"
echo "And build a windows installer" 

# Make sure has the proper sub module state
git submodule init
git submodule update

VERSION=`cat metadata.txt | grep ^version | sed 's/version=//g'`
STATUS=`cat metadata.txt | grep ^status | sed 's/status=//g'`

if [ "${STATUS}" != "final" ]; then
    VERSION="${VERSION}.${STATUS}"
fi

echo ${VERSION}

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR='inasafe'

OUT="/tmp/${DIR}.${VERSION}.zip"

WORKDIR=/tmp/${DIR}
TARGZFILE="/tmp/${DIR}.tar.gz"

mkdir -p ${WORKDIR}
# Archive source code of the current branch to tar gz file.
# Use git-archive-all since we use git submodule.
brew install git-archive-all
git-archive-all ${TARGZFILE}
# Extract the file
tar -xf ${TARGZFILE} -C ${WORKDIR}
# Remove tar gz file
rm ${TARGZFILE}

rm -rf ${WORKDIR}/${DIR}/docs/en/_static/user*
rm -rf ${WORKDIR}/${DIR}/docs/id/_static/user*
rm -rf ${WORKDIR}/${DIR}/unit_test_data
rm -rf ${WORKDIR}/${DIR}/run*
rm -rf ${WORKDIR}/${DIR}/docs
rm -rf ${WORKDIR}/${DIR}/Vagrantfile
rm -rf ${WORKDIR}/${DIR}/.idea
rm -rf ${WORKDIR}/${DIR}/Makefile
rm -rf ${WORKDIR}/${DIR}/.git*
rm -rf ${WORKDIR}/${DIR}/.scrutinizer.yml
rm -rf ${WORKDIR}/${DIR}/.checkignore.yml
rm -rf ${WORKDIR}/${DIR}/scripts
rm -rf ${WORKDIR}/${DIR}/pylintrc
rm -rf ${WORKDIR}/${DIR}/extras
rm -rf ${WORKDIR}/${DIR}/safe/test
rm -rf ${WORKDIR}/${DIR}/realtime
rm -rf ${WORKDIR}/${DIR}/bin
rm -rf ${WORKDIR}/${DIR}/headless
rm -rf ${WORKDIR}/${DIR}/files
rm -rf ${WORKDIR}/${DIR}/fabfile.py
# Commented out next line for #832 - reinstate when that issue is resolved
#rm -rf ${WORKDIR}/${DIR}/safe_qgis/resources
rm -rf ${WORKDIR}/${DIR}/pylintrc_jenkins
rm -rf ${WORKDIR}/${DIR}/.travis.yml
rm -rf ${WORKDIR}/${DIR}/Dockerfile
rm -rf ${WORKDIR}/${DIR}/docs/README.BEFORE.CHANGING.DOCS.txt
rm -rf ${WORKDIR}/${DIR}/71-apt-cacher-ng
rm -rf ${WORKDIR}/${DIR}/.dockerignore
rm -rf ${WORKDIR}/${DIR}/REQUIREMENTS.txt

find ${WORKDIR}/${DIR} -name test*.py -delete
find ${WORKDIR}/${DIR} -name *_test.py -delete
find ${WORKDIR}/${DIR} -name *.po -delete
find ${WORKDIR}/${DIR} -name *.ts -delete

rm -rf ${WORKDIR}/${DIR}/*.bat


pushd .
cd ${WORKDIR}
find . -name test -exec /bin/rm -rf {} \;
# Compress all images shipped
#for FILE in `find . -type f -name "*.png"`
#do
#    echo "Compressing $FILE"
#    convert -dither FloydSteinberg -colors 128 $FILE $FILE
#done

# The \* tells zip to ignore recursively
rm ${OUT}
zip -r ${OUT} ${DIR} --exclude \*.pyc \
              ${DIR}/.git\* \
              ${DIR}/*.bat \
              ${DIR}/.gitattributes \
              ${DIR}/.settings\* \
              ${DIR}/.pydev\* \
              ${DIR}/.coverage\* \
              ${DIR}/.project\* \
              ${DIR}/.achievements\* \
              ${DIR}/Makefile \
              ${DIR}/scripts\* \
              ${DIR}/impossible_state.* \
              ${DIR}/riab_demo_data\* \
              ${DIR}/\*.*~ \
              ${DIR}/\*test_*.py \
              ${DIR}/\*.*.orig \
              ${DIR}/\*.bat \
              ${DIR}/\*.xcf \
              ${DIR}/\.tx\* \
              ${DIR}/\*.sh \
              ${DIR}/\Vagrantfile \
              ${DIR}/~

popd

#rm -rf ${WORKDIR}

echo "Your plugin archive has been generated as"
ls -lah ${OUT}
echo "${OUT}"

# For nsis installer
brew install rpl
brew install makensis
cp scripts/windows-install-builder.nsi scripts/build.nsi
rpl "[[VERSION]]" "${VERSION}" scripts/build.nsi
rm -rf /tmp/nsis-data
mv ${WORKDIR} /tmp/nsis-data
makensis scripts/build.nsi
rm scripts/build.nsi
mv scripts/*.exe /tmp
echo "NSIS Installer created in /tmp/"
ls /tmp/InaSAFE*.exe


make test-translations
make flake8
