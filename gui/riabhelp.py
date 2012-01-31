"""
Disaster risk assessment tool developed by AusAid - **Help Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import QtGui, QtCore
from ui_riabhelp import Ui_RiabHelp
import os


class RiabHelp(QtGui.QDialog):
    """Help dialog class for the Risk In A Box plugin."""

    def __init__(self, iface):
        """Constructor for the dialog.

        This dialog will show the user help documentation.

        Args:

           * iface - a Quantum GIS QGisAppInterface instance.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, None)
        # Save reference to the QGIS interface
        self.iface = iface
        # Set up the user interface from Designer.
        self.ui = Ui_RiabHelp()
        self.ui.setupUi(self)
        self.showHelp()

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        ROOT = os.path.dirname(__file__)
        myPath = os.path.abspath(os.path.join(ROOT, '..', 'docs', 'build',
                                            'html', 'README.html'))
        self.ui.webView.setUrl(QtCore.QUrl('file:///' + myPath))
