#!/bin/bash

# Simple script to update the website documentation after it has been commited into master.
#marco@opengis.ch sept 2012
set -e

#paths
SCRIPTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INASAFEDIR="$SCRIPTDIR/.."
GHPAGESDIR="$SCRIPTDIR/../../inasafe-gh-pages"

# move outside of inasafe-dev dir 
cd $INASAFEDIR/..

#does a gh-pages checkout already exist?
if [ ! -d inasafe-gh-pages ]
then
  # check the repo out since it does not exist
  git clone git@github.com:AIFDR/inasafe.git inasafe-gh-pages
  cd $GHPAGESDIR
  git branch --track gh-pages origin/gh-pages
fi

cd $GHPAGESDIR
#check if a gh-pages branch of inaSAFE is present
set +e
  git checkout gh-pages
set -e
BRANCH="$(git branch 2>/dev/null | sed -e "/^\s/d" -e "s/^\*\s//")"
if [ "$BRANCH" != "gh-pages" ]; then
  echo "Aborting, the inaSAFE branch checkedout is not 'gh-pages', please run git checkout gh-pages"
  exit 1
else
  echo "Environement looks good, lets start"
  git fetch
  echo "Merging lates sources of origin/gh-pages ..."
  git merge origin/gh-pages
  echo "Generating .rst files for API doc..."
  python $SCRIPTDIR/gen_rst_script.py
  echo "Generating .rst files for impact function doc..."
  cd $INASAFEDIR
  make gen_impact_function_doc
  echo "Pulling lates sources of inaSAFE ..."
  git fetch
  git merge origin/master
  echo "Generating docs..."
  make clean docs
  
  git add -A docs/source/api-docs
  MESSAGE="$(git status docs/source/api-docs)"
  #nothing new in local repo, so no need to ask for confirmation for push
  if [[ "$MESSAGE" != *"nothing to commit"* ]]; then
      CONTINUE="n"
      git status docs/source/api-docs
      echo "########################################################"
      echo "Do you want to commit and push the files above to master this should be normally .rst files? [y, n*]:"
      read CONTINUE
      CONTINUE=$(echo $CONTINUE | tr "[:upper:]" "[:lower:]")
      if [ "$CONTINUE" == "y" ]; then
        git commit -m "Automatic updates of api-docs" docs/source/api-docs
        git push origin master
      fi
  fi
  
  echo "Syncing html to gh-pages"
  cd $GHPAGESDIR
  rsync --delete -av --exclude=.buildinfo --exclude=.nojekyll --exclude=CNAME --exclude=.git $INASAFEDIR/docs/build/html/ $GHPAGESDIR
  git add -A
  git commit -m 'Automated docs update'
  git push origin gh-pages
  echo "Done"
  exit 0
fi







