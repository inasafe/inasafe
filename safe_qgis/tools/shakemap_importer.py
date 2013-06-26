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
import os

from PyQt4.QtCore import (QFileInfo, pyqtSignature, SIGNAL, QObject)
from PyQt4.QtGui import QDialogButtonBox, QDialog, QFileDialog, QMessageBox
from qgis.core import (QgsRasterLayer, QgsMapLayerRegistry)

from safe_qgis.ui.shakemap_importer_base import Ui_ShakemapImporterBase
from safe_qgis.safe_interface import get_version, convert_mmi_data
from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import styles
from safe_qgis.utilities.utilities import htmlFooter, htmlHeader


INFO_STYLE = styles.INFO_STYLE
LOGGER = logging.getLogger('InaSAFE')


class ShakemapImporter(QDialog, Ui_ShakemapImporterBase):
    """Importer for shakemap grid.xml files.
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

        self.warning_text = set()
        self.on_leInputPath_textChanged()
        self.on_leOutputPath_textChanged()
        self.update_warning()

        # Event register
        QObject.connect(self.cBDefaultOutputLocation,
                        SIGNAL('toggled(bool)'),
                        self.get_output_from_input)
        QObject.connect(self.leInputPath,
                        SIGNAL('textChanged(QString)'),
                        self.on_leInputPath_textChanged)
        QObject.connect(self.leOutputPath,
                        SIGNAL('textChanged(QString)'),
                        self.on_leOutputPath_textChanged)

        self.showInfo()

    def showInfo(self):
        """Read the header and footer html snippets.
        """
        header = htmlHeader()
        footer = htmlFooter()
        string = header

        heading = m.Heading(self.tr('Shakemap Grid Importer'), **INFO_STYLE)
        body = self.tr(
            'This tool will convert an earthquake \'shakemap\' that is in '
            'grid xml format to a GeoTIFF file. The imported file can be used'
            'in InaSAFE as an input for inpact functions that require and '
            'earthquake layer.  To use this tool effectively:'
        )
        tips = m.BulletedList()
        tips.add(self.tr(
            'Select a grid.xml for the input layer.'))
        tips.add(self.tr(
            'Choose where to write the output layer to.'
        ))
        tips.add(self.tr(
            'Choose the interpolation algorithm that should be used when '
            'converting the xml grid to a raster. If unsure keep the default.'
        ))
        tips.add(self.tr(
            'If you want to obtain shake data you can get it for free from '
            'the USGS shakemap site: '
            'http://earthquake.usgs.gov/earthquakes/shakemap/list.php?y=2013'))
        message = m.Message()
        message.add(heading)
        message.add(body)
        message.add(tips)
        string += message.to_html()
        string += footer

        self.webView.setHtml(string)

    def on_leOutputPath_textChanged(self):
        """Action when output file name is changed
        """
        output_path = str(self.leOutputPath.text())
        output_not_xml_msg = str(self.tr('output file is not .tif'))
        if not output_path.endswith('.tif'):
            self.warning_text.add(output_not_xml_msg)
        elif output_not_xml_msg in self.warning_text:
            self.warning_text.remove(output_not_xml_msg)
        self.update_warning()

    def on_leInputPath_textChanged(self):
        """Action when input file name is changed
        """
        input_path = str(self.leInputPath.text())
        # input_not_exist_msg = str(self.tr('input file is not existed'))
        input_not_grid_msg = str(self.tr('input file is not .xml'))

        if not input_path.endswith('.xml'):
            self.warning_text.add(input_not_grid_msg)
        elif input_not_grid_msg in self.warning_text:
            self.warning_text.remove(input_not_grid_msg)

        if self.cBDefaultOutputLocation.isChecked():
            self.get_output_from_input()
        self.update_warning()

    def update_warning(self):
        """Update warning message and enable/disable Ok button
        """
        if len(self.warning_text) == 0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            return

        header = htmlHeader()
        footer = htmlFooter()
        string = header
        heading = m.Heading(self.tr('Shakemap Grid Importer'), **INFO_STYLE)
        tips = m.BulletedList()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        message = m.Message()
        message.add(heading)
        for warning in self.warning_text:
            tips.add(warning)

        message.add(tips)
        string += message.to_html()
        string += footer
        self.webView.setHtml(string)

    def get_output_from_input(self):
        """Basically, it just get from input file location and
        create default output location for it
        """
        my_input_path = str(self.leInputPath.text())
        if my_input_path.endswith('.xml'):
            my_output_path = my_input_path[:-3] + 'tif'
        elif my_input_path == '':
            my_output_path = ''
        else:
            last_dot = my_input_path.rfind('.')
            if last_dot == -1:
                my_output_path = ''
            else:
                my_output_path = my_input_path[:last_dot + 1] + 'tif'
        self.leOutputPath.setText(my_output_path)

    def accept(self):
        input_path = str(self.leInputPath.text())
        output_path = str(self.leOutputPath.text())
        if not output_path.endswith('.tif'):
            QMessageBox.warning(
                self.parent, self.tr('InaSAFE'),
                (self.tr('Output file name must be tif file')))
        if not os.path.exists(input_path):
            QMessageBox.warning(
                self.parent, self.tr('InaSAFE'),
                (self.tr('Input file is not exist')))
            return
        if self.radNearest.isChecked():
            my_algorithm = 'nearest'
        else:
            my_algorithm = 'invdist'

        fileName = convert_mmi_data(input_path, output_path,
                                    the_algorithm=my_algorithm,
                                    algorithm_name=False)
        if self.cBLoadLayer.isChecked():
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            layer = QgsRasterLayer(fileName, baseName)
            layer.setGrayBandName(layer.bandName(1))
            layer.setDrawingStyle(QgsRasterLayer.SingleBandPseudoColor)
            layer.setColorShadingAlgorithm(QgsRasterLayer.PseudoColorShader)
            layer.saveDefaultStyle()
            if not layer.isValid():
                LOGGER.debug("Failed to load")
            else:
                QgsMapLayerRegistry.instance().addMapLayer(layer)
        self.done(self.Accepted)

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
