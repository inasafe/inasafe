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
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from safe_qgis.ui.options_dialog_base import Ui_OptionsDialogBase
from safe_qgis.help import Help
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.safe_interface import get_version
from safe_qgis.safe_interface import DEFAULTS


class OptionsDialog(QtGui.QDialog, Ui_OptionsDialogBase):
    """Options dialog for the InaSAFE plugin.
    """

    def __init__(self, parent, iface, theDock=None):
        """Constructor for the dialog.

        :param parent: Parent widget of this dialog
        :param iface: A Quantum GIS QGisAppInterface instance.
        :param theDock: Optional dock widget instance that we can notify of
            changes to the keywords.
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s Options' % get_version()))
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
        # hack prevent showing use thread visible and set it false see #557
        self.cbxUseThread.setChecked(True)
        self.cbxUseThread.setVisible(False)

    def restoreState(self):
        """Reinstate the options based on the user's stored session info.
        """
        mySettings = QtCore.QSettings()
        # myFlag = mySettings.value(
        #     'inasafe/useThreadingFlag', False).toBool()
        # hack set use thread to false see #557
        myFlag = False
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

        myFlag = mySettings.value(
            'inasafe/clipHard', False).toBool()
        self.cbxClipHard.setChecked(myFlag)

        myFlag = mySettings.value(
            'inasafe/useSentry', False).toBool()
        self.cbxUseSentry.setChecked(myFlag)

        myFlag = mySettings.value(
            'inasafe/showIntermediateLayers', False).toBool()
        self.cbxShowPostprocessingLayers.setChecked(myFlag)

        myRatio = mySettings.value(
            'inasafe/defaultFemaleRatio',
            DEFAULTS['FEM_RATIO']).toDouble()
        self.dsbFemaleRatioDefault.setValue(myRatio[0])

        myPath = mySettings.value(
            'inasafe/keywordCachePath',
            self.keywordIO.defaultKeywordDbPath()).toString()
        self.leKeywordCachePath.setText(myPath)

        myFlag = mySettings.value(
            'inasafe/devMode', False).toBool()
        self.cbxDevMode.setChecked(myFlag)

    def saveState(self):
        """Store the options into the user's stored session info.
        """
        mySettings = QtCore.QSettings()
        mySettings.setValue('inasafe/useThreadingFlag',
                            False)
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
        mySettings.setValue('inasafe/clipHard',
                            self.cbxClipHard.isChecked())
        mySettings.setValue('inasafe/useSentry',
                            self.cbxUseSentry.isChecked())
        mySettings.setValue('inasafe/showIntermediateLayers',
                            self.cbxShowPostprocessingLayers.isChecked())
        mySettings.setValue('inasafe/defaultFemaleRatio',
                            self.dsbFemaleRatioDefault.value())
        mySettings.setValue('inasafe/keywordCachePath',
                            self.leKeywordCachePath.text())
        mySettings.setValue('inasafe/devMode',
                            self.cbxDevMode.isChecked())

    def showHelp(self):
        """Load the help text for the options safe_qgis
        """
        if not self.helpDialog:
            self.helpDialog = Help(self.iface.mainWindow(), 'options')

    def accept(self):
        """Method invoked when OK button is clicked.
        """
        self.saveState()
        self.dock.readSettings()
        self.close()

    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolKeywordCachePath_clicked(self):
        """Auto-connect slot activated when the selected cache file tool button
        is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        myFilename = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Set keyword cache file'),
            self.keywordIO.defaultKeywordDbPath(),
            self.tr('Sqlite DB File (*.db)'))
        self.leKeywordCachePath.setText(myFilename)
