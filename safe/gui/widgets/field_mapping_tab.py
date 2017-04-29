# coding=utf-8
"""Field Mapping Widget Implementation."""

from PyQt4.QtGui import (
    QWidget,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy)
from PyQt4.QtCore import Qt, QSettings

from collections import OrderedDict
import logging

from safe.definitions.constants import (
    DO_NOT_USE,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC,
    qvariant_numbers,
    RECENT,
    GLOBAL
)

from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from safe.common.exceptions import KeywordNotFoundError
from safe.utilities.i18n import tr
from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)
from safe.utilities.default_values import get_inasafe_default_value_qsetting

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class FieldMappingTab(QWidget, object):

    """Widget class for field mapping."""

    def __init__(self, field_group=None, parent=None, iface=None):
        """Constructor."""
        # Init from parent class
        QWidget.__init__(self, parent)

        # Attributes
        self.layer = None
        self.metadata = {}
        self.parent = parent
        self.iface = iface
        self.field_group = field_group
        self.setting = QSettings()  # TODO(IS): Make dynamic

        # Main container
        self.main_layout = QVBoxLayout()

        # Inner layout
        self.header_layout = QHBoxLayout()
        self.content_layout = QHBoxLayout()
        self.footer_layout = QHBoxLayout()

        # Header
        self.header_label = QLabel()

        # Content
        self.field_layout = QVBoxLayout()
        self.parameter_layout = QHBoxLayout()

        self.field_description = QLabel(tr('List of fields'))

        self.field_list = QListWidget()
        self.field_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.field_list.setDragDropMode(QAbstractItemView.DragDrop)
        self.field_list.setDefaultDropAction(Qt.MoveAction)

        self.field_list.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.field_list.itemSelectionChanged.connect(self.update_footer)

        # Footer
        self.footer_label = QLabel()

        # Parameters
        self.extra_parameters = [
            (GroupSelectParameter, GroupSelectParameterWidget)
        ]

        self.parameters = []
        self.parameter_container = None

        # Adding to layout
        self.header_layout.addWidget(self.header_label)

        self.field_layout.addWidget(self.field_description)
        self.field_layout.addWidget(self.field_list)
        self.field_layout.setSizeConstraint(QLayout.SetMaximumSize)

        self.content_layout.addLayout(self.field_layout)
        self.content_layout.addLayout(self.parameter_layout)

        self.footer_layout.addWidget(self.footer_label)

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addLayout(self.footer_layout)

        self.setLayout(self.main_layout)

    def set_layer(self, layer, keywords=None):
        """Set layer and update UI accordingly.

        :param layer: A vector layer that has been already patched with
            metadata.
        :type layer: QgsVectorLayer
        """
        self.layer = layer
        if keywords:
            self.metadata = keywords
        else:
            # Check if it has keywords
            if not hasattr(layer, 'keywords'):
                message = 'Layer {layer_name} does not have keywords.'.format(
                    layer_name=layer.name())
                raise KeywordNotFoundError(message)
            self.metadata = layer.keywords
        self.populate_parameter()

    def populate_field_list(self, excluded_fields=None):
        """Helper to add field of the layer to the list.

        :param excluded_fields: List of field that want to be excluded.
        :type excluded_fields: list
        """
        # Populate fields list
        if excluded_fields is None:
            excluded_fields = []
        self.field_list.clear()
        for field in self.layer.dataProvider().fields():
            # Skip if it's excluded
            if field.name() in excluded_fields:
                continue
            # Skip if it's not number (float, int, etc)
            if field.type() not in qvariant_numbers:
                continue
            field_item = QListWidgetItem(self.field_list)
            field_item.setFlags(
                Qt.ItemIsEnabled |
                Qt.ItemIsSelectable |
                Qt.ItemIsDragEnabled)
            field_item.setData(Qt.UserRole, field.name())
            field_item.setText(field.name())
            self.field_list.addItem(field_item)

    def populate_parameter(self):
        """Helper to setup the parameter widget."""
        used_fields = []
        self.parameters = []
        for field in self.field_group.get('fields', []):
            selected_option = DO_NOT_USE
            options = OrderedDict([
                (DO_NOT_USE,
                 {
                     'label': tr('Do not use'),
                     'value': None,
                     'type': STATIC,
                     'constraint': {}
                 }),
            ])

            # Example: count
            if field['absolute']:
                # Used in field options
                field_label = tr('Count fields')
            else:  # Example: ratio
                # Used in field options
                field_label = tr('Ratio fields')
                global_default_value = get_inasafe_default_value_qsetting(
                    self.setting, GLOBAL, field['key'])
                options[GLOBAL_DEFAULT] = {
                    'label': tr('Global default'),
                    'value': global_default_value,
                    'type': STATIC,
                    'constraint': {}
                }
                default_custom_value = get_inasafe_default_value_qsetting(
                    self.setting, RECENT, field['key'])
                custom_value = self.metadata.get(
                    'inasafe_default_values', {}).get(
                    field['key'], default_custom_value)
                if field['key'] in self.metadata.get(
                        'inasafe_default_values', {}):
                    if custom_value == global_default_value:
                        selected_option = GLOBAL_DEFAULT
                    else:
                        selected_option = CUSTOM_VALUE
                min_value = field['default_value'].get('min_value', 0)
                max_value = field['default_value'].get('max_value', 100)
                step = (max_value - min_value) / 1000.0
                options[CUSTOM_VALUE] = {
                    'label': tr('Custom'),
                    'value': custom_value,
                    'type': SINGLE_DYNAMIC,
                    'constraint': {
                        'min': min_value,
                        'max': max_value,
                        'step': step
                    }
                }

            custom_fields = self.metadata.get('inasafe_fields', {}).get(
                field['key'], [])
            if field['key'] in self.metadata.get('inasafe_fields', {}):
                selected_option = FIELDS
            if isinstance(custom_fields, basestring):
                custom_fields = [custom_fields]
            options[FIELDS] = {
                'label': field_label,
                'value': custom_fields,
                'type': MULTIPLE_DYNAMIC,
                'constraint': {}
            }
            used_fields.extend(custom_fields)

            parameter = GroupSelectParameter()
            parameter.guid = field['key']
            parameter.name = field['name']
            parameter.options = options
            parameter.selected = selected_option

            self.parameters.append(parameter)

        self.parameter_container = ParameterContainer(
            parameters=self.parameters,
            extra_parameters=self.extra_parameters,
            vertical=False
        )
        self.parameter_container.setup_ui()

        self.parameter_layout.addWidget(self.parameter_container)

        self.populate_field_list(excluded_fields=used_fields)

        # Set header
        # TODO(IS): Set header text here
        header_text = tr('Pleas drag the field/s that represent')

    def get_parameter_value(self):
        """Get parameter of the tab.

        :returns: Dictionary of parameters by type in this format:
            {'fields': {}, 'values': {}}.
        :rtype: dict
        """
        parameters = self.parameter_container.get_parameters(True)
        field_parameters = {}
        value_parameters = {}
        for parameter in parameters:
            if parameter.selected_option_type() in [SINGLE_DYNAMIC, STATIC]:
                value_parameters[parameter.guid] = parameter.value
            elif parameter.selected_option_type() == MULTIPLE_DYNAMIC:
                field_parameters[parameter.guid] = parameter.value
        return {
            'fields': field_parameters,
            'values': value_parameters
        }

    def update_footer(self):
        """Update footer when the field list change."""
        field_item = self.field_list.currentItem()

        field_name = field_item.data(Qt.UserRole)
        field = self.layer.fields().field(field_name)

        index = self.layer.fieldNameIndex(field_name)
        unique_values = self.layer.uniqueValues(index)
        pretty_unique_values = ', '.join([str(v) for v in unique_values[:10]])

        footer_text = tr('Field type: {0}\n').format(field.typeName())
        footer_text += tr('Unique values: {0}').format(pretty_unique_values)
        self.footer_label.setText(footer_text)
