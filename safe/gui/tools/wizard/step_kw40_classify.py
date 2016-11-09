# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Classify (Value Mapping)

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import json

import numpy
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QPyNullVariant
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly

from safe.definitionsv4.layer_purposes import layer_purpose_aggregation
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.definitionsv4.utilities import get_fields
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    classify_raster_question, classify_vector_question)
from safe.utilities.gis import is_raster_layer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwClassify(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Classify (Value Mapping)"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
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

        # Treat var as unused
        _ = column

        if int(item.flags() & QtCore.Qt.ItemIsDropEnabled) \
                and int(item.flags() & QtCore.Qt.ItemIsDragEnabled):
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)

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
                value_list += [tree_leaf.data(0, QtCore.Qt.UserRole)]
            if value_list:
                value_map[tree_branch.data(0, QtCore.Qt.UserRole)] = value_list
        return value_map

    def set_widgets(self):
        """Set widgets on the Classify tab."""
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()

        sel_cl = self.parent.step_kw_classification.selected_classification()
        default_classes = sel_cl['classes']
        classification_name = sel_cl['name']

        if is_raster_layer(self.parent.layer):
            self.lblClassify.setText(classify_raster_question % (
                subcategory['name'], purpose['name'], classification_name))
            dataset = gdal.Open(self.parent.layer.source(), GA_ReadOnly)
            unique_values = numpy.unique(numpy.array(
                dataset.GetRasterBand(1).ReadAsArray()))
            field_type = 0
            # Convert datatype to a json serializable type
            if numpy.issubdtype(unique_values.dtype, float):
                unique_values = [float(i) for i in unique_values]
            else:
                unique_values = [int(i) for i in unique_values]
        else:
            field = self.parent.step_kw_field.selected_field()
            field_index = self.parent.layer.dataProvider().fields().\
                indexFromName(field)
            field_type = self.parent.layer.dataProvider().\
                fields()[field_index].type()
            self.lblClassify.setText(classify_vector_question % (
                    subcategory['name'], purpose['name'],
                    classification_name, field.upper()))
            unique_values = self.parent.layer.uniqueValues(field_index)

        # Assign unique values to classes (according to default)
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['key']] = list()
        for unique_value in unique_values:
            if unique_value is None or isinstance(
                    unique_value, QPyNullVariant):
                # Don't classify features with NULL value
                continue
            # Capitalization of the value and removing '_' (raw OSM data).
            value_as_string = unicode(unique_value).upper().replace('_', ' ')
            assigned = False
            for default_class in default_classes:
                if 'string_defaults' in default_class:
                    condition_1 = (
                        field_type > 9 and
                        value_as_string in [
                            c.upper() for c in
                            default_class['string_defaults']])
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
        # Do not continue if there is no value_map in existing keywords
        if value_map is None:
            return

        # Do not continue if user selected different field
        field_keyword = self.parent.field_keyword_for_the_layer()
        field = self.parent.get_existing_keyword('inasafe_fields').get(
            field_keyword)
        if (not is_raster_layer(self.parent.layer) and
                field != self.parent.step_kw_field.selected_field()):
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
        for unique_value in unique_values:
            if unique_value is None or isinstance(
                    unique_value, QPyNullVariant):
                # Don't classify features with NULL value
                continue
            # check in value map
            assigned = False
            for key, value_list in value_map.iteritems():
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
            QtGui.QAbstractItemView.ExtendedSelection)
        for value in unassigned_values:
            value_as_string = value is not None and unicode(value) or 'NULL'
            list_item = QtGui.QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsDragEnabled)
            list_item.setData(QtCore.Qt.UserRole, value)
            list_item.setText(value_as_string)
            self.lstUniqueValues.addItem(list_item)
        # Populate assigned values tree
        self.treeClasses.clear()
        bold_font = QtGui.QFont()
        bold_font.setItalic(True)
        bold_font.setBold(True)
        bold_font.setWeight(75)
        self.treeClasses.invisibleRootItem().setFlags(
            QtCore.Qt.ItemIsEnabled)
        for default_class in default_classes:
            # Create branch for class
            tree_branch = QtGui.QTreeWidgetItem(self.treeClasses)
            tree_branch.setFlags(
                QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEnabled)
            tree_branch.setExpanded(True)
            tree_branch.setFont(0, bold_font)
            if 'name' in default_class:
                default_class_name = default_class['name']
            else:
                default_class_name = default_class['key']
            tree_branch.setText(0, default_class_name)
            tree_branch.setData(0, QtCore.Qt.UserRole, default_class['key'])
            if 'description' in default_class:
                tree_branch.setToolTip(0, default_class['description'])
            # Assign known values
            for value in assigned_values[default_class['key']]:
                string_value = value is not None and unicode(value) or 'NULL'
                tree_leaf = QtGui.QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsDragEnabled)
                tree_leaf.setData(0, QtCore.Qt.UserRole, value)
                tree_leaf.setText(0, string_value)
