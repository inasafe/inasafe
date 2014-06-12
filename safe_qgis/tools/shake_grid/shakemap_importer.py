# coding=utf-8
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
__date__ = '08/5/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2013, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging
import os

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import QFileInfo, pyqtSignature
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialogButtonBox, QDialog, QFileDialog, QMessageBox
from qgis.core import QgsRasterLayer, QgsMapLayerRegistry

from safe_qgis.ui.shakemap_importer_base import Ui_ShakemapImporterBase
from safe_qgis.safe_interface import get_version
from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import styles
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.utilities import html_footer, html_header
from safe_qgis.utilities.styling import mmi_ramp
from safe_qgis.tools.shake_grid.shake_grid import convert_mmi_data


INFO_STYLE = styles.INFO_STYLE
LOGGER = logging.getLogger('InaSAFE')


class ShakemapImporter(QDialog, Ui_ShakemapImporterBase):
    """Importer for shakemap grid.xml files."""
    def __init__(self, parent=None):
        """Constructor for the dialog.

        Show the grid converter dialog.

        :param parent: parent - widget to use as parent.
        :type parent: QWidget

        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setWindowTitle(
            self.tr('InaSAFE %s Shakemap Converter' % get_version()))
        self.warning_text = set()
        self.on_input_path_textChanged()
        self.on_output_path_textChanged()
        self.update_warning()

        # Event register
        #noinspection PyUnresolvedReferences
        self.use_output_default.toggled.connect(
            self.get_output_from_input)
        #noinspection PyUnresolvedReferences
        self.input_path.textChanged.connect(self.on_input_path_textChanged)
        #noinspection PyUnresolvedReferences
        self.output_path.textChanged.connect(self.on_output_path_textChanged)
        # Set up things for context help
        help_button = self.button_box.button(QDialogButtonBox.Help)
        help_button.clicked.connect(ShakemapImporter.show_help)

        self.show_info()

    @staticmethod
    def show_help():
        """Show context help for the converter dialog."""
        show_context_help('converter')

    def show_info(self):
        """Show usage text to the user."""
        header = html_header()
        footer = html_footer()
        string = header

        heading = m.Heading(self.tr('Shakemap Grid Importer'), **INFO_STYLE)
        body = self.tr(
            'This tool will convert an earthquake \'shakemap\' that is in '
            'grid xml format to a GeoTIFF file. The imported file can be used '
            'in InaSAFE as an input for impact functions that require and '
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

    # noinspection PyPep8Naming
    def on_output_path_textChanged(self):
        """Action when output file name is changed.
        """
        output_path = str(self.output_path.text())
        output_not_xml_msg = str(self.tr('output file is not .tif'))
        if not output_path.endswith('.tif'):
            self.warning_text.add(output_not_xml_msg)
        elif output_not_xml_msg in self.warning_text:
            self.warning_text.remove(output_not_xml_msg)
        self.update_warning()

    #noinspection PyPep8Naming
    def on_input_path_textChanged(self):
        """Action when input file name is changed.
        """
        input_path = str(self.input_path.text())
        # input_not_exist_msg = str(self.tr('input file is not existed'))
        input_not_grid_msg = str(self.tr('input file is not .xml'))

        if not input_path.endswith('.xml'):
            self.warning_text.add(input_not_grid_msg)
        elif input_not_grid_msg in self.warning_text:
            self.warning_text.remove(input_not_grid_msg)

        if self.use_output_default.isChecked():
            self.get_output_from_input()
        self.update_warning()

    def update_warning(self):
        """Update warning message and enable/disable Ok button."""
        if len(self.warning_text) == 0:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            return

        header = html_header()
        footer = html_footer()
        string = header
        heading = m.Heading(self.tr('Shakemap Grid Importer'), **INFO_STYLE)
        tips = m.BulletedList()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        message = m.Message()
        message.add(heading)
        for warning in self.warning_text:
            tips.add(warning)

        message.add(tips)
        string += message.to_html()
        string += footer
        self.webView.setHtml(string)

    def get_output_from_input(self):
        """Create default output location based on input location.
        """
        input_path = str(self.input_path.text())
        if input_path.endswith('.xml'):
            output_path = input_path[:-3] + 'tif'
        elif input_path == '':
            output_path = ''
        else:
            last_dot = input_path.rfind('.')
            if last_dot == -1:
                output_path = ''
            else:
                output_path = input_path[:last_dot + 1] + 'tif'
        self.output_path.setText(output_path)

    def accept(self):
        """Handler for when OK is clicked.
        """
        input_path = str(self.input_path.text())
        input_title = str(self.line_edit_title.text())
        input_source = str(self.line_edit_source.text())
        output_path = str(self.output_path.text())
        if not output_path.endswith('.tif'):
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                (self.tr('Output file name must be tif file')))
        if not os.path.exists(input_path):
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                (self.tr('Input file is not exist')))
            return

        if self.nearest_mode.isChecked():
            algorithm = 'nearest'
        else:
            algorithm = 'invdist'

        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        file_name = convert_mmi_data(
            input_path,
            input_title,
            input_source,
            output_path,
            algorithm=algorithm,
            algorithm_filename_flag=False)

        QtGui.qApp.restoreOverrideCursor()

        if self.load_result.isChecked():
            file_info = QFileInfo(file_name)
            base_name = file_info.baseName()
            layer = QgsRasterLayer(file_name, base_name)
            # noinspection PyTypeChecker
            mmi_ramp(layer)
            layer.saveDefaultStyle()
            if not layer.isValid():
                LOGGER.debug("Failed to load")
            else:
                # noinspection PyArgumentList
                QgsMapLayerRegistry.instance().addMapLayers([layer])
        self.done(self.Accepted)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_open_input_tool_clicked(self):
        """Autoconnect slot activated when open input tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        filename = QFileDialog.getOpenFileName(
            self, self.tr('Input file'), 'grid.xml',
            self.tr('Raw grid file(*.xml)'))
        self.input_path.setText(filename)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_open_output_tool_clicked(self):
        """Autoconnect slot activated when open output tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        filename = QFileDialog.getSaveFileName(
            self, self.tr('Output file'), 'grid.tif',
            self.tr('Raster file(*.tif)'))
        self.output_path.setText(filename)
