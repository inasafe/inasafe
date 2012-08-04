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
	make -C gui

docs: compile
	@echo
	@echo "-------------------------------"
	@echo "Compile documentation into html"
	@echo "-------------------------------"
	cd docs; make html >/dev/null; cd ..

#Qt .ts file updates - run to register new strings for translation in gui
update-translation-strings: compile
	@echo "Collecting strings requiring translations. Please provide translations by editing the translation files below:"
	@# Qt translation stuff first.
	@cd gui; pylupdate4 inasafe.pro; cd .
	@$(foreach LOCALE,$(LOCALES), echo "gui/i18n/inasafe_$(LOCALE).ts";)
	@# Gettext translation stuff next.
	@# apply same xgettext command for each supported locale. TS
	@$(foreach LOCALE,$(LOCALES), scripts/update-strings.sh $(LOCALE) $(POFILES);)

#Qt .qm file updates - run to create binary representation of translated strings for translation in gui
compile-translation-strings: compile
	@#Compile qt messages binary
	cd gui; lrelease inasafe.pro; cd ..
	@#compile gettext messages binary
	$(foreach LOCALE,$(LOCALES), msgfmt --statistics -o i18n/$(LOCALE)/LC_MESSAGES/inasafe.mo i18n/$(LOCALE)/LC_MESSAGES/inasafe.po;)

test-translations:
	@echo
	@echo "----------------------------------------------------------------"
	@echo "Missing translations - for more info run: make translation-stats"
	@echo "----------------------------------------------------------------"
	@python scripts/missing_translations.py `pwd` id

translation-stats:
	@echo
	@echo "----------------------"
	@echo "Translation statistics - for more info see http://inasafe.readthedocs.org/en/latest/developer-docs/i18n.html"
	@echo "----------------------"
	@echo
	@echo "Gettext translations (*.po):"
	@echo "----------------------------"
	@$(foreach LOCALE,$(LOCALES), echo 'Locale: $(LOCALE)'; msgfmt --statistics i18n/$(LOCALE)/LC_MESSAGES/inasafe.po;)
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
	@sloccount . | grep '^[0-9]'
	# This line is for machine readble output for use by Jenkins
	@sloccount --duplicates --wide --details . | fgrep -v .svn > sloccount.sc || :

jenkins-test:
	@echo
	@echo "----------------------------------"
	@echo "Regresssion Test Suite for Jenkins"
	@echo "----------------------------------"
	# xvfb-run --server-args="-screen 0, 1024x768x24" make check
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-coverage --with-xunit --verbose --cover-package=storage,engine,impact_functions,gui || :

jenkins-pyflakes:
	@echo
	@echo "----------------------------------"
	@echo "PyFlakes check for Jenkins"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes storage engine impact_functions gui > pyflakes.log || :



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

# Run the test suite followed by pep8 style checking
test: docs test_suite pep8 dependency_test unwanted_strings data_audit test-translations

# Run the test suite followed by pep8 style checking - dont update from svn for test data
test_no_svn: docs test_suite_no_svn pep8 disabled_tests dependency_test unwanted_strings data_audit

# Run the test suite for gui only
guitest: gui_test_suite pep8 disabled_tests dependency_test unwanted_strings

# Run pep8 style checking
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203 --exclude docs,odict.py,is_keywords_dialog_base.py,is_dock_base.py,is_options_dialog_base.py,resources.py,resources_rc.py,is_help_base.py,xml_tools.py,system_tools.py,data_audit.py,data_audit_wrapper.py . || true

# Run entire test suite
test_suite_no_svn: compile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-coverage --cover-package=storage,engine,impact_functions,gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

	@# FIXME (Ole) - to get of the remaining junk I tried to use
	@#  ...| awk 'BEGIN {FS="Object::"} {print $1}'
	@# This does clip the line, but does not flush and puts an extra
	@# newline in.

	@# Report expected failures if any!
	@#echo Expecting 1 test to fail in support of issue #3
	@#echo Expecting 1 test to fail in support of issue #160

# Run entire test suite
test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-coverage --cover-package=storage,engine,impact_functions,gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

	@# FIXME (Ole) - to get of the remaining junk I tried to use
	@#  ...| awk 'BEGIN {FS="Object::"} {print $1}'
	@# This does clip the line, but does not flush and puts an extra
	@# newline in.

	@# Report expected failures if any!
	@#echo Expecting 1 test to fail in support of issue #3
	@#echo Expecting 1 test to fail in support of issue #160

