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

# LOCALES = space delimited list of iso codes to generate po files for
LOCALES = id af

default: compile

compile:
	@echo
	@echo "-----------------"
	@echo "Compile GUI forms"
	@echo "-----------------"
	make -C safe_qgis

docs: compile
	@echo
	@echo "-------------------------------"
	@echo "Compile documentation into html"
	@echo "-------------------------------"
	cd docs; make html >/dev/null; cd ..

#Qt .ts file updates - run to register new strings for translation in safe_qgis
update-translation-strings: compile
	@echo "Checking current translation."
	@scripts/update-strings.sh $(LOCALES)

#Qt .qm file updates - run to create binary representation of translated strings for translation in safe_qgis
compile-translation-strings: compile
	@#compile gettext messages binary
	$(foreach LOCALE, $(LOCALES), msgfmt --statistics -o safe/i18n/$(LOCALE)/LC_MESSAGES/inasafe.mo safe/i18n/$(LOCALE)/LC_MESSAGES/inasafe.po;)
	@#Compile qt messages binary
	cd safe_qgis; lrelease inasafe.pro; cd ..

test-translations:
	@echo
	@echo "----------------------------------------------------------------"
	@echo "Missing translations - for more info run: make translation-stats"
	@echo "----------------------------------------------------------------"
	@python scripts/missing_translations.py `pwd` id

translation-stats:
	@echo
	@echo "----------------------"
	@echo "Translation statistics - for more info see http://inasafe.org/developer-docs/i18n.html"
	@echo "----------------------"
	@echo
	@echo "Gettext translations (*.po):"
	@echo "----------------------------"
	@$(foreach LOCALE,$(LOCALES), echo 'Locale: $(LOCALE)'; msgfmt --statistics safe/i18n/$(LOCALE)/LC_MESSAGES/inasafe.po;)
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
	@sloccount safe_qgis safe safe_api.py realtime | grep '^[0-9]'

clean:
	@# FIXME (Ole): Use normal Makefile rules instead
	@# Preceding dash means that make will continue in case of errors
	@# Swapping stdout & stderr and filter out low level QGIS garbage
	@# See http://stackoverflow.com/questions/3618078/pipe-only-stderr-through-a-filter
	@-find . -name '*~' -exec rm {} \;
	@-find . -name '*.pyc' -exec rm {} \;
	@-find . -name '*.pyo' -exec rm {} \;
	@-/bin/rm .noseids 2>/dev/null || true
	@-/bin/rm .coverage 2>/dev/null || true

# Run the test suite followed by style checking
test: docs test_suite pep8 pylint dependency_test unwanted_strings run_data_audit testdata_errorcheck test-translations

# Run the test suite for gui only
guitest: gui_test_suite pep8 disabled_tests dependency_test unwanted_strings testdata_errorcheck

quicktest: test_suite_quick pep8 pylint dependency_test unwanted_strings run_data_audit test-translations

test_suite_quick:
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -A 'not slow' -v safe --stop

# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude docs,odict.py,keywords_dialog_base.py,dock_base.py,options_dialog_base.py,resources.py,resources_rc.py,help_base.py,xml_tools.py,system_tools.py,data_audit.py,data_audit_wrapper.py,impact_functions_doc_base.py,configurable_impact_functions_dialog_base.py . || true

# Run entire test suite
test_suite: compile testdata
	@echo
	@echo "---------------------"
	@echo "Regression Test Suite"
	@echo "---------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH);export QGIS_DEBUG=0;export QGIS_LOG_FILE=/dev/null;export QGIS_DEBUG_FILE=/dev/null;nosetests -v --with-id --with-coverage --cover-package=safe,safe_qgis 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

	@# FIXME (Ole) - to get of the remaining junk I tried to use
	@#  ...| awk 'BEGIN {FS="Object::"} {print $1}'
	@# This does clip the line, but does not flush and puts an extra
	@# newline in.

	@# Report expected failures if any!
	@#echo Expecting 1 test to fail in support of issue #3
	@#echo Expecting 1 test to fail in support of issue #160

