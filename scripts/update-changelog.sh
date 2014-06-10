#!/bin/bash

echo "Generate a changelog from git"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3.0"
  exit
fi

VERSION=$1

FILE=/tmp/$$changelog.txt
echo "Changelog for version ${VERSION}" > $FILE
echo "================================" >> $FILE
echo "" >> $FILE
TAG=$(git tag --list | tail -1)
git log --oneline --decorate ${TAG}..HEAD >> $FILE
echo "" >> $FILE
cat CHANGELOG >> $FILE
cp $FILE CHANGELOG
