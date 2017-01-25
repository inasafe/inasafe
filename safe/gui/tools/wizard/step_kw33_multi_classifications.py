# coding=utf-8
"""InaSAFE Keyword Wizard Step for Multi Classifications."""

import logging

from PyQt4.QtGui import QLabel, QHBoxLayout, QComboBox, QPushButton, QTextEdit
from PyQt4.QtCore import Qt

import safe.messaging as m
from safe.messaging import styles

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
from safe.gui.tools.wizard.wizard_utils import clear_layout, skip_inasafe_field
from safe.utilities.resources import html_footer, html_header, resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_wizard_step_ui_class(__file__)
INFO_STYLE = styles.INFO_STYLE


class StepKwMultiClassifications(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Multi Classification."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.exposures = []
        self.exposure_combo_boxes = []
        self.exposure_edit_buttons = []

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

        if not skip_inasafe_field(self.parent.layer, inasafe_fields):
            return self.parent.step_kw_inasafe_fields

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            layer_purpose['key'], subcategory['key'], replace_null=True)
        if default_inasafe_fields:
            return self.parent.step_kw_default_inasafe_fields

        # Any other case
        return self.parent.step_kw_source

    def set_wizard_step_description(self):
        """Set the text for description."""
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        field = self.parent.step_kw_field.selected_field()
        is_raster = is_raster_layer(self.parent.layer)

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


    def setup_left_panel(self):
        """Setup the UI for left panel.

        Generate all exposure, combobox, and edit button.
        """
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        left_panel_heading = QLabel(tr('Classifications'))
        left_panel_heading.setFont(big_font)
        self.left_layout.addWidget(left_panel_heading)
        for exposure in exposure_all:
            exposure_layout = QHBoxLayout()

            # Add label
            # Hazard on Exposure Classifications
            label = tr('%s on %s Classifications' % (
                subcategory['name'], exposure['name']))
            exposure_label = QLabel(label)

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

            # Stretch
            exposure_layout.setStretch(0, 0)
            exposure_layout.setStretch(0, 0)
            exposure_layout.setStretch(0, 1)
            self.left_layout.addLayout(exposure_layout)

            # Adding to step's attribute
            self.exposures.append(exposure)
            self.exposure_combo_boxes.append((exposure_combo_box))
            self.exposure_edit_buttons.append(exposure_edit_button)

    def setup_viewer(self):
        """Setup the UI for QTextEdit to show the current state."""
        right_panel_heading = QLabel(tr('Status'))
        right_panel_heading.setFont(big_font)
        self.right_layout.addWidget(right_panel_heading)

        message = m.Message()
        message.add(m.Heading(tr('InaSAFE Lorem Ipsum'), **INFO_STYLE))
        paragraph = m.Paragraph(tr(
            'InaSAFE is free software that produces realistic natural hazard '
            'impact scenarios for better planning, preparedness and response '
            'activities. It provides a simple but rigourous way to combine data '
            'from scientists, local governments and communities to provide '
            'insights into the likely impacts of future disaster events.'
        ))
        message.add(paragraph)

        status_text_edit = QTextEdit()
        html_string = html_header() + message.to_html() + html_footer()
        status_text_edit.setHtml(html_string)
        self.right_layout.addWidget(status_text_edit)

    def set_widgets(self):
        """Set widgets on the Multi classification step."""
        # Set the step description
        self.set_wizard_step_description()

        # Set the left panel
        self.setup_left_panel()

        # Set the right panel, for the beginning show the viewer
        self.setup_viewer()

    def clear(self):
        """Clear current state."""
        clear_layout(self.left_layout)
        clear_layout(self.right_layout)
