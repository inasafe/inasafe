#!/usr/bin/env bash

# Check if InaSAFE flag is needed below
qgis_setup.sh inasafe
# FIX default installation because the sources must be in "inasafe" parent folder
rm -rf  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
ln -sf /tests_directory /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
# Check if this line is needed
ln -sf /tests_directory /usr/share/qgis/python/plugins/inasafe

pip3 install -r /tests_directory/REQUIREMENTS.txt
pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt
