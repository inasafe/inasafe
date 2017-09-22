# coding=utf-8
"""A dialog for converting grid.xml file."""

import logging
import os

from qgis.core import QgsRasterLayer, QgsMapLayerRegistry
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import QFileInfo, pyqtSignature, pyqtSlot
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialogButtonBox, QDialog, QFileDialog, QMessageBox
from qgis.utils import iface

from safe.common.version import get_version
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.styling import mmi_ramp_roman
from safe.utilities.resources import html_footer, html_header, get_ui_class
from safe.gui.tools.shake_grid.shake_grid import convert_mmi_data
from safe.gui.tools.wizard.wizard_dialog import WizardDialog
from safe.gui.tools.help.shakemap_converter_help import shakemap_converter_help
from safe.gis.raster.reclassify import reclassify
from safe.utilities.keyword_io import KeywordIO
from safe.definitions.hazard_classifications import earthquake_mmi_scale


INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('shakemap_importer_dialog_base.ui')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ShakemapConverterDialog(QDialog, FORM_CLASS):

    """Importer for shakemap grid.xml files."""

    def __init__(self, parent=None, iface=None, dock_widget=None):
        """Constructor for the dialog.

        Show the grid converter dialog.

        :param parent: parent - widget to use as parent.
        :type parent: QWidget

        :param iface: QGIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param dock_widget: Dock widget instance.
        :type dock_widget: Dock
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.iface = iface
        self.dock_widget = dock_widget
        self.setupUi(self)
        self.setWindowTitle(
            self.tr('InaSAFE %s Shakemap Converter' % get_version()))
        self.warning_text = set()
        self.on_input_path_textChanged()
        self.on_output_path_textChanged()
        self.update_warning()
        self.output_layer = None

        # Event register
        # noinspection PyUnresolvedReferences
        self.use_output_default.toggled.connect(
            self.get_output_from_input)
        # noinspection PyUnresolvedReferences
        self.input_path.textChanged.connect(self.on_input_path_textChanged)
        # noinspection PyUnresolvedReferences
        self.output_path.textChanged.connect(self.on_output_path_textChanged)
        self.load_result.clicked.connect(self.load_result_toggled)

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)
        self.update_warning()

    # noinspection PyPep8Naming
    def on_output_path_textChanged(self):
        """Action when output file name is changed."""
        output_path = self.output_path.text()
        output_not_xml_msg = self.tr('output file is not .tif')
        if output_path and not output_path.endswith('.tif'):
            self.warning_text.add(output_not_xml_msg)
        elif output_path and output_not_xml_msg in self.warning_text:
            self.warning_text.remove(output_not_xml_msg)
        self.update_warning()

    # noinspection PyPep8Naming
    def on_input_path_textChanged(self):
        """Action when input file name is changed."""
        input_path = self.input_path.text()
        input_not_grid_msg = self.tr('input file is not .xml')

        if input_path and not input_path.endswith('.xml'):
            self.warning_text.add(input_not_grid_msg)
        elif input_path and input_not_grid_msg in self.warning_text:
            self.warning_text.remove(input_not_grid_msg)

        if self.use_output_default.isChecked():
            self.get_output_from_input()
        self.update_warning()

    def update_warning(self):
        """Update warning message and enable/disable Ok button."""
        if len(self.warning_text) == 0:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        header = html_header()
        footer = html_footer()
        string = header
        heading = m.Heading(self.tr('Shakemap Grid Importer'), **INFO_STYLE)
        tips = m.BulletedList()
        message = m.Message()
        message.add(heading)
        for warning in self.warning_text:
            tips.add(warning)

        message.add(tips)
        string += message.to_html()
        string += footer
        self.info_web_view.setHtml(string)

    def get_output_from_input(self):
        """Create default output location based on input location."""
        input_path = self.input_path.text()
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
        """Handler for when OK is clicked."""
        input_path = self.input_path.text()
        input_title = self.line_edit_title.text()
        input_source = self.line_edit_source.text()
        output_path = self.output_path.text()
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
                (self.tr('Input file does not exist')))
            return

        if self.nearest_mode.isChecked():
            algorithm = 'nearest'
        else:
            algorithm = 'invdist'

        # noinspection PyUnresolvedReferences
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        file_name = convert_mmi_data(
            input_path,
            input_title,
            input_source,
            output_path,
            algorithm=algorithm,
            algorithm_filename_flag=True)

        # reclassify raster
        file_info = QFileInfo(file_name)
        base_name = file_info.baseName()
        self.output_layer = QgsRasterLayer(file_name, base_name)
        self.output_layer.keywords = KeywordIO.read_keywords(self.output_layer)
        self.output_layer.keywords['classification'] = (
            earthquake_mmi_scale['key'])
        keywords = self.output_layer.keywords
        if self.output_layer.isValid():
            self.output_layer = reclassify(
                self.output_layer, overwrite_input=True)
            KeywordIO.write_keywords(self.output_layer, keywords)
        else:
            LOGGER.debug("Failed to load")

        # noinspection PyUnresolvedReferences
        QtGui.qApp.restoreOverrideCursor()

        if self.load_result.isChecked():
            # noinspection PyTypeChecker
            mmi_ramp_roman(self.output_layer)
            self.output_layer.saveDefaultStyle()
            if not self.output_layer.isValid():
                LOGGER.debug("Failed to load")
            else:
                # noinspection PyArgumentList
                QgsMapLayerRegistry.instance().addMapLayer(self.output_layer)
                iface.zoomToActiveLayer()

        if (self.keyword_wizard_checkbox.isChecked() and
                self.keyword_wizard_checkbox.isEnabled()):
            self.launch_keyword_wizard()

        self.done(self.Accepted)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_open_input_tool_clicked(self):
        """Autoconnect slot activated when open input tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        filename = QFileDialog.getOpenFileName(
            self, self.tr('Input file'), 'grid.xml',
            self.tr('Raw grid file (*.xml)'))
        self.input_path.setText(filename)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_open_output_tool_clicked(self):
        """Autoconnect slot activated when open output tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        filename = QFileDialog.getSaveFileName(
            self, self.tr('Output file'), 'grid.tif',
            self.tr('Raster file (*.tif)'))
        self.output_path.setText(filename)

    def load_result_toggled(self):
        """Function that perform action when load_result checkbox is clicked.
        """
        self.keyword_wizard_checkbox.setEnabled(self.load_result.isChecked())

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.2.1

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user.

        .. versionadded: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = shakemap_converter_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def launch_keyword_wizard(self):
        """Launch keyword creation wizard."""
        # make sure selected layer is the output layer
        if self.iface.activeLayer() != self.output_layer:
            return

        # launch wizard dialog
        keyword_wizard = WizardDialog(
            self.iface.mainWindow(), self.iface, self.dock_widget)
        keyword_wizard.set_keywords_creation_mode(self.output_layer)
        keyword_wizard.exec_()  # modal
