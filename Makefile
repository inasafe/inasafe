#/***************************************************************************
#
# InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
#                             -------------------
#        begin                : 2012-01-09
#        copyright            : (C) 2012 by Australia Indonesia Facility for Disaster Reduction
#        email                : ole.moller.nielsen@gmail.com
# ***************************************************************************/
#
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# Makefile for InaSAFE - QGIS
SHELL := /bin/bash
NONGUI := safe
GUI := gui
ALL := $(NONGUI) $(GUI)  # Would like to turn this into comma separated list using e.g. $(subst,...) or $(ALL, Wstr) but None of that works as described in the various posts
DIR := ${CURDIR}

# LOCALES = space delimited list of iso codes to generate po files for
# Please dont remove en here
LOCALES = en id fr vi es_ES

default: quicktest

#Qt .ts file updates - run to register new strings for translation in safe_qgis
update-translation-strings:
	# update application strings
	@echo "Checking current translation."
	@scripts/update-strings.sh $(LOCALES)

#Qt .qm file updates - run to create binary representation of translated strings for translation in safe_qgis
compile-translation-strings:
	@#Compile qt messages binary
	@scripts/create_pro_file.sh
	@lrelease-qt4 inasafe.pro
	@rm inasafe.pro

test-translations:
	@echo
	@echo "----------------------------------------------------------------"
	@echo "Missing translations - for more info run: make translation-stats"
	@echo "----------------------------------------------------------------"
	@python scripts/missing_translations.py `pwd` id
	@python scripts/missing_translations.py `pwd` fr
	@python scripts/missing_translations.py `pwd` af
	@python scripts/missing_translations.py `pwd` es_ES
	@python scripts/missing_translations.py `pwd` vi


translation-stats:
	@echo
	@echo "----------------------"
	@echo "Translation statistics - for more info see http://inasafe.org/developer-docs/i18n.html"
	@echo "----------------------"
	@echo
	@echo "Qt translations (*.ts):"
	@echo "----------------------------"
	@scripts/string-stats.sh

lines-of-code:
	@echo "----------------------"
	@echo " Lines of code analysis"
	@echo " Generated using David A. Wheeler's 'SLOCCount'"
	@echo "----------------------"
	@git log | head -3
	@sloccount safe realtime | grep '^[0-9]'

changelog:
	@echo "----------------------"
	@echo "Generate changelog and append it to CHANGELOG"
	@echo "----------------------"
	@read -p "Version e.g. 1.0.0: " VERSION; \
	    scripts/update-changelog.sh $$VERSION

tag:
	@echo
	@echo "------------------------------------"
	@echo "Tagging the release."
	@echo "------------------------------------"
	@# Note that make runs commands in a subshell so
	@# variable context is lost from one line to the next
	@# So we need to do everything as a single line command
	@read -p "Version e.g. 1.0.0: " VERSION; \
	    scripts/tag-release.sh $$VERSION


clean:
	@# FIXME (Ole): Use normal Makefile rules instead
	@# Preceding dash means that make will continue in case of errors
	@# Swapping stdout & stderr and filter out low level QGIS garbage
	@# See http://stackoverflow.com/questions/3618078/pipe-only-stderr-through-a-filter
	@-find . -name '*~' -exec rm {} \;
	@-find . -name '*.pyc' -exec rm {} \;
	@-find . -name '*.pyo' -exec rm {} \;
	@# Clean stray merge working files from git
	@-find . -name '*.orig' -exec rm {} \;
	@-/bin/rm .noseids 2>/dev/null || true
	@-/bin/rm .coverage 2>/dev/null || true


# Run the test suite followed by style checking
test: clean flake8 pylint dependency_test unwanted_strings run_data_audit testdata_errorcheck test-translations test_suite

# Run the test suite for gui only
guitest: flake8 disabled_tests dependency_test unwanted_strings testdata_errorcheck gui_test_suite

# Run the test suite followed by style checking includes realtime and requires QGIS 3.0
qgis2test: clean flake8 pylint dependency_test unwanted_strings run_data_audit testdata_errorcheck test-translations qgis3_test_suite

quicktest: flake8 pylint dependency_test unwanted_strings run_data_audit test-translations test_suite_quick

# you can pass an argument called PACKAGE to run only tests in that package
# usage: make test_suite_quick PACKAGE=common
test_suite_quick:
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -A 'not slow' -v safe/${PACKAGE} #--with-id

# Similar with test_suite_quick, but for all tests.
# you can pass an argument called PACKAGE to run only tests in that package
# usage: make test_suite_all PACKAGE=common
test_suite_all:
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v safe/${PACKAGE} --with-id

