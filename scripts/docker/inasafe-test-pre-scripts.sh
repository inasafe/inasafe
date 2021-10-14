#!/usr/bin/env bash

<<<<<<< HEAD
qgis_setup.sh

# FIX default installation because the sources must be in "inasafe" parent folder
rm -rf  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
ln -sf /tests_directory /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
ln -sf /tests_directory /usr/share/qgis/python/plugins/inasafe
=======
qgis_setup.sh inasafe

# FIX default installation because the sources must be in "inasafe" parent folder
rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe
>>>>>>> origin/master

pip3 install -r /tests_directory/REQUIREMENTS.txt
pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt
