#!/usr/bin/env bash

# After a Pycharm cleaning import process, we rollback some files for now.
# Select the "safe" directory, "Code" then "Optimize imports"

git checkout $(git diff --name-only | grep __init__.py)
git checkout *.xml
git checkout *.svg
git checkout */test_*.py
git checkout safe/gui/widgets/test/profile_widget_example.py
git checkout safe/common/parameters/test/example_group_select.py
git checkout safe/metadata35/
git checkout safe/test/qgis_app.py
git checkout safe/plugin.py
