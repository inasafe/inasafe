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
test: clean pep8 pylint dependency_test unwanted_strings run_data_audit testdata_errorcheck test-translations test_suite

# Run the test suite for gui only
guitest: pep8 disabled_tests dependency_test unwanted_strings testdata_errorcheck gui_test_suite

# Run the test suite followed by style checking includes realtime and requires QGIS 2.0
qgis2test: clean pep8 pylint dependency_test unwanted_strings run_data_audit testdata_errorcheck test-translations qgis2_test_suite

quicktest: pep8 pylint dependency_test unwanted_strings run_data_audit test-translations test_suite_quick

# you can pass an argument called PACKAGE to run only tests in that package
# usage: make test_suite_quick PACKAGE=common
test_suite_quick:
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -A 'not slow' -v safe/${PACKAGE} #--with-id

# Similar with test_suite_quick, but for all tests.
# you can pass an argument called PACKAGE to run only tests in that package
# usage: make test_suite_all PACKAGE=common
test_suite_all:
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v safe/${PACKAGE} --with-id

# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --version
	@pep8 --repeat --ignore=E121,E402 --exclude venv,pydev,safe_extras,extras,test_*.py  . || true

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
	@flake8 --version
	@flake8 || true


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

# This one includes safe and realtime and runs against QGIS v2
qgis2_test_suite: testdata
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
	@echo "List of QGis related packages installed."
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
	@echo "Image: kartoza/qgis-testing:boundlessgeo-2.14.7"
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


##########################################################
#
# Make targets specific to Jenkins go below this point
#
##########################################################

jenkins-test: testdata clean
	@echo
	@echo "----------------------------------"
	@echo "Regression Test Suite for Jenkins"
	@echo " against QGIS 2.x"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests --cover-package=safe --with-id --with-xcoverage --with-xunit --verbose --cover-package=safe safe || :

jenkins-qgis2-test: testdata clean
	@echo
	@echo "----------------------------------"
	@echo "Regression Test Suite for Jenkins"
	@echo " against QGIS 2.x"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=safe,realtime safe realtime || :

jenkins-pyflakes:
	@echo
	@echo "----------------------------------"
	@echo "PyFlakes check for Jenkins"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes safe realtime > pyflakes.log || :

jenkins-sloccount:
	@echo "----------------------"
	@echo " Lines of code analysis for Jenkins"
	@echo " Generated using David A. Wheeler's 'SLOCCount'"
	@echo "----------------------"
	# This line is for machine readable output for use by Jenkins
	@sloccount --duplicates --wide --details  safe_api.py safe realtime | fgrep -v .svn > sloccount.sc || :

jenkins-pylint:
	@echo
	@echo "----------------------------------"
	@echo "PyLint check for Jenkins"
	@echo " *_base.py modules are ignored since they are autogenerated by Qt4"
	@echo " we enable -i y option so that we can see message ids as in some"
	@echo " cases we want to suppress warnings in the python code like this:"
	@echo " from pydevd import * # pylint: disable=F0401"
	@echo " with 'F0401' being the warning code."
	@echo "----------------------------------"
	rm -f pylint.log
	@pylint --version
	@-export PYTHONPATH=$(PYTHONPATH):`pwd`/safe_extras; pylint --output-format=parseable --reports=y --rcfile=pylintrc_jenkins safe realtime> pylint.log || :

jenkins-pep8:
	@echo
	@echo "-----------------------------"
	@echo "PEP8 issue check for Jenkins"
	@echo "-----------------------------"
	@pep8 --version
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,E402 --exclude pydev,safe_extras,keywords_dialog_base.py,wizard_dialog_base.py,dock_base.py,options_dialog_base.py,minimum_needs_configuration.py,resources_rc.py,help_base.py,xml_tools.py,system_tools.py,data_audit.py,data_audit_wrapper.py,function_browser_base.py,function_options_dialog_base.py,minimum_needs_base.py,shakemap_importer_base.py,batch_dialog_base.py,osm_downloader_base.py,impact_report_dialog_base.py,impact_merge_dialog_base.py,about_dialog_base.py,extent_selector_base.py,extent_selector_dialog_base.py,function_browser_dialog_base.py,needs_calculator_dialog_base.py,needs_manager_dialog_base.py,osm_downloader_dialog_base.py,shakemap_importer_dialog_base.py . > pep8.log || :

jenkins-realtime-test:

	@echo
	@echo "---------------------------------------------------------------"
	@echo "Regresssion Test Suite for Jenkins (Realtime module only)"
	@echo "if you are going to run more than "
	@echo "one InaSAFE Jenkins job, you should run each on a different"
	@echo "display by changing the :100 option below to a different number"
	@echo "Update: Above is taken care of by xvfb jenkins plugin now"
	@echo "---------------------------------------------------------------"
	# xvfb-run --server-args=":101 -screen 0, 1024x768x24" make check
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); xvfb-run --server-args="-screen 0, 1024x768x24" \
	nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=realtime realtime || :

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
