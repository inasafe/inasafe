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

# Makefile for a PyQGIS plugin
default: compile

compile:
	make -C gui

docs: compile
	cd docs; make html; cd ..

clean:
	@# FIXME (Ole): Use normal Makefile rules instead
	@find . -name '*~' -exec rm {} \;
	@find . -name '*.pyc' -exec rm {} \;

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
	@pep8 --repeat --ignore=E203 --exclude ui_riab.py,ui_riabdock.py,resources.py,resources_rc.py,ui_riabhelp.py .

# Run entire test suite
test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`; nosetests -v --with-id --with-coverage --cover-package=engine,storage,gui,impact_functions || true

# Run gui test suite only
gui_test_suite: compile testdata
	@echo
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:/usr/local/share/qgis/python/; export QGISPATH=/usr/local; nosetests -v --with-id --with-coverage --cover-package=gui gui

# Get test data
testdata:
	@echo
	@echo "-----------------------------------------------------------"
	@echo "Updating test data - please hit Enter if asked for password"
	@echo "-----------------------------------------------------------"
	@svn co http://www.aifdr.org/svn/riab_test_data

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

	@# FIXME (Ole): Have variable containing modules to check
	@grep -R PyQt4 storage engine impact_functions || true
	@grep -R qgis.core storage engine impact_functions || true
	@grep -R "import scipy" storage engine impact_functions || true
	@grep -R "from scipy import" storage engine impact_functions || true

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
