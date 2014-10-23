#!/bin/bash
for FILE in `find . -type f -name "*.png" ! -path "./safe_qgis/test/test_data/test_images/*"`
do 
    echo "Compressing $FILE"
    convert -dither FloydSteinberg -colors 128 $FILE $FILE
done
