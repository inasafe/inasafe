# coding=utf-8
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
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.safe_interface import get_version
from safe_qgis.safe_interface import DEFAULTS


class OptionsDialog(QtGui.QDialog, Ui_OptionsDialogBase):
    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, dock=None, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s Options' % get_version()))
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.keywordIO = KeywordIO()
        # Set up things for context help
        myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        myButton.clicked.connect(self.show_help)
        self.grpNotImplemented.hide()
        self.adjustSize()
        self.restore_state()
        # hack prevent showing use thread visible and set it false see #557
        self.cbxUseThread.setChecked(True)
        self.cbxUseThread.setVisible(False)

    def restore_state(self):
        """Reinstate the options based on the user's stored session info.
        """
        mySettings = QtCore.QSettings()
        # myFlag = mySettings.value(
        #     'inasafe/useThreadingFlag', False)
        # hack set use thread to false see #557
        myFlag = False
        self.cbxUseThread.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/visibleLayersOnlyFlag', True))
        self.cbxVisibleLayersOnly.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/setLayerNameFromTitleFlag', True))
        self.cbxSetLayerNameFromTitle.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/setZoomToImpactFlag', True))
        self.cbxZoomToImpact.setChecked(myFlag)
        # whether exposure layer should be hidden after model completes
        myFlag = bool(mySettings.value(
            'inasafe/setHideExposureFlag', False))
        self.cbxHideExposure.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/clipToViewport', True))
        self.cbxClipToViewport.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/clipHard', False))
        self.cbxClipHard.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/useSentry', False))
        self.cbxUseSentry.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/showIntermediateLayers', False))
        self.cbxShowPostprocessingLayers.setChecked(myFlag)

        myRatio = float(mySettings.value(
            'inasafe/defaultFemaleRatio',
            DEFAULTS['FEM_RATIO']))
        self.dsbFemaleRatioDefault.setValue(myRatio)

        myPath = mySettings.value(
            'inasafe/keywordCachePath',
            self.keywordIO.default_keyword_db_path())
        self.leKeywordCachePath.setText(myPath)

        myFlag = bool(mySettings.value(
            'inasafe/devMode', False))
        self.cbxDevMode.setChecked(myFlag)

        myFlag = bool(mySettings.value(
            'inasafe/useNativeZonalStats', False))
        self.cbxNativeZonalStats.setChecked(myFlag)

    def save_state(self):
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
        mySettings.setValue('inasafe/useNativeZonalStats',
                            self.cbxNativeZonalStats.isChecked())

    def show_help(self):
        """Show context help for the options dialog."""
        show_context_help('options')

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        self.dock.read_settings()
        self.close()

    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolKeywordCachePath_clicked(self):
        """Auto-connect slot activated when cache file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        myFilename = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Set keyword cache file'),
            self.keywordIO.default_keyword_db_path(),
            self.tr('Sqlite DB File (*.db)'))
        self.leKeywordCachePath.setText(myFilename)
