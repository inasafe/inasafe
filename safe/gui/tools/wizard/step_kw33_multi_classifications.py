# coding=utf-8
"""InaSAFE Keyword Wizard Step for Multi Classifications."""

from PyQt4.QtGui import (
    QLabel, QHBoxLayout, QComboBox, QPushButton, QWidgetItem, QLayoutItem,
    QSpacerItem)
from PyQt4.QtCore import Qt

from safe.utilities.i18n import tr
from safe.definitions.exposure import exposure_all
from safe.definitions.font import big_font
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.utilities.gis import is_raster_layer
from safe.definitions.utilities import get_fields, get_non_compulsory_fields
from safe.definitions.layer_modes import layer_mode_continuous
from safe.gui.tools.wizard.wizard_strings import (
    multiple_classified_hazard_classifications_vector,
    multiple_continuous_hazard_classifications_vector,
    multiple_classified_hazard_classifications_raster,
    multiple_continuous_hazard_classifications_raster)
from safe.gui.tools.wizard.wizard_utils import clear_layout

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwMultiClassifications(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Multi Classification."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        # TODO(IS): Update this if the development is finished
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose != layer_purpose_aggregation:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
        else:
            subcategory = {'key': None}

        if is_raster_layer(self.parent.layer):
            return self.parent.step_kw_source

        # Check if it can go to inasafe field step
        inasafe_fields = get_non_compulsory_fields(
            layer_purpose['key'], subcategory['key'])
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
        """Set widgets on the Multi classification step."""
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        field = self.parent.step_kw_field.selected_field()
        is_raster = is_raster_layer(self.parent.layer)

        # Set the step description
        if is_raster:
            if layer_mode == layer_mode_continuous:
                text_label = multiple_continuous_hazard_classifications_raster
            else:
                text_label = multiple_classified_hazard_classifications_raster
            # noinspection PyAugmentAssignment
            text_label = text_label % (
                subcategory['name'], layer_purpose['name'])
        else:
            if layer_mode == layer_mode_continuous:
                text_label = multiple_continuous_hazard_classifications_vector
            else:
                text_label = multiple_classified_hazard_classifications_vector
            # noinspection PyAugmentAssignment
            text_label = text_label % (
                subcategory['name'], layer_purpose['name'], field)

        self.multi_classifications_label.setText(text_label)

        # Set the left panel
        left_panel_heading = QLabel(tr('Classifications'))
        left_panel_heading.setFont(big_font)
        self.left_layout.addWidget(left_panel_heading)
        for exposure in exposure_all:
            exposure_layout = QHBoxLayout()

            # Add label
            exposure_label = QLabel(exposure['name'])

            # Add combo box
            exposure_combo_box = QComboBox()
            hazard_classifications = subcategory.get('classifications')
            # Iterate through all available hazard classifications
            for i, hazard_classification in enumerate(hazard_classifications):
                exposure_combo_box.addItem(hazard_classification['name'])
                exposure_combo_box.setItemData(
                    i, hazard_classification['key'], Qt.UserRole)

            # Add edit button
            exposure_edit_button = QPushButton(tr('Edit'))

            # Arrange in layout
            exposure_layout.addWidget(exposure_label)
            exposure_layout.addWidget(exposure_combo_box)
            exposure_layout.addWidget(exposure_edit_button)
            self.left_layout.addLayout(exposure_layout)
        # Set the right panel

    def clear(self):
        """Clear current state."""
        clear_layout(self.left_layout)
        clear_layout(self.right_layout)
