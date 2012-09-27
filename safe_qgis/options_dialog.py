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
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from safe_qgis.options_dialog_base import Ui_OptionsDialogBase
from safe_qgis.help import Help
from safe_qgis.keyword_io import KeywordIO

# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import safe_qgis.resources  # pylint: disable=W0611

#see if we can import pydev - see development docs for details
try:
    from pydevd import *  # pylint: disable=F0401
    print 'Remote debugging is enabled.'
    DEBUG = True
except ImportError:
    print 'Debugging was disabled'


class OptionsDialog(QtGui.QDialog, Ui_OptionsDialogBase):
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
        self.keywordIO = KeywordIO()
        # Set up things for context help
        myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)
        self.grpNotImplemented.hide()
        self.adjustSize()
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

        myFlag = mySettings.value(
                            'inasafe/setLayerNameFromTitleFlag', True).toBool()
        self.cbxSetLayerNameFromTitle.setChecked(myFlag)

        myFlag = mySettings.value(
                            'inasafe/setZoomToImpactFlag', True).toBool()
        self.cbxZoomToImpact.setChecked(myFlag)
        # whether exposure layer should be hidden after model completes
        myFlag = mySettings.value(
                            'inasafe/setHideExposureFlag', False).toBool()
        self.cbxHideExposure.setChecked(myFlag)

        myFlag = mySettings.value(
            'inasafe/clipToViewport', True).toBool()
        self.cbxClipToViewport.setChecked(myFlag)

        myPath = mySettings.value(
                            'inasafe/keywordCachePath',
                            self.keywordIO.defaultKeywordDbPath()).toString()
        self.leKeywordCachePath.setText(myPath)

    def saveState(self):
        """
        Args: Store the options into the user's stored session info
            None
        Returns:
            None
        Raises:
        """
        mySettings = QtCore.QSettings()
        mySettings.setValue('inasafe/useThreadingFlag',
                            self.cbxUseThread.isChecked())
        mySettings.setValue('inasafe/visibleLayersOnlyFlag',
                            self.cbxVisibleLayersOnly.isChecked())
        mySettings.setValue('inasafe/setLayerNameFromTitleFlag',
                            self.cbxSetLayerNameFromTitle.isChecked())
        mySettings.setValue('inasafe/setZoomToImpactFlag',
                            self.cbxZoomToImpact.isChecked())
        mySettings.setValue('inasafe/setHideExposureFlag',
                            self.cbxHideExposure.isChecked())
        mySettings.setValue('inasafe/clipToViewport',
                            self.cbxClipToViewport.isChecked())
        mySettings.setValue('inasafe/keywordCachePath',
                            self.leKeywordCachePath.text())

    def showHelp(self):
        """Load the help text for the options safe_qgis"""
        if not self.helpDialog:
            self.helpDialog = Help(self.iface.mainWindow(), 'options')
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

    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolKeywordCachePath_clicked(self):
        """Autoconnect slot activated when the select cache file tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFilename = QtGui.QFileDialog.getSaveFileName(self,
                    self.tr('Set keyword cache file'),
                    self.keywordIO.defaultKeywordDbPath(),
                    self.tr('Sqlite DB File (*.db)'))
        self.leKeywordCachePath.setText(myFilename)
