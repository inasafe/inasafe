# coding=utf-8
"""InaSAFE Field Mapping Widget."""

from PyQt4.QtGui import QTabWidget
import logging

from safe.utilities.i18n import tr
from safe.common.exceptions import KeywordNotFoundError
from safe.definitions.utilities import definition

from safe.gui.widgets.field_mapping_tab import FieldMappingTab

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

    def set_layer(self, layer):
        """Set layer and update UI accordingly.

        :param layer: A vector layer that has been already patched with
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
        if 'layer_purpose' not in self.metadata:
            message = tr(
                'Key layer_purpose is not found in the layer {layer_name}'
            ).format(layer_name=self.layer.name())
            raise KeywordNotFoundError(message)
        layer_purpose = definition(self.metadata['layer_purpose'])
        field_groups = layer_purpose.get('field_groups', [])
        for field_group in field_groups:
            tab = FieldMappingTab(field_group, self, self.iface)
            tab.set_layer(self.layer)
            self.addTab(tab, field_group['name'])
            self.tabs.append(tab)

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
