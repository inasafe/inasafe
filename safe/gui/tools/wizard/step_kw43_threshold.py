# coding=utf-8
"""InaSAFE Wizard Step Threshold."""

import logging
from collections import OrderedDict
from functools import partial

from PyQt4.QtGui import QDoubleSpinBox, QHBoxLayout, QLabel
from qgis.core import QgsRasterBandStats

from safe import messaging as m
from safe.definitions.layer_geometry import layer_geometry_raster
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.definitions.utilities import get_fields, get_non_compulsory_fields
from safe.gui.tools.wizard.utilities import clear_layout, skip_inasafe_field
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    continuous_raster_question, continuous_vector_question)
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwThreshold(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Threshold."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.classes = OrderedDict()

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        if self.parent.get_layer_geometry_key() == \
                layer_geometry_raster['key']:
            return self.parent.step_kw_source

        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose['key'] != layer_purpose_aggregation['key']:
            subcategory = self.parent.step_kw_subcategory. \
                selected_subcategory()
        else:
            subcategory = {'key': None}

        # Check if it can go to inasafe field step
        non_compulsory_fields = get_non_compulsory_fields(
            layer_purpose['key'], subcategory['key'])
        if not skip_inasafe_field(self.parent.layer, non_compulsory_fields):
            return self.parent.step_kw_inasafe_fields

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            layer_purpose['key'],
            subcategory['key'],
            replace_null=True,
            in_group=False
        )
        if default_inasafe_fields:
            return self.parent.step_kw_default_inasafe_fields

        # Any other case
        return self.parent.step_kw_source

    def set_widgets(self):
        """Set widgets on the Threshold tab."""
        clear_layout(self.gridLayoutThreshold)

        # Set text in the label
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()
        classification = self.parent.step_kw_classification. \
            selected_classification()

        if is_raster_layer(self.parent.layer):
            statistics = self.parent.layer.dataProvider().bandStatistics(
                1, QgsRasterBandStats.All, self.parent.layer.extent(), 0)
            text = continuous_raster_question % (
                layer_purpose['name'],
                layer_subcategory['name'],
                classification['name'],
                statistics.minimumValue,
                statistics.maximumValue)
        else:
            field_name = self.parent.step_kw_field.selected_fields()
            field_index = self.parent.layer.fieldNameIndex(field_name)
            min_value_layer = self.parent.layer.minimumValue(field_index)
            max_value_layer = self.parent.layer.maximumValue(field_index)
            text = continuous_vector_question % (
                layer_purpose['name'],
                layer_subcategory['name'],
                field_name,
                classification['name'],
                min_value_layer,
                max_value_layer)
        self.lblThreshold.setText(text)

        thresholds = self.parent.get_existing_keyword('thresholds')
        selected_unit = self.parent.step_kw_unit.selected_unit()['key']

        self.classes = OrderedDict()
        classes = classification.get('classes')
        # Sort by value, put the lowest first
        classes = sorted(classes, key=lambda k: k['value'])

        for i, the_class in enumerate(classes):
            class_layout = QHBoxLayout()

            # Class label
            class_label = QLabel(the_class['name'])

            # Min label
            min_label = QLabel(tr('Min >'))

            # Min value as double spin
            min_value_input = QDoubleSpinBox()
            # TODO(IS) We can set the min and max depends on the unit, later
            min_value_input.setMinimum(0)
            min_value_input.setMaximum(999999)
            if thresholds.get(the_class['key']):
                min_value_input.setValue(thresholds[the_class['key']][0])
            else:
                default_min = the_class['numeric_default_min']
                if isinstance(default_min, dict):
                    default_min = the_class[
                        'numeric_default_min'][selected_unit]
                min_value_input.setValue(default_min)
            min_value_input.setSingleStep(0.1)

            # Max label
            max_label = QLabel(tr('Max <='))

            # Max value as double spin
            max_value_input = QDoubleSpinBox()
            # TODO(IS) We can set the min and max depends on the unit, later
            max_value_input.setMinimum(0)
            max_value_input.setMaximum(999999)
            if thresholds.get(the_class['key']):
                max_value_input.setValue(thresholds[the_class['key']][1])
            else:
                default_max = the_class['numeric_default_max']
                if isinstance(default_max, dict):
                    default_max = the_class[
                        'numeric_default_max'][selected_unit]
                max_value_input.setValue(default_max)
            max_value_input.setSingleStep(0.1)

            # Add to class_layout
            class_layout.addWidget(min_label)
            class_layout.addWidget(min_value_input)
            # class_layout.addStretch(1)
            class_layout.addWidget(max_label)
            class_layout.addWidget(max_value_input)

            # Add to grid_layout
            self.gridLayoutThreshold.addWidget(class_label, i, 0)
            self.gridLayoutThreshold.addLayout(class_layout, i, 1)

            self.classes[the_class['key']] = [min_value_input, max_value_input]

        self.gridLayoutThreshold.setSpacing(0)

        def min_max_changed(index, the_string):
            """Slot when min or max value change.

            :param index: The index of the double spin.
            :type index: int

            :param the_string: The flag to indicate the min or max value.
            :type the_string: str
            """
            if the_string == 'Max value':
                current_max_value = self.classes.values()[index][1]
                target_min_value = self.classes.values()[index + 1][0]
                if current_max_value.value() != target_min_value.value():
                    target_min_value.setValue(current_max_value.value())
            elif the_string == 'Min value':
                current_min_value = self.classes.values()[index][0]
                target_max_value = self.classes.values()[index - 1][1]
                if current_min_value.value() != target_max_value.value():
                    target_max_value.setValue(current_min_value.value())

        # Set behaviour
        for k, v in self.classes.items():
            index = self.classes.keys().index(k)
            if index < len(self.classes) - 1:
                # Max value changed
                v[1].valueChanged.connect(partial(
                    min_max_changed, index=index, the_string='Max value'))
            if index > 0:
                # Min value
                v[0].valueChanged.connect(partial(
                    min_max_changed, index=index, the_string='Min value'))

    def get_threshold(self):
        """Return threshold based on current state."""
        value_map = dict()
        for key, value in self.classes.items():
            value_map[key] = [
                value[0].value(),
                value[1].value(),
            ]
        return value_map

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Threshold Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'threshold of each class in the classification that you choosed '
            'in the previous step.').format(step_name=self.step_name)))
        return message
