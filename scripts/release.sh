#!/bin/bash
echo "Export the plugin to a zip with no .git folder"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3.0"
  exit
fi

VERSION=$1

#update the metadata file version
TMP=metdata.txt$$
cat metadata.txt | \
  sed "s/^[Vv]ersion=[0-9]\.[0-9]\.[0-9v]/version=${VERSION}/g" \
  | sed "s/^InaSAFE-dev/InaSAFE/g" \
  > ${TMP}
mv ${TMP} metadata.txt

#update the __init__ version
TMP=__init__.py$$
cat __init__.py | \
  sed "s/^[Vv]ersion=[0-9]\.[0-9]\.[0-9v]/version=${VERSION}/g" \
  | sed "s/^InaSAFE-dev/InaSAFE/g" \
  > ${TMP} 
mv ${TMP} __init__.py

#remove any crud
find . -name "*.pyc" -exec rm -rf {} \;
find . -name "*.*~" -exec rm -rf {} \;

#regenerate docs
make docs

echo "You need to commit the version number change before we can package"
git commit -m "Updated version number to ${VERSION}" -a

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR=${PWD##*/}
OUT="/tmp/${DIR}.${1}.zip"
# Cant use git archive since we need generated docs to be bundled
#git archive --prefix=${DIR}/ --format zip --output ${OUT} master

# The \* tells zip to ignore recursively
rm ${OUT}
zip -r ${OUT} ../${DIR} --exclude \*.pyc \
                                  ../${DIR}/docs/source\* \
                                  ../${DIR}/.git\* \
                                  ../${DIR}/.settings\* \
                                  ../${DIR}/.pydev\* \
                                  ../${DIR}/.coverage\* \
                                  ../${DIR}/.project\* \
                                  ../${DIR}/.achievements\* \
                                  \*.noseids \
                                  ../${DIR}/scripts\* \
                                  ../${DIR}/impossible_state.* \
                                  ../${DIR}/riab_demo_data\* \
                                  \*.*~ \
                                  \*test_*.py \
                                  \*.*.orig \
                                  \*.bat \
                                  \*.xcf
                                  



echo "Your plugin archive has been generated as"
ls -lah ${OUT}
echo "${OUT}"
