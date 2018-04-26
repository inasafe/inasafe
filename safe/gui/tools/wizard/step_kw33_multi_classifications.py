# coding=utf-8
"""InaSAFE Wizard Step Multi Classifications."""


import logging
from collections import OrderedDict
from functools import partial

import numpy
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel, QHBoxLayout, QComboBox, QPushButton, QDoubleSpinBox, QGridLayout, QListWidget, QTreeWidget, QAbstractItemView, QListWidgetItem, QTreeWidgetItem, QSizePolicy
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWebKitWidgets import QWebView
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from qgis.core import QgsRasterBandStats

import safe.messaging as m
from safe.definitions.exposure import exposure_all, exposure_population
from safe.definitions.font import big_font
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.hazard_classifications import (
    earthquake_mmi_scale)
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.definitions.utilities import (
    definition,
    get_fields,
    get_non_compulsory_fields,
    default_classification_thresholds,
)
from safe.gui.tools.wizard.utilities import clear_layout, skip_inasafe_field
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    continuous_raster_question,
    continuous_vector_question,
    classify_raster_question,
    classify_vector_question)
from safe.gui.tools.wizard.wizard_strings import (
    multiple_classified_hazard_classifications_vector,
    multiple_continuous_hazard_classifications_vector,
    multiple_classified_hazard_classifications_raster,
    multiple_continuous_hazard_classifications_raster)
from safe.messaging import styles
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr
from safe.utilities.resources import html_footer, html_header
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_wizard_step_ui_class(__file__)
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE

# Mode
CHOOSE_MODE = 0
EDIT_MODE = 1

# Min and Max QDoubleEdit
MIN_VALUE_MODE = 0
MAX_VALUE_MODE = 1


