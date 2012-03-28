"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Options Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.3.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from is_options_dialog_base import Ui_ISOptionsDialogBase
from is_help import ISHelp
from is_utilities import getExceptionWithStacktrace

# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources

#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class ISOptionsDialog(QtGui.QDialog, Ui_ISOptionsDialogBase):
    """Options dialog for the InaSAFE plugin."""
    def __init__(self, parent, iface, theDock=None):
        """Constructor for the dialog.

        Args:
           * parent - parent widget of this dialog
           * iface - a Quantum GIS QGisAppInterface instance.
           * theDock - Optional dock widget instance that we can notify of
             changes to the keywords.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s Options' % __version__))
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = theDock
        self.helpDialog = None
        # Set up things for context help
        myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)
        self.restoreState()

    def restoreState(self):
        """
        Args: Reinstate the options based on the user's stored session info
            None
        Returns:
            None
        Raises:
        """
        mySettings = QtCore.QSettings()
        myFlag = mySettings.value(
                            'inasafe/useThreadingFlag', False).toBool()
        self.cbxUseThread.setChecked(myFlag)
        myFlag = mySettings.value(
                            'inasafe/visibleLayersOnlyFlag', True).toBool()
        self.cbxVisibleLayersOnly.setChecked(myFlag)

    def saveState(self):
        """
        Args: Store the options into the user's stored session info
            None
        Returns:
            None
        Raises:
        """
        mySettings = QtCore.QSettings()
        myFlag = mySettings.setValue(
                            'inasafe/useThreadingFlag',
                            self.cbxUseThread.isChecked())
        myFlag = mySettings.setValue(
                            'inasafe/visibleLayersOnlyFlag',
                            self.cbxVisibleLayersOnly.isChecked())

    def showHelp(self):
        """Load the help text for the options gui"""
        if not self.helpDialog:
            self.helpDialog = ISHelp(self.iface.mainWindow(), 'options')
        self.helpDialog.show()

    def accept(self):
        """Method invoked when ok button is clicked
        Args:
            None
        Returns:
            None
        Raises:
        """
        self.saveState()
        self.dock.readSettings()
        self.close()