# Run pep257 style checking
#http://pypi.python.org/pypi/pep257
# http://pep257.readthedocs.io/en/latest/error_codes.html
# D104 will be disabled.
pep257:
	@echo
	@echo "-----------"
	@echo "PEP257 issues"
	@echo "-----------"
	@pep257 --version
	@pep257 --ignore=D102,D103,D104,D105,D200,D202,D203,D205,D210,D211,D300,D301,D302,D400,D401 safe/ || true

# Run flake8 style checking
flake8:
	@echo
	@echo "-----------"
	@echo "Flake8 issues"
	@echo "-----------"
	@python3 -m flake8 --version
	@python3 -m flake8 || true


# Run entire test suite - excludes realtime until we have QGIS 2.0 support
test_suite: testdata
	@echo
	@echo "---------------------"
	@echo "Regression Test Suite"
	@echo "---------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH);export QGIS_DEBUG=0;export QGIS_LOG_FILE=/dev/null;export QGIS_DEBUG_FILE=/dev/null;nosetests -v --with-id --with-coverage --cover-package=safe safe 3>&1 1>&2 2>&3 3>&- || true

	@# Report expected failures if any!
	@#echo Expecting 1 test to fail in support of issue #3
	@#echo Expecting 1 test to fail in support of issue #160

# Run safe package tests only
safe_test_suite: testdata
	@echo
	@echo "---------------------"
	@echo "Safe Regression Test Suite"
	@echo "---------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id \
	--with-coverage --cover-package=safe safe  3>&1 1>&2 2>&3 3>&- || true

# This one includes safe and realtime and runs against QGIS v3
qgis3_test_suite: testdata
	@echo
	@echo "---------------------"
	@echo "Regression Test Suite"
	@echo "---------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH);export QGIS_DEBUG=0;export QGIS_LOG_FILE=/dev/null;export QGIS_DEBUG_FILE=/dev/null;nosetests -v --with-id --with-coverage --cover-package=safe safe 3>&1 1>&2 2>&3 3>&- | true

# Run realtime test suite only
realtime_test_suite:

	@echo
	@echo "-------------------"
	@echo "Realtime Test Suite"
	@echo "-------------------"

	@# Preceding dash means that make will continue in case of errors
	#Quiet version
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH);export QGIS_DEBUG=0;export QGIS_LOG_FILE=/dev/null;export QGIS_DEBUG_FILE=/dev/null;nosetests -v --with-id --with-coverage --cover-package=realtime realtime 3>&1 1>&2 2>&3 3>&- || true

# Get test data
# FIXME (Ole): Need to attempt cloning this r/w for those with
# commit rights. See issue https://github.com/AIFDR/inasafe/issues/232
testdata:
	@echo
	@echo "------------------------------------------------------------"
	@echo "Updating inasafe_data - public test and demo data repository"
	@echo "Update the hash to check out a specific data version        "
	@echo "------------------------------------------------------------"
	@scripts/update-test-data.sh 2a264a166890ef8a276b285f60809cdce95fbb04 2>&1 | tee tmp_warnings.txt; [ $${PIPESTATUS[0]} -eq 0 ] && rm -f tmp_warnings.txt || echo "Stored update warnings in tmp_warnings.txt";

#check and show if there was an error retrieving the test data
testdata_errorcheck:
	@echo
	@echo "---------------------"
	@echo "Inasafe_data problems"
	@echo "---------------------"
	@[ -f tmp_warnings.txt ] && more tmp_warnings.txt || true; rm -f tmp_warnings.txt

disabled_tests:
	@echo
	@echo "--------------"
	@echo "Disabled tests"
	@echo "--------------"
	@grep -R [X,x]test * | grep ".py:" || true

unwanted_strings:
	@echo
	@echo "------------------------------"
	@echo "Strings that should be deleted"
	@echo "------------------------------"

	@grep -R "settrace()" * | grep ".py:" | grep -v Makefile | grep -v pydev || true

	@grep -R "assert " * | grep ".py:" | grep -v Makefile | grep -v test_ | \
	grep -v utilities_for_testing.py | grep -v odict.py | grep -v .pyc | \
	grep -v gui_example.py | grep -v message_element.py | grep -v pydev | \
	grep -v safe_extras || true

