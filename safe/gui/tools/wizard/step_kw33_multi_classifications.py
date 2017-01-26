# coding=utf-8
"""InaSAFE Keyword Wizard Step for Multi Classifications."""

import logging
from functools import partial

from PyQt4.QtGui import QLabel, QHBoxLayout, QComboBox, QPushButton, QTextBrowser
from PyQt4.QtCore import Qt
from PyQt4.QtWebKit import QWebView


import safe.messaging as m
from safe.messaging import styles

from safe.utilities.i18n import tr
from safe.definitions.exposure import exposure_all
from safe.definitions.font import big_font
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.widgets.message_viewer import MessageViewer
from safe.utilities.gis import is_raster_layer
from safe.definitions.utilities import (
    get_fields, get_non_compulsory_fields, classification_thresholds)
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

# Mode
CHOOSE_MODE = 0
EDIT_MODE = 1

class StepKwMultiClassifications(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Multi Classification."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.exposures = []
        self.exposure_labels = []
        self.exposure_combo_boxes = []
        self.exposure_edit_buttons = []
        self.mode = 0
        # Store the current representative state of the UI.
        # self.classifications = {}
        self.value_maps = {}
        self.thresholds = {}
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
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
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
                    i, hazard_classification, Qt.UserRole)

            # Add edit button
            exposure_edit_button = QPushButton(tr('Edit'))
            exposure_edit_button.clicked.connect(
                partial(self.edit_button_clicked,
                        edit_button=exposure_edit_button,
                        exposure_combo_box=exposure_combo_box,
                        exposure=exposure))

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
            self.exposure_labels.append(label)

            # Set the current thresholds
            if layer_mode == layer_mode_continuous:
                unit = self.parent.step_kw_unit.selected_unit()
                thresholds = classification_thresholds(
                    self.get_classification(exposure_combo_box), unit)
                self.thresholds[exposure['key']] = thresholds

    def edit_button_clicked(self, edit_button, exposure_combo_box, exposure):
        """Method to handle edit button."""
        LOGGER.debug(exposure['key'])
        LOGGER.debug(self.get_classification(exposure_combo_box)['key'])
        if self.mode == CHOOSE_MODE:
            # Change mode
            self.mode = EDIT_MODE
            # Disable all edit button
            for exposure_edit_button in self.exposure_edit_buttons:
                exposure_edit_button.setEnabled(False)
            # Except one that was clicked
            edit_button.setEnabled(True)
            # Disable all combo box
            for exposure_combo_box in self.exposure_combo_boxes:
                exposure_combo_box.setEnabled(False)
            # Change the edit button to cancel
            edit_button.setText(tr('Cancel'))

            # Clear right panel
            # Show edit threshold or value mapping

        elif self.mode == EDIT_MODE:
            # Change mode
            self.mode = CHOOSE_MODE
            # Enable all edit button
            for exposure_edit_button in self.exposure_edit_buttons:
                exposure_edit_button.setEnabled(True)
            # Enable all combo box
            for exposure_combo_box in self.exposure_combo_boxes:
                exposure_combo_box.setEnabled(True)
            # Revert back the text of the edit button.
            edit_button.setText(tr('Edit'))

            # Clear right panel
            # Show current state

    def setup_thresholds_panel(self):
        """Setup threshold panel in the right panel."""


    def show_current_state(self):
        """Setup the UI for QTextEdit to show the current state."""
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
        right_panel_heading = QLabel(tr('Status'))
        right_panel_heading.setFont(big_font)
        self.right_layout.addWidget(right_panel_heading)

        message = m.Message()
        if layer_mode == layer_mode_continuous:
            unit = self.parent.step_kw_unit.selected_unit()
            title = tr('Thresholds')
        else:
            unit = None
            title = tr('Value maps')

        message.add(m.Heading(title, **INFO_STYLE))

        for i in range(len(self.exposures)):
            message.add(m.Text(self.exposure_labels[i]))
            table = m.Table(style_class='table table-condensed table-striped')
            header = m.Row()
            header.add(m.Cell(tr('Class name')))
            header.add(m.Cell(tr('Minimum')))
            header.add(m.Cell(tr('Maximum')))
            table.add(header)
            classification = self.get_classification(
                self.exposure_combo_boxes[i])
            thresholds = classification_thresholds(classification, unit)
            for class_key, threshold in thresholds.items():
                row = m.Row()
                row.add(m.Cell(class_key))
                row.add(m.Cell(threshold[0]))
                row.add(m.Cell(threshold[1]))
                table.add(row)
            message.add(table)

        status_text_edit = QTextBrowser(None)
        # status_text_edit = MessageViewer(None)
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
        self.show_current_state()

    def clear(self):
        """Clear current state."""
        clear_layout(self.left_layout)
        clear_layout(self.right_layout)

    def get_current_state(self):
        """Obtain current classification and value map / threshold."""

    def get_classification(self, combo_box):
        """Helper to obtain the classification from a combo box.

        :param combo_box: A classification combo box.
        :type combo_box: QComboBox.

        :returns: Classification definitions.
        :rtype: dict
        """
        return combo_box.itemData(combo_box.currentIndex(), Qt.UserRole)
