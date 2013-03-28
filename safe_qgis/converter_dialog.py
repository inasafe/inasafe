"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Converter Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '12/2/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2013, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from PyQt4.QtCore import (QFileInfo, pyqtSignature, SIGNAL, QObject)
from PyQt4.QtGui import QDialogButtonBox, QDialog, QFileDialog, QMessageBox

from converter_dialog_base import Ui_ConverterDialogBase
from qgis.core import (QgsRasterLayer, QgsMapLayerRegistry)
from safe_qgis.safe_interface import get_version, convert_mmi_data

LOGGER = logging.getLogger('InaSAFE')


class ConverterDialog(QDialog, Ui_ConverterDialogBase):
    """Converter Dialog for InaSAFE
    """
    def __init__(self, theParent=None):
        """Constructor for the dialog.

                This dialog will show the user converter dialog

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QDialog.__init__(self, theParent)
        self.parent = theParent
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %1 Converter').arg(
            get_version()))
        # I'm too lazy to put a text :)
        self.leInputPath.setText('/home/sunnii/Downloads/grid.xml')
        self.list_algorithm = ['Nearest', 'Invdist']
        self.test_mode = False
        self.populate_algorithm()
        # Event register
        QObject.connect(self.cBDefaultOutputLocation,
                        SIGNAL('toggled(bool)'),
                        self.update_output_location)
        QObject.connect(self.leInputPath,
                        SIGNAL('textChanged(QString)'),
                        self.update_output_location)
        QObject.connect(self.leOutputPath,
                        SIGNAL('textChanged(QString)'),
                        self.on_leOutputPath_textChanged)

    def populate_algorithm(self):
        """Populate algorithm for converting grid.xml
        """
        self.cboAlgorithm.addItems(self.list_algorithm)

    def on_leOutputPath_textChanged(self):
        """Action when output file name is changed
        """
        output_path = str(self.leOutputPath.text())
        if not output_path.endswith('.tif'):
            self.lblWarning.setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.lblWarning.setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def update_output_location(self):
        """Update output location if cBDefaultOutputLocation
        is toggled.
        """
        if self.cBDefaultOutputLocation.isChecked():
            self.get_output_from_input()

    def get_output_from_input(self):
        """Basically, it just get from input file location and
        create default output location for it
        """
        my_input_path = str(self.leInputPath.text())
        if my_input_path.endswith('.xml'):
            my_output_path = my_input_path[:-3] + 'tif'
        else:
            last_dot = my_input_path.rfind('.')
            my_output_path = my_input_path[:last_dot + 1] + 'tif'
        self.leOutputPath.setText(my_output_path)

    def on_leInputPath_textChanged(self):
        """Event handler when leInputPath changed its text
        """
        if self.cBDefaultOutputLocation.isChecked():
            self.get_output_from_input()

    def accept(self):
        input_path = str(self.leInputPath.text())
        output_path = str(self.leOutputPath.text())
        if not output_path.endswith('.tif'):
            QMessageBox.warning(
                self.parent, self.tr('InaSAFE'),
                (self.tr('Output file name must be tif file')))
        my_algorithm = str(self.cboAlgorithm.currentText()).lower()
        fileName = convert_mmi_data(input_path, output_path,
                                    the_algorithm=my_algorithm,
                                    algorithm_name=False)
        if self.cBLoadLayer.isChecked():
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            my_raster_layer = QgsRasterLayer(fileName, baseName)
            if not my_raster_layer.isValid():
                LOGGER.debug("Failed to load")
            else:
                QgsMapLayerRegistry.instance().addMapLayer(my_raster_layer)
        self.done(self.Accepted)
        if not self.test_mode:
            QMessageBox.warning(
                self.parent, self.tr('InaSAFE'),
                (self.tr('Success to convert %1 to %2').
                 arg(input_path).arg(output_path)))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tBtnOpenInput_clicked(self):
        """Autoconnect slot activated when the open input tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFilename = QFileDialog.getOpenFileName(
            self, self.tr('Input file'), 'grid.xml',
            self.tr('Raw grid file(*.xml)'))
        self.leInputPath.setText(myFilename)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tBtnOpenOutput_clicked(self):
        """Autoconnect slot activated when the open output tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFilename = QFileDialog.getSaveFileName(
            self, self.tr('Ouput file'), 'ismailsunni.tif',
            self.tr('Raster file(*.tif)'))
        self.leOutputPath.setText(myFilename)
