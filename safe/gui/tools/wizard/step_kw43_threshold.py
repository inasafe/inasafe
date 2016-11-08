# coding=utf-8
"""Keyword Wizard Step for Threshold"""
from PyQt4.QtGui import (
    QDoubleSpinBox, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout)

from safe.utilities.i18n import tr
from safe.definitionsv4.layer_purposes import layer_purpose_aggregation
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.definitionsv4.utilities import get_fields
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.gis import is_raster_layer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwThreshold(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Threshold"""
    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

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
        classification = self.parent.step_kw_classification.\
            selected_classification()
        classes = classification.get('classes')

        for i, the_class in enumerate(classes):
            class_layout = QHBoxLayout()

            # Class label
            class_label = QLabel(the_class['name'])

            # Min label
            min_label = QLabel(tr('Min'))

            # Min value as double spin
            min_value = QDoubleSpinBox()
            min_value.setValue(the_class['numeric_default_min'])
            min_value.setSingleStep(0.1)

            # Max label
            max_label = QLabel(tr('Max'))

            # Max value as double spin
            max_value = QDoubleSpinBox()
            max_value.setValue(the_class['numeric_default_max'])
            max_value.setSingleStep(0.1)

            # Add to class_layout
            class_layout.addWidget(min_label)
            class_layout.addWidget(min_value)
            # class_layout.addStretch(1)
            class_layout.addWidget(max_label)
            class_layout.addWidget(max_value)

            # Add to grid_layout
            self.gridLayoutThreshold.addWidget(class_label, i, 0)
            self.gridLayoutThreshold.addLayout(class_layout, i, 1)

        self.gridLayoutThreshold.setSpacing(0)
