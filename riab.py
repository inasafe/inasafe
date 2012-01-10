"""
/***************************************************************************
 Riab
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

# Import the PyQt and QGIS libraries
# FIXME (Ole): I want to replace the import * form with import <name> to
# be more explicit about namespaces.
from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from riabdialog import RiabDialog


class Riab:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(':/plugins/riab/icon.png'), \
            'Risk In A Box', self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL('triggered()'), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&Risk In A Box', self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('&Risk In A Box', self.action)
        self.iface.removeToolBarIcon(self.action)

    # Run method that performs all the real work
    def run(self):

        # Create and show the dialog
        dlg = RiabDialog()

        # Show the dialog
        dlg.show()
        result = dlg.exec_()

        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
