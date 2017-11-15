# coding=utf-8
"""Metadata Converter Dialog Implementation."""
import logging

from PyQt4.QtCore import pyqtSignature, pyqtSlot
from PyQt4.QtGui import (
    QDialog, QHBoxLayout, QLabel, QDialogButtonBox, QMessageBox)
from parameters.parameter_exceptions import InvalidValidationException
from qgis.gui import QgsMapLayerComboBox

from safe.common.exceptions import (
    NoKeywordsFoundError,
    KeywordNotFoundError,
    MetadataReadError,
    InaSAFEError)
from safe.definitions.constants import RECENT
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard, layer_purpose_aggregation)
from safe.gui.widgets.field_mapping_widget import FieldMappingWidget
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.qgis_utilities import display_warning_message_box
from safe.utilities.resources import (
    get_ui_class, html_footer, html_header)
from safe.utilities.unicode import get_string
from safe.utilities.utilities import get_error_message

FORM_CLASS = get_ui_class('metadata_converter_dialog_base.ui')

LOGGER = logging.getLogger('InaSAFE')

accepted_layer_purposes = [
    layer_purpose_hazard['key'],
    layer_purpose_exposure['key'],
    layer_purpose_aggregation['key']
]


class MetadataConverterDialog(QDialog, FORM_CLASS):

    """Dialog implementation class for the InaSAFE metadata converter tool."""

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE Metadata Converter'))
        self.parent = parent
        self.iface = iface

        self.keyword_io = KeywordIO()
        self.layer = None

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

    def set_layer(self, layer=None, keywords=None):
        """Set layer and update UI accordingly.

        :param layer: A QgsVectorLayer.
        :type layer: QgsVectorLayer

        :param keywords: Keywords for the layer.
        :type keywords: dict, None
        """
        if layer:
            self.layer = layer
        else:
            self.layer = self.layer_combo_box.currentLayer()
        if not self.layer:
            return

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

        # message = field_mapping_help()

        # string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def save_metadata(self):
        """Save metadata based on the field mapping state."""
        metadata = self.field_mapping_widget.get_field_mapping()
        for key, value in metadata['fields'].items():
            # Delete the key if it's set to None
            if key in self.metadata['inasafe_default_values']:
                self.metadata['inasafe_default_values'].pop(key)
            if value is None or value == []:
                if key in self.metadata['inasafe_fields']:
                    self.metadata['inasafe_fields'].pop(key)
            else:
                self.metadata['inasafe_fields'][key] = value

        for key, value in metadata['values'].items():
            # Delete the key if it's set to None
            if key in self.metadata['inasafe_fields']:
                self.metadata['inasafe_fields'].pop(key)
            if value is None:
                if key in self.metadata['inasafe_default_values']:
                    self.metadata['inasafe_default_values'].pop(key)
            else:
                self.metadata['inasafe_default_values'][key] = value

        # Save metadata
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=self.metadata)
        except InaSAFEError, e:
            error_message = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the following '
                    'keywords:\n %s') % error_message.to_html())))

    def accept(self):
        """Method invoked when OK button is clicked."""
        super(MetadataConverterDialog, self).accept()
