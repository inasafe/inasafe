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

##################### EDITABLE AREA starts ##################################
# List of ui files and rc files here that should be compiled to py files.
#############################################################################

UI_FILES = \
	about_dialog_base.ui \
	batch_dialog_base.ui \
	dock_base.ui \
	function_options_dialog_base.ui \
	impact_merge_dialog_base.ui \
	keywords_dialog_base.ui	\
	minimum_needs_base.ui \
	options_dialog_base.ui \
	osm_downloader_base.ui \
	shakemap_importer_base.ui \
    function_browser_base.ui \
    wizard_dialog_base.ui

###################### EDITABLE AREA ENDS ###################################

COMPILED_UI = $(UI_FILES:%.ui=%.py)

default : ui

clean:
	rm $(COMPILED_UI)
	rm *.pyc

ui: $(COMPILED_UI)

# Conversion rules

%.py : %.ui
	pyuic4 -o $@ $<