# Run gui test suite only and without svn updating test data
gui_test_suite_no_svn: compile
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-coverage --cover-package=gui gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

# Run gui test suite only
gui_test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); nosetests -v --with-id --with-coverage --cover-package=gui gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

# Get test data
testdata:
	@echo
	@echo "-----------------------------------------------------------"
	@echo "Updating test data - please hit Enter if asked for password"
	@echo "-----------------------------------------------------------"
	@svn co http://www.aifdr.org/svn/inasafe_data ../inasafe_data

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

list_gis_packages:
	@echo
	@echo "---------------------------------------"
	@echo "List of QGis related packages installed"
	@echo "---------------------------------------"
	@dpkg -l | grep qgis || true
	@dpkg -l | grep gdal || true
	@dpkg -l | grep geos || true

data_audit:
	@echo
	@echo "---------------------------------------"
	@echo "Audit of IP status for bundled data    "
	@echo "---------------------------------------"
	@python scripts/data_IP_audit.py

pylint:
	@echo
	@echo "---------------------------------------"
	@echo "Pylint report                          "
	@echo "---------------------------------------"
	pylint --disable=C,R storage engine gui

profile:
	@echo
	@echo "---------------------------------------"
	@echo "Profiling engine                       "
	@echo "---------------------------------------"
	python -m cProfile engine/test_engine.py -s cumulative

##########################################################
#
# Make targets specific to Jenkins go below this point
#
##########################################################

jenkins-test:
	@echo
	@echo "---------------------------------------------------------------"
	@echo "Regresssion Test Suite for Jenkins"
	@echo "if you are going to run more than "
	@echo "one InaSAFE Jenkins job, you should run each on a different"
	@echo "display by changing the :100 option below to a different number"
	@echo "---------------------------------------------------------------"
	# xvfb-run --server-args=":101 -screen 0, 1024x768x24" make check
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); xvfb-run --server-args="-screen 0, 1024x768x24" \
		nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=storage,engine,impact_functions,gui || :

jenkins-realtime-test:
	@echo
	@echo "---------------------------------------------------------------"
	@echo "Regresssion Test Suite for Jenkins (Realtime module only)"
	@echo "if you are going to run more than "
	@echo "one InaSAFE Jenkins job, you should run each on a different"
	@echo "display by changing the :100 option below to a different number"
	@echo "---------------------------------------------------------------"
	# xvfb-run --server-args=":101 -screen 0, 1024x768x24" make check
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); xvfb-run --server-args="-screen 0, 1024x768x24" \
		nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=realtime realtime|| :

jenkins-pyflakes:
	@echo
	@echo "----------------------------------"
	@echo "PyFlakes check for Jenkins"
	@echo "----------------------------------"
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); pyflakes storage engine impact_functions gui realtime > pyflakes.log || :

jenkins-sloccount:
	@echo "----------------------"
	@echo " Lines of code analysis for Jenkins"
	@echo " Generated using David A. Wheeler's 'SLOCCount'"
	@echo "----------------------"
	# This line is for machine readble output for use by Jenkins
	@sloccount --duplicates --wide --details . | fgrep -v .svn > sloccount.sc || :

jenkins-pylint:
	@echo
	@echo "----------------------------------"
	@echo "PyLint check for Jenkins"
	@echo " *_base.py modules are ignored since they are autogenerated by Qt4"
	@echo " we enable -i y option so that we can see message ids as in some"
	@echo " cases we want to suppress warnings in the python code like this:"
	@echo " from pydevd import * # pylint: disable=F0401"
	@echo " with 'F0401' being the warning code."
	@echo " Ignored lines will generate an I0011 message id which are grepped away"
	@echo "----------------------------------"
	rm -f pylint.log
	pylint --output-format=parseable -i y --reports=y --disable=C,R --rcfile=pylintrc --ignore=odict.py,is_help_base.py,is_keywords_dialog_base.py,is_options_dialog_base.py,is_dock_base.py storage engine gui realtime | grep -v 'I0011' > pylint.log || :

jenkins-pep8:
	@echo
	@echo "-----------------------------"
	@echo "PEP8 issue check for Jenkins"
	@echo "-----------------------------"
	@pep8 --repeat --ignore=E203 --exclude docs,odict.py,is_keywords_dialog_base.py,is_dock_base.py,is_options_dialog_base.py,resources.py,resources_rc.py,is_help_base.py,xml_tools.py,system_tools.py,data_audit.py,data_audit_wrapper.py . > pep8.log || :
