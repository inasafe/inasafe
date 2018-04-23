# coding=utf-8
"""InaSAFE Field Mapping Widget."""

import logging

from qgis.PyQt.QtWidgets import QTabWidget

from safe.common.exceptions import KeywordNotFoundError
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitions.utilities import get_field_groups
from safe.gui.widgets.field_mapping_tab import FieldMappingTab
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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

        self.keyword_io = KeywordIO()

    def set_layer(self, layer, keywords=None):
        """Set layer and update UI accordingly.

        :param layer: A vector layer that has been already patched with
            metadata.
        :type layer: QgsVectorLayer

        :param keywords: Custom keyword for the layer.
        :type keywords: dict, None
        """
        self.layer = layer
        if keywords is not None:
            self.metadata = keywords
        else:
            self.metadata = self.keyword_io.read_keywords(self.layer)
        self.populate_tabs()

    def populate_tabs(self):
        """Populating tabs based on layer metadata."""
        self.delete_tabs()
        layer_purpose = self.metadata.get('layer_purpose')
        if not layer_purpose:
            message = tr(
                'Key layer_purpose is not found in the layer {layer_name}'
            ).format(layer_name=self.layer.name())
            raise KeywordNotFoundError(message)
        if layer_purpose == layer_purpose_exposure['key']:
            layer_subcategory = self.metadata.get('exposure')
        elif layer_purpose == layer_purpose_hazard['key']:
            layer_subcategory = self.metadata.get('hazard')
        else:
            layer_subcategory = None

        field_groups = get_field_groups(layer_purpose, layer_subcategory)
        for field_group in field_groups:
            tab = FieldMappingTab(field_group, self, self.iface)
            tab.set_layer(self.layer, self.metadata)
            self.addTab(tab, field_group['name'])
            self.tabs.append(tab)

    def delete_tabs(self):
        """Methods to delete tabs."""
        self.clear()
        self.tabs = []

    def get_field_mapping(self):
        """Obtain metadata from current state of the widget.

        :returns: Dictionary of values by type in this format:
            {'fields': {}, 'values': {}}.
        :rtype: dict
        """
        fields = {}
        values = {}
        for tab in self.tabs:
            parameter_values = tab.get_parameter_value()
            fields.update(parameter_values['fields'])
            values.update(parameter_values['values'])
        return {
            'fields': fields,
            'values': values
        }
