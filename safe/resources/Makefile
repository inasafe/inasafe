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

RESOURCE_FILES = resources.qrc

###################### EDITABLE AREA ENDS ###################################

COMPILED_RESOURCES = $(RESOURCE_FILES:%.qrc=%_rc.py)

default : resources

clean:
	# rm $(COMPILED_RESOURCES)
	rm ../ui/resources_rc.py
	rm ../ui/resources_rc.pyc
	rm *.pyc

resources: $(COMPILED_RESOURCES)
	mv resources_rc.py ../ui

# Conversion rules

%_rc.py : %.qrc
	pyrcc4 -o $@ $<

