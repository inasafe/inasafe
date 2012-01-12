"""
Disaster risk assessment tool developed by AusAid -
**QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon

# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from riabdialog import RiabDialog


class Riab:
    """The QGIS interface implementation for the Risk in a box plugin.

    This class acts as the 'glue' between QGIS and our custom logic.
    It creates a toolbar and menubar entry and launches the RIAB user
    interface if these are activated.
    """

    def __init__(self, iface):
        """Class constructor.

        On instantiation, the plugin instance will be assigned a copy
        of the QGIS iface object which will allow this plugin to access and
        manipulate the running QGIS instance that spawned it.

        Args:
           iface - a Quantum GIS QGisAppInterface instance. This instance
           is automatically passed to the plugin by QGIS when it loads the
           plugin.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        """Gui initialisation procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to set up
        any graphical user interface elements that should appear in QGIS by
        default (i.e. before the user performs any explicit action with the
        plugin).

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(':/plugins/riab/icon.png'), \
            'Risk In A Box', self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL('triggered()'), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&Risk In A Box', self.action)

    def unload(self):
        """Gui breakdown procedure (for QGIS plugin api).

        This method is called by QGIS and should be used to *remove*
        any graphical user interface elements that should appear in QGIS.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('&Risk In A Box', self.action)
        self.iface.removeToolBarIcon(self.action)

    # Run method that performs all the real work
    def run(self):
        """Gui run procedure.

        This slot is called when the user clicks the toolbar icon or
        menu item associated with this plugin.

        .. see also:: :func:`Riab.initGui`.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        # Create and show the dialog
        dlg = RiabDialog(self.iface)

        # Show the dialog
        dlg.show()
        result = dlg.exec_()

        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
