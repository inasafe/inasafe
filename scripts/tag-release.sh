#!/bin/bash

echo "Tag the plugin in git"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3.0"
  exit
fi

VERSION=$1
# Make a git friendly version of the release no
UNDER_VERSION=`echo $VERSION | sed 's/\./\_/g'`
echo "Git friendly Version: ${UNDER_VERSION}"
git tag -s version-${UNDER_VERSION} -m "Version ${VERSION}"
git push --tags origin version-${UNDER_VERSION}


