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


default: compile

compile:
	@echo
	@echo "------------------------------"
	@echo "Compile ui and resources forms"
	@echo "------------------------------"
	make -C ui
	make -C resources


clean:
	@echo
	@echo "------------------------------"
	@echo "Clean ui and resources forms"
	@echo "------------------------------"
	make clean -C ui
	make clean -C resources
