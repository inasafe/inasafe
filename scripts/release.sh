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

#regenerate docs
rm -rf docs/build
make docs

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR=${PWD##*/}

# For some reason sphinx copies image resources both into build/_static and build/images
# _static should hold just theme based resources
# _images should contain all document referenced resources - sphinx flattens the dir structure
# Normally we wouldn't care but we want to bundle this as documentation so we do care about size
pushd .
cd docs/build/html
for FILE in `ls _images/` 
do 
  echo "Deleting $FILE from _static"
  rm _static/${FILE}
done
rm -rf _static/screenshot*
rm -rf _static/tutorial
popd

OUT="/tmp/${DIR}.${1}.zip"

rm -rf /tmp/${DIR}
mkdir /tmp/${DIR}
git archive `git branch | grep '\*'| sed 's/^\* //g'` | tar -x -C /tmp/${DIR}
rm -rf /tmp/${DIR}/docs/
rm -rf /tmp/${DIR}/unit_test_data
rm -rf /tmp/${DIR}/.idea
rm -rf /tmp/${DIR}/Makefile
rm -rf /tmp/${DIR}/.git*
rm -rf /tmp/${DIR}/scripts
rm -rf /tmp/${DIR}/pylintrc
rm -rf /tmp/${DIR}/extras
rm -rf /tmp/${DIR}/safe/test
rm -rf /tmp/${DIR}/safe_qgis/resources
rm -rf /tmp/${DIR}/pylintrc_jenkins
rm -rf /tmp/${DIR}/.travis.yml
rm -rf /tmp/${DIR}/setup.py


find /tmp/${DIR} -name test*.py -delete
find /tmp/${DIR} -name *_test.py -delete
find /tmp/${DIR} -name *.po -delete
find /tmp/${DIR} -name *.ts -delete
rm -rf /tmp/${DIR}/*.bat
mkdir -p /tmp/${DIR}/docs/build
cp -r docs/build/html /tmp/${DIR}/docs/build/html
pushd .
cd /tmp/
# The \* tells zip to ignore recursively
rm ${OUT}
zip -r ${OUT} ${DIR} --exclude \*.pyc \
              ${DIR}/docs/source\* \
              ${DIR}/docs/*.odf\
              ${DIR}/docs/*.odg\
              ${DIR}/docs/build/doctrees\* \
              ${DIR}/docs/build/html\.buildinfo\* \
              ${DIR}/docs/cloud_sptheme\* \
              ${DIR}/docs/Flyer_InaSafe_FINAL.pdf \
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
              ${DIR}/~ 
              #${DIR}/docs/*.jpg\
              #${DIR}/docs/*.jpeg\
              #${DIR}/docs/*.png\
              
popd


echo "Your plugin archive has been generated as"
ls -lah ${OUT}
echo "${OUT}"
