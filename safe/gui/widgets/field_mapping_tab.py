# coding=utf-8
"""Field Mapping Widget Implementation."""

from PyQt4.QtGui import (
    QWidget, QListWidget, QAbstractItemView, QListWidgetItem,
    QLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QToolButton, QTabWidget,
    QGridLayout,
    QSizePolicy)
from PyQt4.QtCore import Qt, QSettings
from collections import OrderedDict

from safe.definitions.constants import RECENT, GLOBAL
from safe.definitions.constants import (
    DO_NOT_USE, CUSTOM_VALUE, GLOBAL_DEFAULT, FIELDS, STATIC, SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC)

from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from safe.utilities.i18n import tr
from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)
from safe.utilities.settings import get_inasafe_default_value_qsetting

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class FieldMapping(QWidget, object):
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
        self.header_label = QLabel('This is a header')

        # Content
        self.field_layout = QVBoxLayout()
        self.parameter_layout = QHBoxLayout()

        self.field_description = QLabel('List of fields')
        self.field_list = QListWidget()
        self.field_list.setDragDropMode(QAbstractItemView.DragDrop)
        self.field_list.setDefaultDropAction(Qt.MoveAction)
        self.field_list.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Expanding)

        # Footer
        self.footer_label = QLabel('This is a footer')

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
        self.populate_field_list()
        self.populate_parameter()

    def populate_field_list(self):
        """Helper to add field of the layer to the list."""
        # Populate fields list
        self.field_list.clear()
        self.field_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for field in self.layer.dataProvider().fields():
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
        self.parameters = []
        selected_option = DO_NOT_USE
        for field in self.field_group.get('fields', []):
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
                pass
            else: # Example: ratio
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
                # TODO(IS): Check from keywords first
                default_custom_value = get_inasafe_default_value_qsetting(
                    self.setting, RECENT, field['key'])
                custom_value = self.metadata['inasafe_default_values'].get(
                    field['key'], default_custom_value)
                if field['key'] in self.metadata['inasafe_default_values']:
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

            custom_fields = self.metadata['inasafe_fields'].get(
                field['key'], [])
            if field['key'] in self.metadata['inasafe_fields']:
                selected_option = 'field'
            if isinstance(custom_fields, basestring):
                custom_fields = [custom_fields]
            options[FIELDS] = {
                'label': field_label,
                'value': custom_fields,
                'type': MULTIPLE_DYNAMIC,
                'constraint': {}
            }


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
