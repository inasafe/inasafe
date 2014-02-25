#!/bin/bash

echo "Note: We assume that you have a working build environment for the docs."

if [ ! -d ../inasafe-doc ]
then
  # check the repo out since it does not exist
  pushd .
  cd ..
  git clone --depth 1 git://github.com/AIFDR/inasafe-doc.git inasafe-doc
  cd inasafe-doc
  scripts/post_translate_application_docs.sh
  popd
fi

cp -r ../inasafe-doc/docs/output-app-docs/html/* ${WORKDIR}/${DIR}/docs/
rm -rf ${WORKDIR}/${DIR}/docs/en/_static/user*
rm -rf ${WORKDIR}/${DIR}/docs/id/_static/user*