dependency_test:
	@echo
	@echo "------------------------------------------------"
	@echo "List of unwanted dependencies in InaSAFE library"
	@echo "------------------------------------------------"

	@# Need disjunction with "true" because grep returns non-zero error code if no matches were found
	@# nielso@shakti:~/sandpit/inasafe$ grep PyQt4 engine
	@# nielso@shakti:~/sandpit/inasafe$ echo $?
	@# 1
	@# See http://stackoverflow.com/questions/4761728/gives-an-error-in-makefile-not-in-bash-when-grep-output-is-empty why we need "|| true"

	@# Since InaSAFE 2.0 we now can use PyQt4 libs in safe lib
	@#grep -R PyQt4 $(NONGUI) | grep -v gui_example.py | grep -v message_element|| true
	@# Since InaSAFE 2.0 we now can use qgis libs in safe lib
	@#grep -R qgis.core $(NONGUI) || true
	@grep -R "import scipy" $(NONGUI) || true
	@grep -R "from scipy import" $(NONGUI) || true
	@grep -R "django" $(NONGUI) || true
	@grep -R "geonode" $(NONGUI) || true
	@grep -R "geoserver" $(NONGUI) || true
	@grep -R "owslib" $(NONGUI) || true
	@# Allowed since 2.0
	@#grep -R "safe_extras" $(NONGUI) || true

list_gpackages:
	@echo
	@echo "----------------------------------------"
	@echo "List of Qgis related packages installed."
	@echo "----------------------------------------"
	@dpkg -l | grep qgis || true
	@dpkg -l | grep gdal || true
	@dpkg -l | grep geos || true

data_audit: testdata run_data_audit

run_data_audit:
	@echo
	@echo "-----------------------------------"
	@echo "Audit of IP status for bundled data"
	@echo "-----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); python scripts/data_IP_audit.py

pylint-count:
	@echo
	@echo "---------------------------"
	@echo "Number of pylint violations"
	@echo "For details run make pylint"
	@echo "---------------------------"
	@pylint --output-format=parseable --reports=n --rcfile=pylintrc safe realtime | wc -l

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --version
	@pylint --reports=n --rcfile=pylintrc safe realtime || true

profile:
	@echo
	@echo "----------------"
	@echo "Profiling engine"
	@echo "----------------"
	python -m cProfile safe/engine/test_engine.py -s time

pyflakes:
	@echo
	@echo "---------------"
	@echo "PyFlakes issues"
	@echo "---------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes safe realtime | wc -l

indent:
	@echo
	@echo "---------------"
	@echo "Check indentation is at 4 spaces (and apply fix)"
	@echo "---------------"
	@# sudo apt-get install python2.7-examples for reindent script
	python /usr/share/doc/python2.7/examples/Tools/scripts/reindent.py *.py


##########################################################
#
# A little helper to trigger a nightly build and an
# experimental build on the InaSAFE server.
#
# You need to have the correct ssh configs and keys set
# up in order for this to work.
#
##########################################################

build-nightlies:
	@echo "Building nightlies"
	@ssh inasafe-docker /home/data/experimental.inasafe.org/build_nightly_from_host.sh
	@ssh inasafe-docker /home/data/nightly.inasafe.org/build_nightly_from_host.sh
	@rsync -av inasafe-docker:/home/data/experimental.inasafe.org ../
	@rsync -av inasafe-docker:/home/data/nightly.inasafe.org ../

##########################################################
#
# Make targets specific to Docker go below this point
#
##########################################################

docker-test:
	@echo
	@echo "----------------------------------"
	@echo "Run tests in docker"
	@echo "Image: qgis/qgis with the LTR version of QGIS"
	@echo "You can change the tested package in 'test_suite.py' in the 'test_package' function."
	@echo "----------------------------------"
	@./run-docker-test.sh

docker-update-translation-strings:
	@echo "Update translation using docker"
	@docker run -t -i -v $(DIR):/home kartoza/qt-translation make update-translation-strings

docker-compile-translation-strings:
	@echo "Update translation using docker"
	@docker run -t -i -v $(DIR):/home kartoza/qt-translation make compile-translation-strings

docker-test-translation:
	@echo "Update translation using docker"
	@docker run -t -i -v $(DIR):/home kartoza/qt-translation make test-translations

apidocs:
	@echo
	@echo "---------------------------------------------------------------"
	@echo ""Generating API doc for InaSAFE
	@echo "---------------------------------------------------------------"
	@echo "Please make sure you have cloned inasafe-doc repository"
	@echo "Generating RST files for apidoc..."
	@sphinx-apidoc -f -e -o docs/apidocs safe realtime
	@echo "RST files for apidocs has been created."
	@echo "Building HTML API docs..."
	@cd docs && $(MAKE) html
	@echo "HTML API docs has been builded."
	@echo "You can look it under docs/_build directory.."
