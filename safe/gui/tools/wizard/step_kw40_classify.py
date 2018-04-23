# coding=utf-8
"""InaSAFE Wizard Step Value Mapping."""


import json
from copy import deepcopy

import numpy
from qgis.PyQt.QtWidgets import QListWidgetItem, QAbstractItemView, QTreeWidgetItem
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly

from safe import messaging as m
from safe.definitions.exposure_classifications import data_driven_classes
from safe.definitions.font import bold_font
from safe.definitions.layer_geometry import layer_geometry_raster
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.definitions.utilities import get_fields, get_compulsory_fields
from safe.gui.tools.wizard.utilities import skip_inasafe_field
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    classify_raster_question, classify_vector_question)
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwClassify(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Value Mapping."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.treeClasses.itemChanged.connect(self.update_dragged_item_flags)

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
        :rtype: WizardStep
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

        # Get all fields with replace_null = False
        inasafe_fields = get_fields(
            layer_purpose['key'],
            subcategory['key'],
            replace_null=False,
            in_group=False
        )
        # remove compulsory field since it has been set in previous step
        try:
            inasafe_fields.remove(get_compulsory_fields(
                layer_purpose['key'], subcategory['key']))
        except ValueError:
            pass

        # Check if possible to skip inasafe field step
        if skip_inasafe_field(self.parent.layer, inasafe_fields):
            default_inasafe_fields = get_fields(
                layer_purpose['key'],
                subcategory['key'],
                replace_null=True,
                in_group=False
            )
            # Check if it can go to inasafe default step
            if default_inasafe_fields:
                return self.parent.step_kw_default_inasafe_fields
            # Else, go to source step
            else:
                return self.parent.step_kw_source

        # If not possible to skip inasafe field step, then go there
        else:
            return self.parent.step_kw_inasafe_fields

    # noinspection PyMethodMayBeStatic
    def update_dragged_item_flags(self, item, column):
        """Fix the drop flag after the item is dropped.

        Check if it looks like an item dragged from QListWidget
        to QTreeWidget and disable the drop flag.
        For some reasons the flag is set when dragging.

        :param item:
        :param column:

        .. note:: This is a slot executed when the item change.
        """
        _ = column  # NOQA

        if int(item.flags() & Qt.ItemIsDropEnabled) \
                and int(item.flags() & Qt.ItemIsDragEnabled):
            item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

    def selected_mapping(self):
        """Obtain the value-to-class mapping set by user.

        :returns: The complete mapping as a dict of lists.
        :rtype: dict
        """
        value_map = {}
        tree_clone = self.treeClasses.invisibleRootItem().clone()
        for tree_branch in tree_clone.takeChildren():
            value_list = []
            for tree_leaf in tree_branch.takeChildren():
                value_list += [tree_leaf.data(0, Qt.UserRole)]
            if value_list:
                value_map[tree_branch.data(0, Qt.UserRole)] = value_list
        return value_map

    def set_widgets(self):
        """Set widgets on the Classify tab."""
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()

        classification = self.parent.step_kw_classification.\
            selected_classification()
        classification_name = classification['name']

        if is_raster_layer(self.parent.layer):
            self.lblClassify.setText(classify_raster_question % (
                subcategory['name'], purpose['name'], classification_name))
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
            self.lblClassify.setText(classify_vector_question % (
                subcategory['name'], purpose['name'],
                classification_name, field.upper()))
            unique_values = self.parent.layer.uniqueValues(field_index)

        clean_unique_values = []
        for unique_value in unique_values:
            if unique_value is None:
                # Don't classify features with NULL value
                continue
            clean_unique_values.append(unique_value)

        # get default classes
        default_classes = deepcopy(classification['classes'])
        if classification['key'] == data_driven_classes['key']:
            for unique_value in clean_unique_values:
                name = str(unique_value).upper().replace('_', ' ')
                default_class = {'key': unique_value,
                                 'name': name,
                                 # 'description': tr('Settlement'),
                                 'string_defaults': [name]}

                default_classes.append(default_class)

        # Assign unique values to classes (according to default)
        unassigned_values = list()
        assigned_values = dict()

        for default_class in default_classes:
            assigned_values[default_class['key']] = list()
        for unique_value in clean_unique_values:
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
                        default_class['numeric_default_min'] <= unique_value <=
                        default_class['numeric_default_max']))
                if condition_1 or condition_2:
                    assigned_values[default_class['key']] += [unique_value]
                    assigned = True

            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [unique_value]

        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

        # Overwrite assigned values according to existing keyword (if present).
        # Note the default_classes and unique_values are already loaded!

        value_map = self.parent.get_existing_keyword('value_map')
        value_map_classification_name = self.parent.get_existing_keyword(
            'classification')
        # Do not continue if there is no value_map in existing keywords
        if (value_map is None or
                value_map_classification_name != classification['key']):
            return

        # Do not continue if user selected different field
        field_keyword = self.parent.field_keyword_for_the_layer()
        field = self.parent.get_existing_keyword('inasafe_fields').get(
            field_keyword)
        if (not is_raster_layer(self.parent.layer) and
                field != self.parent.step_kw_field.selected_fields()):
            return

        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['key']] = list()
        if isinstance(value_map, str):
            try:
                value_map = json.loads(value_map)
            except ValueError:
                return

        for unique_value in clean_unique_values:
            # check in value map
            assigned = False
            for key, value_list in list(value_map.items()):
                if unique_value in value_list and key in assigned_values:
                    assigned_values[key] += [unique_value]
                    assigned = True
            if not assigned:
                unassigned_values += [unique_value]
        self.populate_classified_values(
           unassigned_values, assigned_values, default_classes)

    def populate_classified_values(
            self, unassigned_values, assigned_values, default_classes):
        """Populate lstUniqueValues and treeClasses.from the parameters.

        :param unassigned_values: List of values that haven't been assigned
            to a class. It will be put in self.lstUniqueValues.
        :type unassigned_values: list

        :param assigned_values: Dictionary with class as the key and list of
            value as the value of the dictionary. It will be put in
            self.treeClasses.
        :type assigned_values: dict

        :param default_classes: Default classes from unit.
        :type default_classes: list
        """
        # Populate the unique values list
        self.lstUniqueValues.clear()
        self.lstUniqueValues.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        for value in unassigned_values:
            value_as_string = value is not None and str(value) or 'NULL'
            list_item = QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(
                Qt.ItemIsEnabled |
                Qt.ItemIsSelectable |
                Qt.ItemIsDragEnabled)
            list_item.setData(Qt.UserRole, value)
            list_item.setText(value_as_string)
            self.lstUniqueValues.addItem(list_item)
        # Populate assigned values tree
        self.treeClasses.clear()
        self.treeClasses.invisibleRootItem().setFlags(Qt.ItemIsEnabled)
        for default_class in default_classes:
            # Create branch for class
            tree_branch = QTreeWidgetItem(self.treeClasses)
            tree_branch.setFlags(Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
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

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Value Mapping Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to map the '
            'value in the field (in the left panel) to a group in the right '
            'panel. You can do this by drag the value and drop it to the '
            'preferred group.').format(step_name=self.step_name)))
        return message
