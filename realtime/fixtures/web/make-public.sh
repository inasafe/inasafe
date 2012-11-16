#!/bin/bash

#Search for available quakes and make sure they are listed in public

mkdir -p /home/web/quake/public/
cp -r /home/timlinux/dev/python/inasafe-realtime/realtime/fixtures/web/resource/ /home/web/quake/public/
cd /home/web/quake
for FILE in `find shakemaps-extracted -name *.pdf`; do  cp -af $FILE public/`basename $FILE`; done
for FILE in `find shakemaps-extracted -name *.png`; do  cp -af $FILE public/`basename $FILE`; done
