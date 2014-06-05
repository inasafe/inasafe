FILE=/tmp/$$changelog.txt
echo "Changelog for version x.x.x" > $FILE
echo "===========================" >> $FILE
echo "" >> $FILE
TAG=$(git tag --list | tail -1)
git log --oneline --decorate ${TAG}..HEAD >> $FILE
echo "" >> $FILE
cat CHANGELOG >> $FILE
cp $FILE CHANGELOG
