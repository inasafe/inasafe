# coding=utf-8
"""InaSAFE Field Mapping Widget."""

from PyQt4.QtGui import QTabWidget
import logging

from safe.definitions.layer_purposes import (
    layer_purpose_aggregation, layer_purpose_exposure)
from safe.definitions.field_groups import (
    aggregation_field_groups, exposure_field_groups)

from safe.gui.widgets.field_mapping_tab import FieldMappingTab

LOGGER = logging.getLogger('InaSAFE')


class FieldMappingWidget(QTabWidget, object):
    """Field Mapping Widget."""

    def __init__(self, parent=None, iface=None):
        """Constructor."""

        super(FieldMappingWidget, self).__init__(parent)

        # Attributes
        self.parent = parent
        self.iface = iface

        self.layer = None
        self.metadata = {}

        self.tabs = []  # Store all tabs

        # Layout

    def set_layer(self, layer):
        """Set layer and update UI accordingly.

        :param layer: A vector ayer that has been already patched with
            metadata.
        :type layer: QgsVectorLayer
        """
        # Check if it has keywords
        if not hasattr(layer, 'keywords'):
            raise
        self.layer = layer
        self.metadata = layer.keywords
        self.populate_tabs()

    def populate_tabs(self):
        """Populating tabs based on layer metadata."""
        field_groups = []
        if self.metadata['layer_purpose'] == layer_purpose_aggregation['key']:
            field_groups = aggregation_field_groups
        elif self.metadata['layer_purpose'] == layer_purpose_exposure['key']:
            field_groups = exposure_field_groups
        for field_group in field_groups:
            tab = FieldMappingTab(field_group, self, self.iface)
            tab.set_layer(self.layer)
            self.addTab(tab, field_group['name'])
            self.tabs.append(tab)