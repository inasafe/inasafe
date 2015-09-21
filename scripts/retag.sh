#!/bin/bash
echo "Deletes existing tag for this release, repackages and re-tags"
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

echo "Deleting current tags"
git tag -d version-${UNDER_VERSION}
git push upstream :refs/tags/version-${UNDER_VERSION}

# Preferred - signed version
#git tag -s version-${UNDER_VERSION} -m "Version ${VERSION}"
# Less preferred - unsigned version
git tag version-${UNDER_VERSION} -m "Version ${VERSION}"
git push --tags upstream version-${UNDER_VERSION}

scripts/release.sh ${VERSION}
