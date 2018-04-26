# coding=utf-8
"""A dialog for converting grid.xml file."""

import logging
import os

from qgis.core import (QgsApplication, QgsProject, QgsRasterLayer,
                       QgsVectorLayer)
# noinspection PyPackageRequirements
from qgis.PyQt import QtCore, QtGui
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QFileInfo, pyqtSlot
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import (QDialog, QDialogButtonBox, QFileDialog,
                                 QMessageBox)
from qgis.utils import iface
from safe import messaging as m
from safe.common.version import get_version
from safe.definitions.constants import (NONE_SMOOTHING, NUMPY_SMOOTHING,
                                        SCIPY_SMOOTHING)
from safe.definitions.extra_keywords import (extra_keyword_earthquake_event_id,
                                             extra_keyword_earthquake_source)
from safe.gui.tools.help.shakemap_converter_help import shakemap_converter_help
from safe.gui.tools.shake_grid.shake_grid import convert_mmi_data
from safe.gui.tools.wizard.wizard_dialog import WizardDialog
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import (get_ui_class, html_footer, html_header,
                                      resources_path)
from safe.utilities.settings import setting
from safe.utilities.styling import mmi_ramp_roman

try:
    import scipy  # NOQA
    from scipy.ndimage.filters import gaussian_filter  # NOQA
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

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

        :param iface: QGIS QgisAppInterface instance.
        :type iface: QgisAppInterface

        :param dock_widget: Dock widget instance.
        :type dock_widget: Dock
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.iface = iface
        self.dock_widget = dock_widget
        self.setupUi(self)
        self.setWindowTitle(
            tr('InaSAFE %s Shakemap Converter' % get_version()))
        icon = resources_path('img', 'icons', 'show-converter-tool.svg')
        self.setWindowIcon(QtGui.QIcon(icon))
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
        self.help_button = self.button_box.button(QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)
        self.check_box_custom_shakemap_id.toggled.connect(
            self.line_edit_shakemap_id.setEnabled)

        # Set value for EQ source type combo box
        self.combo_box_source_type.addItem(tr('N/A'), '')
        for source_type in extra_keyword_earthquake_source['options']:
            self.combo_box_source_type.addItem(
                source_type['name'], source_type['key'])
        self.combo_box_source_type.setCurrentIndex(0)

        self.update_warning()

        if not setting('developer_mode', expected_type=bool):
            self.smoothing_group_box.hide()

        self.use_ascii_mode.setToolTip(tr(
            'This algorithm will convert the grid xml to a ascii raster file. '
            'If the cell width and height is different, it will use the width '
            '(length cell in x axis).'))

        if not HAS_SCIPY:
            if self.scipy_smoothing.isChecked:
                self.none_smoothing.setChecked(True)
            self.scipy_smoothing.setToolTip(tr(
                'You can not use select this option since you do not have '
                'scipy installed in you system.'))
            self.scipy_smoothing.setEnabled(False)
        else:
            self.scipy_smoothing.setEnabled(True)
            self.scipy_smoothing.setToolTip('')

    # noinspection PyPep8Naming
    def on_output_path_textChanged(self):
        """Action when output file name is changed."""
        output_path = self.output_path.text()
        output_not_xml_msg = tr('output file is not .tif')
        if output_path and not output_path.endswith('.tif'):
            self.warning_text.add(output_not_xml_msg)
        elif output_path and output_not_xml_msg in self.warning_text:
            self.warning_text.remove(output_not_xml_msg)
        self.update_warning()

    # noinspection PyPep8Naming
    def on_input_path_textChanged(self):
        """Action when input file name is changed."""
        input_path = self.input_path.text()
        input_not_grid_msg = tr('input file is not .xml')

        if input_path and not input_path.endswith('.xml'):
            self.warning_text.add(input_not_grid_msg)
        elif input_path and input_not_grid_msg in self.warning_text:
            self.warning_text.remove(input_not_grid_msg)

        if self.use_output_default.isChecked():
            self.get_output_from_input()
        self.update_warning()

    # noinspection PyPep8Naming
    def prepare_place_layer(self):
        """Action when input place layer name is changed."""
        if os.path.exists(self.input_place.text()):
            self.place_layer = QgsVectorLayer(
                self.input_place.text(),
                tr('Nearby Cities'),
                'ogr'
            )
            if self.place_layer.isValid():
                LOGGER.debug('Get field information')
                self.name_field.setLayer(self.place_layer)
                self.population_field.setLayer(self.place_layer)
            else:
                LOGGER.debug('failed to set name field')

    def update_warning(self):
        """Update warning message and enable/disable Ok button."""
        if len(self.warning_text) == 0:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        header = html_header()
        footer = html_footer()
        string = header
        heading = m.Heading(tr('Shakemap Grid Importer'), **INFO_STYLE)
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
                tr('InaSAFE'),
                tr('Output file name must be tif file'))
        if not os.path.exists(input_path):
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QMessageBox.warning(
                self,
                tr('InaSAFE'),
                tr('Input file does not exist'))
            return

        algorithm = 'nearest'
        if self.nearest_mode.isChecked():
            algorithm = 'nearest'
        elif self.inverse_distance_mode.isChecked():
            algorithm = 'invdist'
        elif self.use_ascii_mode.isChecked():
            algorithm = 'use_ascii'

        # Smoothing
        smoothing_method = NONE_SMOOTHING
        if self.numpy_smoothing.isChecked():
            smoothing_method = NUMPY_SMOOTHING
        if self.scipy_smoothing.isChecked():
            smoothing_method = SCIPY_SMOOTHING

        # noinspection PyUnresolvedReferences
        QgsApplication.instance().setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        extra_keywords = {}
        if self.check_box_custom_shakemap_id.isChecked():
            event_id = self.line_edit_shakemap_id.text()
            extra_keywords[extra_keyword_earthquake_event_id['key']] = event_id

        current_index = self.combo_box_source_type.currentIndex()
        source_type = self.combo_box_source_type.itemData(current_index)
        if source_type:
            extra_keywords[
                extra_keyword_earthquake_source['key']] = source_type

        file_name = convert_mmi_data(
            input_path,
            input_title,
            input_source,
            output_path,
            algorithm=algorithm,
            algorithm_filename_flag=True,
            smoothing_method=smoothing_method,
            extra_keywords=extra_keywords
        )

        file_info = QFileInfo(file_name)
        base_name = file_info.baseName()
        self.output_layer = QgsRasterLayer(file_name, base_name)

        # noinspection PyUnresolvedReferences
        QgsApplication.instance().restoreOverrideCursor()

        if self.load_result.isChecked():
            # noinspection PyTypeChecker
            mmi_ramp_roman(self.output_layer)
            self.output_layer.saveDefaultStyle()
            if not self.output_layer.isValid():
                LOGGER.debug("Failed to load")
            else:
                # noinspection PyArgumentList
                QgsProject.instance().addMapLayer(self.output_layer)
                iface.zoomToActiveLayer()

        if (self.keyword_wizard_checkbox.isChecked() and
                self.keyword_wizard_checkbox.isEnabled()):
            self.launch_keyword_wizard()

        self.done(self.Accepted)

    @pyqtSlot()  # prevents actions being handled twice
    def on_open_input_tool_clicked(self):
        """Autoconnect slot activated when open input tool button is clicked.
        """
        input_path = self.input_path.text()
        if not input_path:
            input_path = os.path.expanduser('~')
        # noinspection PyCallByClass,PyTypeChecker
        filename, __ = QFileDialog.getOpenFileName(
            self, tr('Input file'), input_path, tr('Raw grid file (*.xml)'))
        if filename:
            self.input_path.setText(filename)

    @pyqtSlot()  # prevents actions being handled twice
    def on_open_output_tool_clicked(self):
        """Autoconnect slot activated when open output tool button is clicked.
        """
        output_path = self.output_path.text()
        if not output_path:
            output_path = os.path.expanduser('~')
        # noinspection PyCallByClass,PyTypeChecker
        filename, __ = QFileDialog.getSaveFileName(
            self, tr('Output file'), output_path, tr('Raster file (*.tif)'))
        if filename:
            self.output_path.setText(filename)

    @pyqtSlot()
    def on_open_place_tool_clicked(self):
        input_place = self.input_place.text()
        if not input_place:
            input_place = os.path.expanduser('~')
        filename, __ = QFileDialog.getOpenFileName(
            self, tr('Input place layer'), input_place, tr('All Files (*.*)'))
        if filename:
            self.input_place.setText(filename)

    def load_result_toggled(self):
        """Function that perform action when load_result checkbox is clicked.
        """
        self.keyword_wizard_checkbox.setEnabled(self.load_result.isChecked())

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.2.1

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(tr('Show Help'))
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