class StepKwMultiClassifications(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Multi Classifications."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)
        self.exposures = []
        self.exposure_labels = []
        self.exposure_combo_boxes = []
        self.exposure_edit_buttons = []
        self.mode = CHOOSE_MODE

        self.layer_purpose = None
        self.layer_mode = None

        # Store the current representative state of the UI.
        # self.classifications = {}
        self.value_maps = {}
        self.thresholds = {}

        # Temporary attributes
        self.threshold_classes = OrderedDict()
        self.active_exposure = None

        self.list_unique_values = None
        self.tree_mapping_widget = None

        # GUI, good for testing
        self.save_button = None
        self.restore_default_button = None

        # Has default threshold
        # Trick for EQ raster for population #3853
        self.use_default_thresholds = False
        # Index of the special case exposure classification
        self.special_case_index = None

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        # Still editing
        if self.mode == EDIT_MODE:
            return False
        for combo_box in self.exposure_combo_boxes:
            # Enable if there is one that has classification
            if combo_box.currentIndex() > 0:
                return True
        # Trick for EQ raster for population #3853
        if self.use_default_thresholds:
            return True
        return False

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        if self.layer_purpose != layer_purpose_aggregation:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
        else:
            subcategory = {'key': None}

        if is_raster_layer(self.parent.layer):
            return self.parent.step_kw_source

        # Check if it can go to inasafe field step
        inasafe_fields = get_non_compulsory_fields(
            self.layer_purpose['key'], subcategory['key'])

        if not skip_inasafe_field(self.parent.layer, inasafe_fields):
            return self.parent.step_kw_inasafe_fields

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            self.layer_purpose['key'],
            subcategory['key'],
            replace_null=True,
            in_group=False
        )
        if default_inasafe_fields:
            return self.parent.step_kw_default_inasafe_fields

        # Any other case
        return self.parent.step_kw_source

    def set_wizard_step_description(self):
        """Set the text for description."""
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        field = self.parent.step_kw_field.selected_fields()
        is_raster = is_raster_layer(self.parent.layer)

        if is_raster:
            if self.layer_mode == layer_mode_continuous:
                text_label = multiple_continuous_hazard_classifications_raster
            else:
                text_label = multiple_classified_hazard_classifications_raster
            # noinspection PyAugmentAssignment
            text_label = text_label % (
                subcategory['name'], self.layer_purpose['name'])
        else:
            if self.layer_mode == layer_mode_continuous:
                text_label = multiple_continuous_hazard_classifications_vector
            else:
                text_label = multiple_classified_hazard_classifications_vector
            # noinspection PyAugmentAssignment
            text_label = text_label % (
                subcategory['name'], self.layer_purpose['name'], field)

        self.multi_classifications_label.setText(text_label)

    def setup_left_panel(self):
        """Setup the UI for left panel.

        Generate all exposure, combobox, and edit button.
        """
        hazard = self.parent.step_kw_subcategory.selected_subcategory()
        left_panel_heading = QLabel(tr('Classifications'))
        left_panel_heading.setFont(big_font)
        self.left_layout.addWidget(left_panel_heading)

        inner_left_layout = QGridLayout()

        row = 0
        for exposure in exposure_all:
            special_case = False
            if not setting('developer_mode'):
                # Filter out unsupported exposure for the hazard
                if exposure in hazard['disabled_exposures']:
                    # Remove from the storage if the exposure is disabled
                    if self.layer_mode == layer_mode_continuous:
                        if exposure['key'] in self.thresholds:
                            self.thresholds.pop(exposure['key'])
                    else:
                        if exposure['key'] in self.value_maps:
                            self.value_maps.pop(exposure['key'])
                    continue
            # Trick for EQ raster for population #3853
            if exposure == exposure_population and hazard == hazard_earthquake:
                if is_raster_layer(self.parent.layer):
                    if self.layer_mode == layer_mode_continuous:
                        self.use_default_thresholds = True
                        special_case = True
                        # Set classification for EQ Raster for Population
                        self.thresholds[exposure_population['key']] = {
                            earthquake_mmi_scale['key']: {
                                'classes': default_classification_thresholds(
                                    earthquake_mmi_scale),
                                'active': True
                            }
                        }

            # Add label
            # Hazard on Exposure Classifications
            label = tr(
                '{hazard_name} on {exposure_name} Classifications').format(
                hazard_name=hazard['name'],
                exposure_name=exposure['name']
            )
            exposure_label = QLabel(label)

            # Add combo box
            exposure_combo_box = QComboBox()
            hazard_classifications = hazard.get('classifications')
            exposure_combo_box.addItem(tr('No classifications'))
            exposure_combo_box.setItemData(
                0, None, Qt.UserRole)

            current_index = 0
            i = 0
            # Iterate through all available hazard classifications
            for hazard_classification in hazard_classifications:
                # Skip if the classification is not for the exposure
                if 'exposures' in hazard_classification:
                    if exposure not in hazard_classification['exposures']:
                        continue
                exposure_combo_box.addItem(hazard_classification['name'])
                exposure_combo_box.setItemData(
                    i + 1, hazard_classification, Qt.UserRole)
                if self.layer_mode == layer_mode_continuous:
                    current_hazard_classifications = self.thresholds.get(
                        exposure['key'])
                else:
                    current_hazard_classifications = self.value_maps.get(
                        exposure['key'])
                if current_hazard_classifications:
                    current_hazard_classification = \
                        current_hazard_classifications.get(
                            hazard_classification['key'])
                    if current_hazard_classification:
                        is_active = current_hazard_classification.get('active')
                        if is_active:
                            current_index = i + 1
                i += 1
            # Set current classification
            exposure_combo_box.setCurrentIndex(current_index)

            # Add edit button
            exposure_edit_button = QPushButton(tr('Edit'))

            # For special case. Raster EQ on Population.
            if special_case:
                mmi_index = exposure_combo_box.findText(
                    earthquake_mmi_scale['name'])
                exposure_combo_box.setCurrentIndex(mmi_index)
                exposure_combo_box.setEnabled(False)
                exposure_edit_button.setEnabled(False)
                tool_tip_message = tr(
                    'InaSAFE use default classification for Raster Earthquake '
                    'hazard on population.')
                exposure_label.setToolTip(tool_tip_message)
                exposure_combo_box.setToolTip(tool_tip_message)
                exposure_edit_button.setToolTip(tool_tip_message)

            else:
                if current_index == 0:
                    # Disable if there is no classification chosen.
                    exposure_edit_button.setEnabled(False)
                exposure_edit_button.clicked.connect(
                    partial(
                        self.edit_button_clicked,
                        edit_button=exposure_edit_button,
                        exposure_combo_box=exposure_combo_box,
                        exposure=exposure))
                exposure_combo_box.currentIndexChanged.connect(
                    partial(
                        self.classifications_combo_box_changed,
                        exposure=exposure,
                        exposure_combo_box=exposure_combo_box,
                        edit_button=exposure_edit_button))

            # Arrange in layout
            inner_left_layout.addWidget(exposure_label, row, 0)
            inner_left_layout.addWidget(exposure_combo_box, row, 1)
            inner_left_layout.addWidget(exposure_edit_button, row, 2)

            # Adding to step's attribute
            self.exposures.append(exposure)
            self.exposure_combo_boxes.append(exposure_combo_box)
            self.exposure_edit_buttons.append(exposure_edit_button)
            self.exposure_labels.append(label)
            if special_case:
                self.special_case_index = len(self.exposures) - 1

            row += 1

        self.left_layout.addLayout(inner_left_layout)
        # To push the inner_left_layout up
        self.left_layout.addStretch(1)

    # noinspection PyUnusedLocal
    def edit_button_clicked(self, edit_button, exposure_combo_box, exposure):
        """Method to handle when an edit button is clicked.

        :param edit_button: The edit button.
        :type edit_button: QPushButton

        :param exposure_combo_box: The combo box of the exposure, contains
            list of classifications.
        :type exposure_combo_box: QComboBox

        :param exposure: Exposure definition.
        :type exposure: dict
        """
        # Note(IS): Do not change the text of edit button for now until we
        # have better behaviour.
        classification = self.get_classification(exposure_combo_box)

        if self.mode == CHOOSE_MODE:
            # Change mode
            self.mode = EDIT_MODE
            # Set active exposure
            self.active_exposure = exposure
            # Disable all edit button
            for exposure_edit_button in self.exposure_edit_buttons:
                exposure_edit_button.setEnabled(False)
            # Except one that was clicked
            # edit_button.setEnabled(True)
            # Disable all combo box
            for exposure_combo_box in self.exposure_combo_boxes:
                exposure_combo_box.setEnabled(False)
            # Change the edit button to cancel
            # edit_button.setText(tr('Cancel'))

            # Clear right panel
            clear_layout(self.right_layout)
            # Show edit threshold or value mapping
            if self.layer_mode == layer_mode_continuous:
                self.setup_thresholds_panel(classification)
            else:
                self.setup_value_mapping_panels(classification)
            self.add_buttons(classification)

        elif self.mode == EDIT_MODE:
            # Behave the same as cancel button clicked.
            self.cancel_button_clicked()

        self.parent.pbnNext.setEnabled(self.is_ready_to_next_step())

    def show_current_state(self):
        """Setup the UI for QTextEdit to show the current state."""
        right_panel_heading = QLabel(tr('Status'))
        right_panel_heading.setFont(big_font)
        right_panel_heading.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.right_layout.addWidget(right_panel_heading)

        message = m.Message()
        if self.layer_mode == layer_mode_continuous:
            title = tr('Thresholds')
        else:
            title = tr('Value maps')

        message.add(m.Heading(title, **INFO_STYLE))

        for i in range(len(self.exposures)):
            message.add(m.Text(self.exposure_labels[i]))

            classification = self.get_classification(
                self.exposure_combo_boxes[i])
            if self.layer_mode == layer_mode_continuous:
                thresholds = self.thresholds.get(self.exposures[i]['key'])
                if not thresholds or not classification:
                    message.add(m.Paragraph(tr('No classifications set.')))
                    continue
                table = m.Table(
                    style_class='table table-condensed table-striped')
                header = m.Row()
                header.add(m.Cell(tr('Class name')))
                header.add(m.Cell(tr('Minimum')))
                header.add(m.Cell(tr('Maximum')))
                table.add(header)
                classes = classification.get('classes')
                # Sort by value, put the lowest first
                classes = sorted(classes, key=lambda k: k['value'])
                for the_class in classes:
                    threshold = thresholds[classification['key']]['classes'][
                        the_class['key']]
                    row = m.Row()
                    row.add(m.Cell(the_class['name']))
                    row.add(m.Cell(threshold[0]))
                    row.add(m.Cell(threshold[1]))
                    table.add(row)
            else:
                value_maps = self.value_maps.get(self.exposures[i]['key'])
                if not value_maps or not classification:
                    message.add(m.Paragraph(tr('No classifications set.')))
                    continue
                table = m.Table(
                    style_class='table table-condensed table-striped')
                header = m.Row()
                header.add(m.Cell(tr('Class name')))
                header.add(m.Cell(tr('Value')))
                table.add(header)
                classes = classification.get('classes')
                # Sort by value, put the lowest first
                classes = sorted(classes, key=lambda k: k['value'])
                for the_class in classes:
                    value_map = value_maps[classification['key']][
                        'classes'].get(the_class['key'], [])
                    row = m.Row()
                    row.add(m.Cell(the_class['name']))
                    row.add(m.Cell(', '.join([str(v) for v in value_map])))
                    table.add(row)
            message.add(table)

        # status_text_edit = QTextBrowser(None)
        status_text_edit = QWebView(None)
        status_text_edit.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored)

        status_text_edit.page().mainFrame().setScrollBarPolicy(
            Qt.Horizontal,
            Qt.ScrollBarAlwaysOff)
        html_string = html_header() + message.to_html() + html_footer()
        status_text_edit.setHtml(html_string)
        self.right_layout.addWidget(status_text_edit)

    def set_widgets(self):
        """Set widgets on the Multi classification step."""
        self.clear()
        self.layer_mode = self.parent.step_kw_layermode.selected_layermode()
        self.layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        self.set_current_state()

        # Set the step description
        self.set_wizard_step_description()

        # Set the left panel
        self.setup_left_panel()

        # Set the right panel, for the beginning show the viewer
        self.show_current_state()

    def clear(self):
        """Clear current state."""
        self.exposures = []
        self.exposure_labels = []
        self.exposure_combo_boxes = []
        self.exposure_edit_buttons = []
        self.mode = CHOOSE_MODE

        self.layer_purpose = None
        self.layer_mode = None
        self.special_case_index = None

        self.value_maps = {}
        self.thresholds = {}

        # Temporary attributes
        self.threshold_classes = OrderedDict()
        self.active_exposure = None

        self.list_unique_values = None
        self.tree_mapping_widget = None

        clear_layout(self.left_layout)
        clear_layout(self.right_layout)

    def get_current_state(self):
        """Obtain current classification and value map / threshold."""
        def clean_state(dictionary):
            """Clean dictionary from bad value.

            :param dictionary: Dictionary of value maps or thresholds.
            :type dictionary: dict

            :returns: Clean state.
            :rtype: dict
            """
            clean_dictionary = {
                k: v for k, v in list(dictionary.items())
                if isinstance(v, dict)}

            return clean_dictionary

        if self.layer_mode == layer_mode_continuous:
            output = {'thresholds': clean_state(self.thresholds)}
            key = 'thresholds'
        else:
            output = {'value_maps': clean_state(self.value_maps)}
            key = 'value_maps'

        # Clean non existing hazard class key
        empty_exposure_classifications = []
        for the_exposure, the_hazard_classifications in list(
                output[key].items()):
            for the_hazard_classification in list(the_hazard_classifications.
                                                  keys()):
                invalid_classifications = []
                if not definition(the_hazard_classification):
                    invalid_classifications.append(
                        the_hazard_classification)
                for invalid_classification in invalid_classifications:
                    the_hazard_classifications.pop(invalid_classification)
            if not the_hazard_classifications:
                empty_exposure_classifications.append(the_exposure)

        for empty_exposure_classification in empty_exposure_classifications:
            output[key].pop(empty_exposure_classification)

        return output

    @staticmethod
    def get_classification(combo_box):
        """Helper to obtain the classification from a combo box.

        :param combo_box: A classification combo box.
        :type combo_box: QComboBox.

        :returns: Classification definitions.
        :rtype: dict
        """
        return combo_box.itemData(combo_box.currentIndex(), Qt.UserRole)

    def setup_thresholds_panel(self, classification):
        """Setup threshold panel in the right panel.

        :param classification: Classification definition.
        :type classification: dict
        """
        # Set text in the label
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()

        if is_raster_layer(self.parent.layer):
            active_band = self.parent.step_kw_band_selector.selected_band()
            layer_extent = self.parent.layer.extent()
            statistics = self.parent.layer.dataProvider().bandStatistics(
                active_band, QgsRasterBandStats.All, layer_extent, 0)
            description_text = continuous_raster_question % (
                layer_purpose['name'],
                layer_subcategory['name'],
                classification['name'],
                statistics.minimumValue,
                statistics.maximumValue)
        else:
            field_name = self.parent.step_kw_field.selected_fields()
            field_index = self.parent.layer.fields().lookupField(field_name)
            min_value_layer = self.parent.layer.minimumValue(field_index)
            max_value_layer = self.parent.layer.maximumValue(field_index)
            description_text = continuous_vector_question % (
                layer_purpose['name'],
                layer_subcategory['name'],
                field_name,
                classification['name'],
                min_value_layer,
                max_value_layer)

        # Set description
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        self.right_layout.addWidget(description_label)

        if self.thresholds:
            thresholds = self.thresholds
        else:
            thresholds = self.parent.get_existing_keyword('thresholds')
        selected_unit = self.parent.step_kw_unit.selected_unit()['key']

        self.threshold_classes = OrderedDict()
        classes = classification.get('classes')
        # Sort by value, put the lowest first
        classes = sorted(classes, key=lambda the_key: the_key['value'])

        grid_layout_thresholds = QGridLayout()

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

            if thresholds.get(self.active_exposure['key']):
                exposure_thresholds = thresholds.get(
                    self.active_exposure['key'])
                if exposure_thresholds.get(classification['key']):
                    exposure_thresholds_classifications = exposure_thresholds\
                        .get(classification['key'])
                    min_value_input.setValue(
                        exposure_thresholds_classifications['classes'][
                            the_class['key']][0])
                else:
                    default_min = the_class['numeric_default_min']
                    if isinstance(default_min, dict):
                        default_min = the_class[
                            'numeric_default_min'][selected_unit]
                    min_value_input.setValue(default_min)
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
            if thresholds.get(self.active_exposure['key']):
                exposure_thresholds = thresholds.get(
                    self.active_exposure['key'])
                if exposure_thresholds.get(classification['key']):
                    exposure_thresholds_classifications = exposure_thresholds \
                        .get(classification['key'])
                    max_value_input.setValue(
                        exposure_thresholds_classifications['classes'][
                            the_class['key']][1])
                else:
                    default_max = the_class['numeric_default_max']
                    if isinstance(default_max, dict):
                        default_max = the_class[
                            'numeric_default_max'][selected_unit]
                    max_value_input.setValue(default_max)
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
            class_layout.addWidget(max_label)
            class_layout.addWidget(max_value_input)

            class_layout.setStretch(0, 1)
            class_layout.setStretch(1, 2)
            class_layout.setStretch(2, 1)
            class_layout.setStretch(3, 2)

            # Add to grid_layout
            grid_layout_thresholds.addWidget(class_label, i, 0)
            grid_layout_thresholds.addLayout(class_layout, i, 1)

            self.threshold_classes[the_class['key']] = [
                min_value_input, max_value_input]

        grid_layout_thresholds.setColumnStretch(0, 1)
        grid_layout_thresholds.setColumnStretch(0, 2)

        def min_max_changed(double_spin_index, mode):
            """Slot when min or max value change.

            :param double_spin_index: The index of the double spin.
            :type double_spin_index: int

            :param mode: The flag to indicate the min or max value.
            :type mode: int
            """
            if mode == MAX_VALUE_MODE:
                current_max_value = list(self.threshold_classes.values())[
                    double_spin_index][1]
                target_min_value = list(self.threshold_classes.values())[
                    double_spin_index + 1][0]
                if current_max_value.value() != target_min_value.value():
                    target_min_value.setValue(current_max_value.value())
            elif mode == MIN_VALUE_MODE:
                current_min_value = list(self.threshold_classes.values())[
                    double_spin_index][0]
                target_max_value = list(self.threshold_classes.values())[
                    double_spin_index - 1][1]
                if current_min_value.value() != target_max_value.value():
                    target_max_value.setValue(current_min_value.value())

        # Set behaviour
        for k, v in list(self.threshold_classes.items()):
            index = list(self.threshold_classes.keys()).index(k)
            if index < len(self.threshold_classes) - 1:
                # Max value changed
                v[1].valueChanged.connect(partial(
                    min_max_changed,
                    double_spin_index=index,
                    mode=MAX_VALUE_MODE))
            if index > 0:
                # Min value
                v[0].valueChanged.connect(partial(
                    min_max_changed,
                    double_spin_index=index,
                    mode=MIN_VALUE_MODE))

        grid_layout_thresholds.setSpacing(0)

        self.right_layout.addLayout(grid_layout_thresholds)

    def add_buttons(self, classification):
        """Helper to setup 3 buttons.

        :param classification: The current classification.
        :type classification: dict
        """
        # Note(IS): Until we have good behaviour, we will disable cancel
        # button.
        # Add 3 buttons: Restore default, Cancel, Save

        # Restore default button, only for continuous layer (with threshold)
        if self.layer_mode == layer_mode_continuous['key']:
            self.restore_default_button = QPushButton(tr('Restore Default'))
            self.restore_default_button.clicked.connect(partial(
                self.restore_default_button_clicked,
                classification=classification))

        # Cancel button
        # cancel_button = QPushButton(tr('Cancel'))
        # cancel_button.clicked.connect(self.cancel_button_clicked)

        # Save button
        self.save_button = QPushButton(tr('Save'))
        self.save_button.clicked.connect(
            partial(self.save_button_clicked, classification=classification))

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.restore_default_button)
        button_layout.addWidget(self.save_button)

        button_layout.setStretch(0, 3)
        button_layout.setStretch(1, 1)
        button_layout.setStretch(2, 1)
        # button_layout.setStretch(3, 1)

        self.right_layout.addLayout(button_layout)

    def setup_value_mapping_panels(self, classification):
        """Setup value mapping panel in the right panel.

        :param classification: Classification definition.
        :type classification: dict
        """
        # Set text in the label
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_subcategory = self.parent.step_kw_subcategory. \
            selected_subcategory()

        if is_raster_layer(self.parent.layer):
            description_text = classify_raster_question % (
                layer_subcategory['name'],
                layer_purpose['name'],
                classification['name'])

            dataset = gdal.Open(self.parent.layer.source(), GA_ReadOnly)
            active_band = self.parent.step_kw_band_selector.selected_band()
            unique_values = numpy.unique(numpy.array(
                dataset.GetRasterBand(active_band).ReadAsArray()))
            field_type = 0
            # Convert datatype to a json serializable type
            if numpy.issubdtype(unique_values.dtype, float):
                unique_values = [float(i) for i in unique_values]
            else:
                unique_values = [int(i) for i in unique_values]
        else:
            field = self.parent.step_kw_field.selected_fields()
            field_index = self.parent.layer.fields().indexFromName(field)
            field_type = self.parent.layer.fields()[field_index].type()
            description_text = classify_vector_question % (
                layer_subcategory['name'],
                layer_purpose['name'],
                classification['name'],
                field.upper())
            unique_values = self.parent.layer.uniqueValues(field_index)

        # Set description
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        self.right_layout.addWidget(description_label)

        self.list_unique_values = QListWidget()
        self.list_unique_values.setDragDropMode(QAbstractItemView.DragDrop)
        self.list_unique_values.setDefaultDropAction(Qt.MoveAction)

        self.tree_mapping_widget = QTreeWidget()
        self.tree_mapping_widget.setDragDropMode(QAbstractItemView.DragDrop)
        self.tree_mapping_widget.setDefaultDropAction(Qt.MoveAction)
        self.tree_mapping_widget.header().hide()

        self.tree_mapping_widget.itemChanged.connect(
            self.update_dragged_item_flags)

        value_mapping_layout = QHBoxLayout()
        value_mapping_layout.addWidget(self.list_unique_values)
        value_mapping_layout.addWidget(self.tree_mapping_widget)

        self.right_layout.addLayout(value_mapping_layout)

        default_classes = classification['classes']

        # Assign unique values to classes (according to default)
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['key']] = list()
        for unique_value in unique_values:
            if unique_value is None:
                # Don't classify features with NULL value
                continue
            # Capitalization of the value and removing '_' (raw OSM data).
            value_as_string = str(unique_value).upper().replace('_', ' ')
            assigned = False
            for default_class in default_classes:
                if 'string_defaults' in default_class:
                    # To make it case insensitive
                    upper_string_defaults = [
                        c.upper() for c in default_class['string_defaults']]
                    in_string_default = (
                        value_as_string in upper_string_defaults)
                    condition_1 = field_type > 9 and in_string_default
                else:
                    condition_1 = False
                condition_2 = (
                    field_type < 10 and
                    'numeric_default_min' in default_class and
                    'numeric_default_max' in default_class and (
                        default_class['numeric_default_min'] <= unique_value <
                        default_class['numeric_default_max']))
                if condition_1 or condition_2:
                    assigned_values[default_class['key']] += [unique_value]
                    assigned = True
                    break
            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [unique_value]
        self.populate_classified_values(
            unassigned_values,
            assigned_values,
            default_classes,
            self.list_unique_values,
            self.tree_mapping_widget
        )

        # Current value map for exposure and classification
        available_classifications = self.value_maps.get(
            self.active_exposure['key'])
        if not available_classifications:
            return
        # Get active one
        current_classification = available_classifications.get(
            classification['key'])
        if not current_classification:
            return
        # Should come from metadata
        current_value_map = current_classification.get('classes')
        if not current_value_map:
            return

        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['key']] = list()
        for unique_value in unique_values:
            if unique_value is None:
                # Don't classify features with NULL value
                continue
            # check in value map
            assigned = False
            for key, value_list in list(current_value_map.items()):
                if unique_value in value_list and key in assigned_values:
                    assigned_values[key] += [unique_value]
                    assigned = True
            if not assigned:
                unassigned_values += [unique_value]
        self.populate_classified_values(
            unassigned_values,
            assigned_values,
            default_classes,
            self.list_unique_values,
            self.tree_mapping_widget
        )

    # noinspection PyMethodMayBeStatic
    def update_dragged_item_flags(self, item):
        """Fix the drop flag after the item is dropped.

        Check if it looks like an item dragged from QListWidget
        to QTreeWidget and disable the drop flag.
        For some reasons the flag is set when dragging.

        :param item: Item which is dragged.
        :type item: QTreeWidgetItem

        .. note:: This is a slot executed when the item change.
        """
        if int(item.flags() & Qt.ItemIsDropEnabled) \
                and int(item.flags() & Qt.ItemIsDragEnabled):
            item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

    @staticmethod
    def populate_classified_values(
            unassigned_values, assigned_values, default_classes,
            list_unique_values, tree_mapping_widget):
        """Populate lstUniqueValues and treeClasses.from the parameters.

        :param unassigned_values: List of values that haven't been assigned
            to a class. It will be put in list_unique_values.
        :type unassigned_values: list

        :param assigned_values: Dictionary with class as the key and list of
            value as the value of the dictionary. It will be put in
            tree_mapping_widget.
        :type assigned_values: dict

        :param default_classes: Default classes from unit.
        :type default_classes: list

        :param list_unique_values: List Widget for unique values
        :type list_unique_values: QListWidget

        :param tree_mapping_widget: Tree Widget for classifying.
        :type tree_mapping_widget: QTreeWidget
        """
        # Populate the unique values list
        list_unique_values.clear()
        list_unique_values.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        for value in unassigned_values:
            value_as_string = value is not None and str(value) or 'NULL'
            list_item = QListWidgetItem(list_unique_values)
            list_item.setFlags(
                Qt.ItemIsEnabled |
                Qt.ItemIsSelectable |
                Qt.ItemIsDragEnabled)
            list_item.setData(Qt.UserRole, value)
            list_item.setText(value_as_string)
            list_unique_values.addItem(list_item)
        # Populate assigned values tree
        tree_mapping_widget.clear()
        bold_font = QFont()
        bold_font.setItalic(True)
        bold_font.setBold(True)
        bold_font.setWeight(75)
        tree_mapping_widget.invisibleRootItem().setFlags(
            Qt.ItemIsEnabled)
        for default_class in default_classes:
            # Create branch for class
            tree_branch = QTreeWidgetItem(tree_mapping_widget)
            tree_branch.setFlags(
                Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
            tree_branch.setExpanded(True)
            tree_branch.setFont(0, bold_font)
            if 'name' in default_class:
                default_class_name = default_class['name']
            else:
                default_class_name = default_class['key']
            tree_branch.setText(0, default_class_name)
            tree_branch.setData(0, Qt.UserRole, default_class['key'])
            if 'description' in default_class:
                tree_branch.setToolTip(0, default_class['description'])
            # Assign known values
            for value in assigned_values[default_class['key']]:
                string_value = value is not None and str(value) or 'NULL'
                tree_leaf = QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(
                    Qt.ItemIsEnabled |
                    Qt.ItemIsSelectable |
                    Qt.ItemIsDragEnabled)
                tree_leaf.setData(0, Qt.UserRole, value)
                tree_leaf.setText(0, string_value)

    def cancel_button_clicked(self):
        """Action for cancel button clicked."""
        # Change mode
        self.mode = CHOOSE_MODE
        # Enable all edit buttons and combo boxes
        for i in range(len(self.exposures)):
            if i == self.special_case_index:
                self.exposure_edit_buttons[i].setEnabled(False)
                self.exposure_combo_boxes[i].setEnabled(False)
                continue
            if self.get_classification(self.exposure_combo_boxes[i]):
                self.exposure_edit_buttons[i].setEnabled(True)
            else:
                self.exposure_edit_buttons[i].setEnabled(False)
            # self.exposure_edit_buttons[i].setText(tr('Edit'))
            self.exposure_combo_boxes[i].setEnabled(True)

        # Clear right panel
        clear_layout(self.right_layout)
        # Show current state
        self.show_current_state()
        # Unset active exposure
        self.active_exposure = None

        self.parent.pbnNext.setEnabled(self.is_ready_to_next_step())

    def save_button_clicked(self, classification):
        """Action for save button clicked.

        :param classification: The classification that being edited.
        :type classification: dict
        """
        # Save current edit
        if self.layer_mode == layer_mode_continuous:
            thresholds = self.get_threshold()
            classification_class = {
                'classes': thresholds,
                'active': True
            }
            if self.thresholds.get(self.active_exposure['key']):
                # Set other class to not active
                for current_classification in list(self.thresholds.get(
                        self.active_exposure['key']).values()):
                    current_classification['active'] = False
            else:
                self.thresholds[self.active_exposure['key']] = {}

            self.thresholds[self.active_exposure['key']][
                classification['key']] = classification_class
        else:
            value_maps = self.get_value_map()
            classification_class = {
                'classes': value_maps,
                'active': True
            }
            if self.value_maps.get(self.active_exposure['key']):
                # Set other class to not active
                for current_classification in list(self.value_maps.get(
                        self.active_exposure['key']).values()):
                    current_classification['active'] = False
            else:
                self.value_maps[self.active_exposure['key']] = {}

            self.value_maps[self.active_exposure['key']][
                classification['key']] = classification_class
        # Back to choose mode
        self.cancel_button_clicked()

    def restore_default_button_clicked(self, classification):
        """Action for restore default button clicked.

        It will set the threshold with default value.

        :param classification: The classification that being edited.
        :type classification: dict
        """
        # Obtain default value
        class_dict = {}
        for the_class in classification.get('classes'):
            class_dict[the_class['key']] = {
                'numeric_default_min': the_class['numeric_default_min'],
                'numeric_default_max': the_class['numeric_default_max'],
            }
        # Set for all threshold
        for key, value in list(self.threshold_classes.items()):
            value[0].setValue(class_dict[key]['numeric_default_min'])
            value[1].setValue(class_dict[key]['numeric_default_max'])

    def get_threshold(self):
        """Return threshold based on current state."""
        value_map = dict()
        for key, value in list(self.threshold_classes.items()):
            value_map[key] = [
                value[0].value(),
                value[1].value(),
            ]
        return value_map

    def get_value_map(self):
        """Obtain the value-to-class mapping set by user.

        :returns: The complete mapping as a dict of lists.
        :rtype: dict
        """
        value_map = {}
        tree_clone = self.tree_mapping_widget.invisibleRootItem().clone()
        for tree_branch in tree_clone.takeChildren():
            value_list = []
            for tree_leaf in tree_branch.takeChildren():
                value_list += [tree_leaf.data(0, Qt.UserRole)]
            if value_list:
                value_map[tree_branch.data(0, Qt.UserRole)] = value_list
        return value_map

    def set_current_state(self):
        """"Helper to set the state of the step from current keywords."""
        if not self.thresholds:
            self.thresholds = self.parent.get_existing_keyword('thresholds')
        if not self.value_maps:
            self.value_maps = self.parent.get_existing_keyword('value_maps')

    def classifications_combo_box_changed(
            self, index, exposure, exposure_combo_box, edit_button):
        """Action when classification combo box changed.

        :param index: The index of the combo box.
        :type index: int

        :param exposure: The exposure associated with the combo box.
        :type exposure: dict

        :param exposure_combo_box: Combo box for the classification.
        :type exposure_combo_box: QComboBox

        :param edit_button: The edit button associate with combo box.
        :type edit_button: QPushButton
        """
        # Disable button if it's no classification
        edit_button.setEnabled(bool(index))

        classification = self.get_classification(exposure_combo_box)
        self.activate_classification(exposure, classification)
        clear_layout(self.right_layout)
        self.show_current_state()

        self.parent.pbnNext.setEnabled(self.is_ready_to_next_step())

        # Open edit panel directly
        edit_button.click()

    def activate_classification(self, exposure, classification=None):
        """Set active to True for classification for the exposure.

        If classification = None, all classification set active = False.

        :param exposure: Exposure definition.
        :type exposure: dict

        :param classification: Classification definition.
        :type classification: dict
        """
        if self.layer_mode == layer_mode_continuous:
            selected_unit = self.parent.step_kw_unit.selected_unit()['key']
            target = self.thresholds.get(exposure['key'])
            if target is None:
                self.thresholds[exposure['key']] = {}
            target = self.thresholds.get(exposure['key'])
        else:
            selected_unit = None
            target = self.value_maps.get(exposure['key'])
            if target is None:
                self.value_maps[exposure['key']] = {}
            target = self.value_maps.get(exposure['key'])

        if classification is not None:
            if classification['key'] not in target:
                if self.layer_mode == layer_mode_continuous:
                    default_classes = default_classification_thresholds(
                        classification, selected_unit)
                    target[classification['key']] = {
                        'classes': default_classes,
                        'active': True
                    }
                else:
                    # Set classes to empty, since we haven't mapped anything
                    target[classification['key']] = {
                        'classes': {},
                        'active': True
                    }
                return

        for classification_key, value in list(target.items()):
            if classification is None:
                value['active'] = False
                continue

            if classification_key == classification['key']:
                value['active'] = True
            else:
                value['active'] = False

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Multi Classification Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'classification that you will use per exposure type. You can also '
            'set the threshold or value map for each classification.'
        ).format(step_name=self.step_name)))
        return message