# Run gui test suite only
gui_test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	#Noisy version - uncomment if you want to see all qgis stdout
	#@-export PYTHONPATH=`pwd`:$(PYTHONPATH);nosetests -v --with-id --with-coverage --cover-package=safe_qgis safe_qgis 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true
	#Quiet version
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH);export QGIS_DEBUG=0;export QGIS_LOG_FILE=/dev/null;export QGIS_DEBUG_FILE=/dev/null;nosetests -v --with-id --with-coverage --cover-package=safe_qgis safe_qgis 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

# Get test data
# FIXME (Ole): Need to attempt cloning this r/w for those with
# commit rights. See issue https://github.com/AIFDR/inasafe/issues/232
testdata:
	@echo
	@echo "------------------------------------------------------------"
	@echo "Updating inasafe_data - public test and demo data repository"
	@echo "Update the hash to check out a specific data version        "
	@echo "------------------------------------------------------------"
	@scripts/update-test-data.sh 450f2396a6d34a5982e658eeabc92bd4b1d0d354 2>&1 | tee tmp_warnings.txt; [ $${PIPESTATUS[0]} -eq 0 ] && rm -f tmp_warnings.txt || echo "Stored update warnings in tmp_warnings.txt";

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
	@grep -R Xtest * | grep ".py:" | grep -v "docs/build/html" || true

unwanted_strings:
	@echo
	@echo "------------------------------"
	@echo "Strings that should be deleted"
	@echo "------------------------------"
	@grep -R "settrace()" * | grep ".py:" | grep -v Makefile || true
	@grep -R "assert " * | grep ".py:" | grep -v Makefile | grep -v test_ | grep -v utilities_test.py | grep -v odict.py || true

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

	@grep -R PyQt4 $(NONGUI) || true
	@grep -R qgis.core $(NONGUI) || true
	@grep -R "import scipy" $(NONGUI) || true
	@grep -R "from scipy import" $(NONGUI) || true
	@grep -R "django" $(NONGUI) || true
	@grep -R "geonode" $(NONGUI) || true
	@grep -R "geoserver" $(NONGUI) || true
	@grep -R "owslib" $(NONGUI) || true

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
	@pylint --output-format=parseable --reports=n --rcfile=pylintrc -i y safe safe_qgis | wc -l

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --output-format=parseable --reports=n --rcfile=pylintrc -i y safe safe_qgis || true

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
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes safe safe_qgis | wc -l

##########################################################
#
# Make targets specific to Jenkins go below this point
#
##########################################################

jenkins-test: testdata
	@echo
	@echo "----------------------------------"
	@echo "Regresssion Test Suite for Jenkins"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=safe,safe_qgis || :

jenkins-pyflakes:
	@echo
	@echo "----------------------------------"
	@echo "PyFlakes check for Jenkins"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes safe safe_qgis > pyflakes.log || :

jenkins-sloccount:
	@echo "----------------------"
	@echo " Lines of code analysis for Jenkins"
	@echo " Generated using David A. Wheeler's 'SLOCCount'"
	@echo "----------------------"
	# This line is for machine readble output for use by Jenkins
	@sloccount --duplicates --wide --details  safe_api.py safe safe_qgis realtime | fgrep -v .svn > sloccount.sc || :

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
	pylint --output-format=parseable --reports=y --rcfile=pylintrc_jenkins -i y safe safe_qgis > pylint.log || :

jenkins-pep8:
	@echo
	@echo "-----------------------------"
	@echo "PEP8 issue check for Jenkins"
	@echo "-----------------------------"
	@pep8 --repeat --ignore=E203 --exclude docs,odict.py,keywords_dialog_base.py,dock_base.py,options_dialog_base.py,resources.py,resources_rc.py,help_base.py,xml_tools.py,system_tools.py,data_audit.py,data_audit_wrapper.py,impact_functions_doc_base.py,configurable_impact_functions_dialog_base.py . > pep8.log || :
