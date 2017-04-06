# coding=utf-8
"""Field Mapping Tool Implementation."""

from PyQt4.QtGui import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel

import logging

from safe.common.exceptions import (
    NoKeywordsFoundError, KeywordNotFoundError, MetadataReadError)
from safe.utilities.resources import (
    get_ui_class,
    resources_path,
    html_footer,
    html_header)
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.gui.widgets.field_mapping_widget import FieldMappingWidget

FORM_CLASS = get_ui_class('field_mapping_dialog_base.ui')

LOGGER = logging.getLogger('InaSAFE')


class FieldMappingDialog(QDialog, FORM_CLASS):

    """Dialog implementation class for the InaSAFE field mapping tool."""

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE Field Mapping Tool'))
        self.parent = parent
        self.iface = iface

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

        self.main_layout.addWidget(QLabel('Hello world'))
        self.main_layout.addLayout(self.layer_input_layout)
        # self.main_layout.addWidget(self.field_mapping_widget)

        # Signal
        self.layer_combo_box.layerChanged.connect(self.set_layer)

        if self.layer_combo_box.currentLayer():
            self.set_layer(self.layer_combo_box.currentLayer())

    def set_layer(self, layer=None):
        """Set layer and update UI accordingly."""
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

        self.field_mapping_widget = FieldMappingWidget(
            parent=self, iface=self.iface)
        self.field_mapping_widget.set_layer(self.layer)
        self.field_mapping_widget.show()
        self.main_layout.addWidget(self.field_mapping_widget)
