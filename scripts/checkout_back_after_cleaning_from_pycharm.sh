#!/usr/bin/env bash

# After a Pycharm cleaning import process, we rollback some files for now.
# Select the "safe" directory, "Code" then "Optimize imports"

git checkout */__init__.py
git checkout *.xml
git checkout *.svg
git checkout */test_*.py
git checkout safe/plugin.py
