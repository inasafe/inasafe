# coding=utf-8
"""Field Mapping Tool Implementation."""

from PyQt4.QtGui import (
    QDialog, QHBoxLayout, QLabel, QDialogButtonBox, QMessageBox)
from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel
from PyQt4.QtCore import pyqtSignature, pyqtSlot, QSettings

import logging

from safe.definitions.constants import RECENT
from safe.common.exceptions import (
    NoKeywordsFoundError, KeywordNotFoundError, MetadataReadError,
    InaSAFEError)
from safe.utilities.resources import (
    get_ui_class,
    html_footer,
    html_header)
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.gui.widgets.field_mapping_widget import FieldMappingWidget
from safe.gui.tools.help.field_mapping_help import field_mapping_help
from safe.utilities.utilities import (
    get_error_message, is_keyword_version_supported)
from safe.utilities.default_values import set_inasafe_default_value_qsetting

FORM_CLASS = get_ui_class('field_mapping_dialog_base.ui')

LOGGER = logging.getLogger('InaSAFE')


class FieldMappingDialog(QDialog, FORM_CLASS):

    """Dialog implementation class for the InaSAFE field mapping tool."""

    def __init__(self, parent=None, iface=None, setting=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE Field Mapping Tool'))
        self.parent = parent
        self.iface = iface
        if setting is None:
            setting = QSettings()
        self.setting = setting

        self.keyword_io = KeywordIO()

        self.layer = None
        self.metadata = {}

        self.layer_input_layout = QHBoxLayout()
        self.layer_label = QLabel(tr('Layer'))
        self.layer_combo_box = QgsMapLayerComboBox()
        self.layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.field_mapping_widget = None
        self.main_stacked_widget.setCurrentIndex(1)

        # Input
        self.layer_input_layout.addWidget(self.layer_label)
        self.layer_input_layout.addWidget(self.layer_combo_box)

        self.header_label = QLabel()
        self.main_layout.addWidget(self.header_label)
        self.main_layout.addLayout(self.layer_input_layout)

        # Signal
        self.layer_combo_box.layerChanged.connect(self.set_layer)

        if self.layer_combo_box.currentLayer():
            self.set_layer(self.layer_combo_box.currentLayer())

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

    def set_layer(self, layer=None):
        """Set layer and update UI accordingly.

        :param layer: A QgsVectorLayer.
        :type layer: QgsVectorLayer
        """
        if self.field_mapping_widget is not None:
            self.field_mapping_widget.setParent(None)
            self.field_mapping_widget.close()
            self.field_mapping_widget.deleteLater()
            self.main_layout.removeWidget(self.field_mapping_widget)

        if layer:
            self.layer = layer
        else:
            self.layer = self.layer_combo_box.currentLayer()
        if not self.layer:
            LOGGER.debug('No layer')
            return
        else:
            LOGGER.debug('A layer: %s' % self.layer.name())
        try:
            self.metadata = self.layer.keywords
        except AttributeError:
            try:
                self.metadata = self.keyword_io.read_keywords(self.layer)
                self.layer.keywords = self.metadata
            except (
                NoKeywordsFoundError,
                KeywordNotFoundError,
                MetadataReadError) as e:
                raise e
        if 'inasafe_default_values' not in self.metadata:
            self.metadata['inasafe_default_values'] = {}
        if 'inasafe_fields' not in self.metadata:
            self.metadata['inasafe_fields'] = {}
        self.field_mapping_widget = FieldMappingWidget(
            parent=self, iface=self.iface)
        self.field_mapping_widget.set_layer(self.layer)
        self.field_mapping_widget.show()
        self.main_layout.addWidget(self.field_mapping_widget)

        # Set header label
        group_names = [self.field_mapping_widget.tabText(i) for i in
             range(self.field_mapping_widget.count())]
        if len(group_names) == 1:
            pretty_group_name = group_names[0]
        elif len(group_names) == 2:
            pretty_group_name = group_names[0] + tr(' and ') + group_names[1]
        else:
            pretty_group_name = ', '.join(group_names[:-1])
            pretty_group_name += tr(', and {0}').format(group_names[-1])
        header_text = tr(
            'Please fill the information for every tab to determine the '
            'attribute for {0} group.').format(pretty_group_name)
        self.header_label.setText(header_text)

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

        message = field_mapping_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def save_metadata(self):
        """Save metadata based on the field mapping state."""
        LOGGER.debug('Save metadata')
        metadata = self.field_mapping_widget.get_field_mapping()
        for key, value in metadata['fields'].items():
            # Delete the key if it's set to None
            if key in self.metadata['inasafe_default_values']:
                self.metadata['inasafe_default_values'].pop(key)
            if value is None:
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

        if self.metadata.get('inasafe_default_values'):
            for key, value in \
                    self.metadata['inasafe_default_values'].items():
                set_inasafe_default_value_qsetting(
                    self.setting, key, RECENT, value)

    def accept(self):
        """Method invoked when OK button is clicked."""
        LOGGER.debug('Accepted.')
        self.save_metadata()
        self.close()
