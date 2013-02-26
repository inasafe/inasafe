#!/bin/bash

# Simple script to update the test data.

if test -z "$1"
then
  echo "usage: $0 <git hash>"
  echo "e.g. : $0 096fg5"
  exit
fi

VERSION=$1

echo "Updating test data"

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

# Checkout desired version
# Use unneccessary force because
# local files might have been modified
# and can block the checkout. Issue
# https://github.com/AIFDR/inasafe/issues/313
#
# However this is dangerous as it will kill
# any new file put under git in the detached branch.
# More scary, any file added (but not committed or
# not under git) under master will also disappear. Why?
echo "Setting test data to revision: $VERSION"
git checkout --force $VERSION
EXITCODE=$?
popd
exit $EXITCODE
