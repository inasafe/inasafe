# coding=utf-8
"""Metadata Converter Dialog Implementation."""

import logging
import os

from qgis.PyQt.QtCore import Qt, QFile, pyqtSignal
from qgis.PyQt.Qt import QT_VERSION
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from qgis.PyQt.QtGui import QIcon

from safe.common.exceptions import (
    NoKeywordsFoundError,
    KeywordNotFoundError,
    MetadataConversionError,
)
from safe.definitions.exposure import exposure_all
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard, layer_purpose_aggregation)
from safe.gui.tools.help.metadata_converter_help import metadata_converter_help
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.metadata import active_classification
from safe.utilities.metadata import (
    convert_metadata, write_iso19115_metadata
)
from safe.utilities.qgis_utilities import (
    display_warning_message_box, display_success_message_bar)
from safe.utilities.resources import (
    get_ui_class, html_footer, html_header, resources_path)
from safe.utilities.utilities import is_keyword_version_supported

FORM_CLASS = get_ui_class('metadata_converter_dialog_base.ui')

LOGGER = logging.getLogger('InaSAFE')

accepted_layer_purposes = [
    layer_purpose_hazard['key'],
    layer_purpose_exposure['key'],
    layer_purpose_aggregation['key']
]


class MetadataConverterDialog(QDialog, FORM_CLASS):

    """Dialog implementation class for the InaSAFE metadata converter tool."""

    resized = pyqtSignal()

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        icon = resources_path('img', 'icons', 'show-metadata-converter.svg')
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle(self.tr('InaSAFE Metadata Converter'))
        self.parent = parent
        self.iface = iface

        self.keyword_io = KeywordIO()
        self.layer = None

        # Setup header label
        self.header_label.setText(tr(
            'In this tool, you can convert a metadata 4.x of a layer to '
            'metadata 3.5. You will get a directory contains all the files of '
            'the layer and the new 3.5 metadata. If you want to convert '
            'hazard layer, you need to choose what exposure that you want to '
            'work with.')
        )

        # Setup input layer combo box
        # Filter our layers
        excepted_layers = []
        for i in range(self.input_layer_combo_box.count()):
            layer = self.input_layer_combo_box.layer(i)
            try:
                keywords = self.keyword_io.read_keywords(layer)
            except (KeywordNotFoundError, NoKeywordsFoundError):
                # Filter out if no keywords
                excepted_layers.append(layer)
                continue
            layer_purpose = keywords.get('layer_purpose')
            if not layer_purpose:
                # Filter out if no layer purpose
                excepted_layers.append(layer)
                continue
            if layer_purpose not in accepted_layer_purposes:
                # Filter out if not aggregation, hazard, or exposure layer
                excepted_layers.append(layer)
                continue
            keyword_version = keywords.get('keyword_version')
            if not keyword_version:
                # Filter out if no keyword version
                excepted_layers.append(layer)
                continue
            if not is_keyword_version_supported(keyword_version):
                # Filter out if the version is not supported (4.x)
                excepted_layers.append(layer)
                continue

        self.input_layer_combo_box.setExceptedLayerList(excepted_layers)

        # Select the active layer.
        if self.iface.activeLayer():
            found = self.input_layer_combo_box.findText(
                self.iface.activeLayer().name())
            if found > -1:
                self.input_layer_combo_box.setLayer(self.iface.activeLayer())

        # Set current layer as the active layer
        if self.input_layer_combo_box.currentLayer():
            self.set_layer(self.input_layer_combo_box.currentLayer())

        # Signals
        self.input_layer_combo_box.layerChanged.connect(self.set_layer)
        self.output_path_tool.clicked.connect(self.select_output_directory)

        # Set widget to show the main page (not help page)
        self.main_stacked_widget.setCurrentIndex(1)

        # Set up things for context help
        self.help_button = self.button_box.button(QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)

        # Set up things for ok button
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.ok_button.clicked.connect(self.accept)

        # Set up things for cancel button
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.cancel_button.clicked.connect(self.reject)

        # The bug is fixed in QT 5.4
        if QT_VERSION < 0x050400:
            self.resized.connect(self.after_resize)

    def set_layer(self, layer=None):
        """Set layer and update UI accordingly.

        :param layer: A QgsVectorLayer.
        :type layer: QgsVectorLayer
        """
        if layer:
            self.layer = layer
        else:
            self.layer = self.input_layer_combo_box.currentLayer()
        if not self.layer:
            return

        keywords = self.keyword_io.read_keywords(layer)
        self.show_current_metadata()

        # TODO(IS): Show only possible exposure target
        if keywords['layer_purpose'] == layer_purpose_hazard['key']:
            self.target_exposure_label.setEnabled(True)
            self.target_exposure_combo_box.setEnabled(True)
            self.target_exposure_combo_box.clear()
            for exposure in exposure_all:
                # Only show exposure that has active classification
                if active_classification(keywords, exposure['key']):
                    self.target_exposure_combo_box.addItem(
                        exposure['name'], exposure['key'])
        else:
            self.target_exposure_label.setEnabled(False)
            self.target_exposure_combo_box.setEnabled(False)
            self.target_exposure_combo_box.clear()
            self.target_exposure_combo_box.addItem(tr("Not Applicable"))

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
        message = metadata_converter_help()

        string = header
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def convert_metadata(self):
        """Method invoked when OK button is clicked."""
        # Converter parameter
        converter_parameter = {}
        # Target exposure
        if self.target_exposure_combo_box.isEnabled():
            exposure_index = self.target_exposure_combo_box.currentIndex()
            exposure_key = self.target_exposure_combo_box.itemData(
                exposure_index, Qt.UserRole)
            converter_parameter['exposure'] = exposure_key

        # Metadata
        current_metadata = self.keyword_io.read_keywords(self.layer)
        old_metadata = convert_metadata(
            current_metadata, **converter_parameter)

        # Input
        input_layer_path = self.layer.source()
        input_directory_path = os.path.dirname(input_layer_path)
        input_file_name = os.path.basename(input_layer_path)
        input_base_name = os.path.splitext(input_file_name)[0]
        input_extension = os.path.splitext(input_file_name)[1]

        # Output
        output_path = self.output_path_line_edit.text()
        output_directory_path = os.path.dirname(output_path)
        output_file_name = os.path.basename(output_path)
        output_base_name = os.path.splitext(output_file_name)[0]

        # Copy all related files, if exists
        extensions = [
            # Vector layer
            '.shp', '.geojson', '.qml', '.shx', '.dbf', '.prj', 'qpj',
            # Raster layer
            '.tif', '.tiff', '.asc',
        ]
        for extension in extensions:
            source_path = os.path.join(
                input_directory_path, input_base_name + extension)
            if not os.path.exists(source_path):
                continue
            target_path = os.path.join(
                output_directory_path, output_base_name + extension)
            QFile.copy(source_path, target_path)

        # Replace the metadata with the old one
        output_file_path = os.path.join(
            output_directory_path, output_base_name + input_extension
        )
        write_iso19115_metadata(
            output_file_path, old_metadata, version_35=True)

    def accept(self):
        """Method invoked when OK button is clicked."""
        output_path = self.output_path_line_edit.text()
        if not output_path:
            display_warning_message_box(
                self,
                tr('Empty Output Path'),
                tr('Output path can not be empty'))
            return
        try:
            self.convert_metadata()
        except MetadataConversionError as e:
            display_warning_message_box(
                self,
                tr('Metadata Conversion Failed'),
                e.message)
            return

        if not os.path.exists(output_path):
            display_warning_message_box(
                self,
                tr('Metadata Conversion Failed'),
                tr('Result file is not found.'))
            return

        display_success_message_bar(
            tr('Metadata Conversion Success'),
            tr('You can find your copied layer with metadata version 3.5 in '
               '%s' % output_path))
        super(MetadataConverterDialog, self).accept()

    def select_output_directory(self):
        """Select output directory"""
        # Input layer
        input_layer_path = self.layer.source()
        input_file_name = os.path.basename(input_layer_path)
        input_extension = os.path.splitext(input_file_name)[1]

        # Get current path
        current_file_path = self.output_path_line_edit.text()
        if not current_file_path or not os.path.exists(current_file_path):
            current_file_path = input_layer_path

        # Filtering based on input layer
        extension_mapping = {
            '.shp': tr('Shapefile (*.shp);;'),
            '.geojson': tr('GeoJSON (*.geojson);;'),
            '.tif': tr('Raster TIF/TIFF (*.tif, *.tiff);;'),
            '.tiff': tr('Raster TIF/TIFF (*.tiff, *.tiff);;'),
            '.asc': tr('Raster ASCII File (*.asc);;'),
        }
        # Open File Dialog
        file_path, __ = QFileDialog.getSaveFileName(
            self,
            tr('Output File'),
            current_file_path,
            extension_mapping[input_extension]
        )
        if file_path:
            self.output_path_line_edit.setText(file_path)

    def show_current_metadata(self):
        """Show metadata of the current selected layer."""
        LOGGER.debug('Showing layer: ' + self.layer.name())
        keywords = KeywordIO(self.layer)
        content_html = keywords.to_message().to_html()
        full_html = html_header() + content_html + html_footer()
        self.metadata_preview_web_view.setHtml(full_html)

    # Adapted from https://stackoverflow.com/a/43126946/1198772
    def resizeEvent(self, event):
        """Emit custom signal when the window is re-sized.

        :param event: The re-sized event.
        :type event: QResizeEvent
        """
        self.resized.emit()
        return super(MetadataConverterDialog, self).resizeEvent(event)

    def after_resize(self):
        """Method after resizing the window."""
        # https://stackoverflow.com/q/25644026/1198772
        # It's fixed in QT 5.4 https://bugreports.qt.io/browse/QTBUG-37673
        max_height = self.height() - 275  # Magic number, to make it pretty
        self.metadata_preview_web_view.setMaximumHeight(max_height)
