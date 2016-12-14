# coding=utf-8
"""Keyword Wizard Step for Threshold"""
from builtins import range
from collections import OrderedDict
from functools import partial
import logging
import numpy
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from qgis.PyQt.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QWidgetItem, QSpacerItem, QLayout

from safe.utilities.i18n import tr
from safe.definitionsv4.layer_purposes import layer_purpose_aggregation
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.definitionsv4.utilities import get_fields
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    continuous_raster_question, continuous_vector_question)
from safe.utilities.gis import is_raster_layer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwThreshold(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Threshold"""
    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.classes = OrderedDict()

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
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
        inasafe_fields = get_fields(
            layer_purpose['key'], subcategory['key'], replace_null=False)
        if inasafe_fields:
            return self.parent.step_kw_inasafe_fields

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            layer_purpose['key'], subcategory['key'], replace_null=True)
        if default_inasafe_fields:
            return self.parent.step_kw_default_inasafe_fields

        # Any other case
        return self.parent.step_kw_source

    def set_widgets(self):
        """Set widgets on the Threshold tab."""

        # Adapted from http://stackoverflow.com/a/9375273/1198772
        def clear_layout(layout):
            """Clear layout content

            :param layout: A layout.
            :type layout: QLayout
            """
            for i in reversed(list(range(layout.count()))):
                item = layout.itemAt(i)

                if isinstance(item, QWidgetItem):
                    item.widget().close()
                elif isinstance(item, QLayout):
                    clear_layout(item.layout())
                elif isinstance(item, QSpacerItem):
                    # No need to do anything
                    pass
                else:
                    pass

                # Remove the item from layout
                layout.removeItem(item)

        clear_layout(self.gridLayoutThreshold)

        # Set text in the label
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()
        classification = self.parent.step_kw_classification. \
            selected_classification()

        if is_raster_layer(self.parent.layer):
            dataset = gdal.Open(self.parent.layer.source(), GA_ReadOnly)
            min_value_layer = numpy.amin(numpy.array(
                dataset.GetRasterBand(1).ReadAsArray()))
            max_value_layer = numpy.amax(numpy.array(
                dataset.GetRasterBand(1).ReadAsArray()))
            text = continuous_raster_question % (
                layer_purpose['name'],
                layer_subcategory['name'],
                classification['name'], min_value_layer, max_value_layer)
        else:
            field_name = self.parent.step_kw_field.selected_field()
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

        self.classes = OrderedDict()
        classes = classification.get('classes')
        # Sort by value, put the lowest first
        classes = sorted(classes, key=lambda k: k['value'])

        for i, the_class in enumerate(classes):
            class_layout = QHBoxLayout()

            # Class label
            class_label = QLabel(the_class['name'])

            # Min label
            min_label = QLabel(tr('Min'))

            # Min value as double spin
            min_value_input = QDoubleSpinBox()
            if thresholds.get(the_class['key']):
                min_value_input.setValue(thresholds[the_class['key']][0])
            else:
                min_value_input.setValue(the_class['numeric_default_min'])
            min_value_input.setSingleStep(0.1)
            min_value_input.setMinimum(min_value_layer)
            min_value_input.setMaximum(max_value_layer)

            # Max label
            max_label = QLabel(tr('Max'))

            # Max value as double spin
            max_value_input = QDoubleSpinBox()
            if thresholds.get(the_class['key']):
                max_value_input.setValue(thresholds[the_class['key']][1])
            else:
                max_value_input.setValue(the_class['numeric_default_max'])
            max_value_input.setSingleStep(0.1)
            max_value_input.setMinimum(min_value_layer)
            max_value_input.setMaximum(max_value_layer)

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
                current_max_value = list(self.classes.values())[index][1]
                target_min_value = list(self.classes.values())[index + 1][0]
                if current_max_value.value() != target_min_value.value():
                    target_min_value.setValue(current_max_value.value())
            elif the_string == 'Min value':
                current_min_value = list(self.classes.values())[index][0]
                target_max_value = list(self.classes.values())[index - 1][1]
                if current_min_value.value() != target_max_value.value():
                    target_max_value.setValue(current_min_value.value())

        # Set behaviour
        for k, v in list(self.classes.items()):
            index = list(self.classes.keys()).index(k)
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
        for key, value in list(self.classes.items()):
            value_map[key] = [
                value[0].value(),
                value[1].value(),
            ]
        return value_map
