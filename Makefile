#/***************************************************************************
# Riab
#
# Disaster risk assessment tool developed by AusAid and World Bank
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

# Makefile for Risk in a Box - QGIS

NONGUI := storage engine impact_functions
GUI := gui
ALL := $(NONGUI) $(GUI)  # Would like to turn this into comma separated list using e.g. $(subst,...) or $(ALL, Wstr) but None of that works as described in the various posts

default: compile

compile:
	make -C gui

docs: compile
	cd docs; make html; cd ..

#Qt .ts file updates - run to register new strings for translation in gui
update-translation-strings: compile
	cd gui; pylupdate4 riab.pro; cd ..
	xgettext -j -d id -o i18n/id/LC_MESSAGES/riab.po \
		storage/test_io.py \
		impact_functions/flood/flood_building_impact.py

#Qt .qm file updates - run to create binary representation of translated strings for translation in gui
compile-translation-strings: compile
	cd gui; lrelease riab.pro; cd ..
	msgfmt -o i18n/id/LC_MESSAGES/riab.mo i18n/id/LC_MESSAGES/riab.po

clean:
	@# FIXME (Ole): Use normal Makefile rules instead
	@# Preceding dash means that make will continue in case of errors
	@# Swapping stdout & stderr and filter out low level QGIS garbage
	@# See http://stackoverflow.com/questions/3618078/pipe-only-stderr-through-a-filter
	@-find . -name '*~' -exec rm {} \;
	@-find . -name '*.pyc' -exec rm {} \;
	@-/bin/rm .noseids 2>/dev/null || true
	@-/bin/rm .coverage 2>/dev/null || true

# Run the test suite followed by pep8 style checking
test: test_suite pep8 disabled_tests dependency_test unwanted_strings

# Run the test suite for gui only
guitest: gui_test_suite pep8 disabled_tests dependency_test unwanted_strings

# Run pep8 style checking
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203 --exclude ui_riab.py,ui_riabdock.py,resources.py,resources_rc.py,ui_riabhelp.py . || true

# Run entire test suite
test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"
	@-export PYTHONPATH=`pwd`; nosetests -v --with-id --with-coverage --cover-package=storage,engine,impact_functions,gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

	@# FIXME (Ole) - to get of the remaining junk I tried to use
	@#  ...| awk 'BEGIN {FS="Object::"} {print $1}'
	@# This does clip the line, but does not flush and puts an extra
	@# newline in.

	@# Report expected failures if any!
	@#echo Expecting 1 test to fail in support of issue #3

# Run gui test suite only
gui_test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`; nosetests -v --with-id --with-coverage --cover-package=gui gui 3>&1 1>&2 2>&3 3>&- | grep -v "^Object::" || true

# Get test data
testdata:
	@echo
	@echo "-----------------------------------------------------------"
	@echo "Updating test data - please hit Enter if asked for password"
	@echo "-----------------------------------------------------------"
	@svn co http://www.aifdr.org/svn/riab_test_data ../riab_test_data

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

dependency_test:
	@echo
	@echo "---------------------------------------------"
	@echo "List of unwanted dependencies in RIAB library"
	@echo "---------------------------------------------"

	@# Need disjunction with "true" because grep returns non-zero error code if no matches were found
	@# nielso@shakti:~/sandpit/risk_in_a_box$ grep PyQt4 engine
	@# nielso@shakti:~/sandpit/risk_in_a_box$ echo $?
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
