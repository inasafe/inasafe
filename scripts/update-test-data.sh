#!/bin/bash

# Simple script to update the test data.

if test -z "$1"
then
  echo "usage: $0 <git hash>"
  echo "e.g. : $0 096fg5"
  exit
fi

VERSION=$1

echo "Updating and setting test data to revision: $VERSION"

if [ ! -d ../inasafe_data ]
then
  # check the repo out since it does not exist
  pushd .
  cd ..
  git clone --depth 1 git://github.com/AIFDR/inasafe_data.git inasafe_data
  popd
fi

pushd .
cd ../inasafe_data
git fetch
git checkout $VERSION
EXITCODE=$?
popd
exit $EXITCODE
