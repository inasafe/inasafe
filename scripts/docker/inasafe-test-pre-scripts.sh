#!/usr/bin/env bash

qgis_setup.sh inasafe

# FIX default installation because the sources must be in "inasafe" parent folder
rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe

pip3 install -r /tests_directory/REQUIREMENTS.txt
pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt
