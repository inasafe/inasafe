"""
/***************************************************************************
 RiabDialog
                                 A QGIS plugin
 Disaster risk assessment tool developed by AusAid
                             -------------------
        begin                : 2012-01-09
        copyright            : (C) 2012 by Australia Indonesia Facility for
                                           Disaster Reduction
        email                : ole.moller.nielsen@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_riab import Ui_Riab


# Create the dialog for zoom to point
class RiabDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_Riab()
        self.ui.setupUi(self)
