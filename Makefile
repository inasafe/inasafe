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

# Run the test suite followed by pep8 style checking
test: test_suite pep8

# Run pep8 style checking only
pep8: compile
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	pep8 --repeat --ignore=E203 --exclude ui_riab.py,ui_riabdock.py,resources.py,resources_rc.py,ui_riabhelp.py .

# Run test suite only
test_suite: compile testdata
	@echo "----------------------"
	@echo "Regresssion Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	-nosetests -v --with-id --with-coverage --cover-package=.,engine,storage,impact_functions

# Get test data
testdata:
	@echo "Updating test data - please hit Enter if asked for password"
	svn co http://www.aifdr.org/svn/riab_test_data --username anonymous