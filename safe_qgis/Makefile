#/***************************************************************************
# IS
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

# Makefile for a PyQGIS plugin

# Note by Tim. I think we can get rid of py_files, and extras
PLUGINNAME = inasafe

PY_FILES = __init__.py \
					clipper.py \
					dock.py \
					exceptions.py\
					help.py \
					html_renderer.py \
					impact_calculator.py \
					impact_calculator_thread.py \
					impact_functions_doc.py \
					keyword_io.py \
					keywords_dialog.py \
					map_legend.py \
					map.py \
					options_dialog.py \
					plugin.py \
					qgis_interface.py \
					safe_interface.py \
					utilities.py

EXTRAS = icon.png

UI_FILES = dock_base.py \
					 options_dialog_base.py \
					 keywords_dialog_base.py \
					 impact_functions_doc_base.py \
					 options_dialog_base.py

RESOURCE_FILES = resources.py

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	pyrcc4 -o $@  $<
	@#this is ugly but the resource referenced by the ui
	@#looks for a file generated with a different name
	cp resources.py resources_rc.py

clean: compile
	rm $(UI_FILES)

%.py : %.ui
	pyuic4 -o $@ $<
