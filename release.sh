#!/bin/bash
echo "Export the plugin to a zip with no .git folder"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3"
  exit
fi

VERSION=$1

#update the metadata file version
TMP=metdata.txt$$
cat metadata.txt | \
  sed "s/^[Vv]ersion=[0-9]\.[0-9]/version=${VERSION}/g" \
  > ${TMP}
mv ${TMP} metadata.txt

#update the __init__ version
TMP=__init__.py$$
cat __init__.py | \
  sed "s/[Vv]ersion [0-9]\.[0-9]/Version ${VERSION}/g" \
  > ${TMP} 
mv ${TMP} __init__.py

#remove any crud
rm *.pyc
rm *.*~

echo "You need to commit the version number change before we can package"
git commit -m "Updated version number to ${VERSION}" -a

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR=${PWD##*/}
OUT="/tmp/${DIR}.${1}.zip"
git archive --prefix=${DIR}/ --format zip --output ${OUT} master


echo "Your plugin archive has been generated as"
echo "${OUT}"
