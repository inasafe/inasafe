#!/bin/bash
echo "Export the plugin to a zip with no .git folder"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3.0"
  exit
fi

VERSION=$1

# TODO
#replace _type_ = 'alpha' or 'beta' with final

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR='inasafe'

OUT="/tmp/${DIR}.${1}.zip"

WORKDIR=/tmp/${DIR}$$
mkdir -p ${WORKDIR}/${DIR}
git archive `git branch | grep '\*'| sed 's/^\* //g'` | tar -x -C ${WORKDIR}/${DIR}
rm -rf ${WORKDIR}/${DIR}/docs/en/_static/user*
rm -rf ${WORKDIR}/${DIR}/docs/id/_static/user*
rm -rf ${WORKDIR}/${DIR}/unit_test_data
rm -rf ${WORKDIR}/${DIR}/.idea
rm -rf ${WORKDIR}/${DIR}/Makefile
rm -rf ${WORKDIR}/${DIR}/.git*
rm -rf ${WORKDIR}/${DIR}/scripts
rm -rf ${WORKDIR}/${DIR}/pylintrc
rm -rf ${WORKDIR}/${DIR}/extras
rm -rf ${WORKDIR}/${DIR}/safe/test
rm -rf ${WORKDIR}/${DIR}/realtime
rm -rf ${WORKDIR}/${DIR}/files
rm -rf ${WORKDIR}/${DIR}/fabfile.py
# Commented out next line for #832 - reinstate when that issue is resolved
#rm -rf ${WORKDIR}/${DIR}/safe_qgis/resources
rm -rf ${WORKDIR}/${DIR}/pylintrc_jenkins
rm -rf ${WORKDIR}/${DIR}/.travis.yml
rm -rf ${WORKDIR}/${DIR}/setup.py

find ${WORKDIR}/${DIR} -name test*.py -delete
find ${WORKDIR}/${DIR} -name *_test.py -delete
find ${WORKDIR}/${DIR} -name *.po -delete
find ${WORKDIR}/${DIR} -name *.ts -delete

rpl "from safe.common.testing import HAZDATA, EXPDATA, TESTDATA, UNITDATA, BOUNDDATA" "" ${WORKDIR}/${DIR}/safe/api.py

rm -rf ${WORKDIR}/${DIR}/*.bat


pushd .
cd ${WORKDIR}
find . -name test -exec /bin/rm -rf {} \;
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
