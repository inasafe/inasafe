#!/bin/bash

echo "A script to generate a source video progression"
echo "see http://woostuff.wordpress.com/2011/01/03/generating-a-gource-source-commit-history-visualization-for-qgis-quantum-gis/"
echo "Run it from the root directory e.g. scripts/$0"

# OSX installation for gource:

# Install brew
# brew install ffmpeg
# brew install gource

gource --title "InaSAFE" --logo resources/img/icons/icon.png \
    --hide filenames \
    --date-format "%d, %B %Y" \
    --seconds-per-day 0.05 \
    --highlight-all-users \
    --auto-skip-seconds 0.5 \
    --file-idle-time 0 \
    --max-files 999999999 \
    --multi-sampling \
    -b ffffff \
    --stop-at-end \
    --elasticity 0.1 \
    --disable-progress \
    --user-friction .2 \
    --output-ppm-stream - | \
 ffmpeg -an -threads 4 -y -vb 8000000 -r 60 -f image2pipe \
        -vcodec ppm -i - -vcodec libx264 -b 3000K inasafe-history.avi
