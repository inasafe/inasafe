# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
import re
import json
from sqlite3 import OperationalError
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature
# noinspection PyPackageRequirements
from PyQt4.QtGui import QListWidgetItem, QPixmap, QApplication

from safe.api import ImpactFunctionManager
from safe.api import metadata  # pylint: disable=W0612

from safe_qgis.safe_interface import InaSAFEError, DEFAULTS
from safe_qgis.ui.wizard_dialog_base import Ui_WizardDialogBase
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_point_layer,
    is_polygon_layer,
    is_raster_layer,
    layer_attribute_names)
from safe_qgis.utilities.defaults import breakdown_defaults
from safe_qgis.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    UnsupportedProviderError)
from safe_qgis.utilities.help import show_context_help


LOGGER = logging.getLogger('InaSAFE')


# Constants for categories
category_question = QApplication.translate(
    'WizardDialog',
    'By following the simple steps in this wizard, you can assign '
    'keywords to your layer: <b>%s</b>. First you need to define '
    'the category of your layer.')   # (layer name)

# Constants for hazards
hazard_question = QApplication.translate(
    'WizardDialog',
    'What kind of hazard does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this hazard layer can be used with. '
    'For example, if you choose <b>flood</b> you will be '
    'able to use this hazard layer with impact functions such '
    'as <b>flood impact on population</b>.')

# Constants for exposures
exposure_question = QApplication.translate(
    'WizardDialog',
    'What kind of exposure does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this exposure layer can be used with. '
    'For example, if you choose <b>population</b> you will be '
    'able to use this exposure layer with impact functions such '
    'as <b>flood impact on population</b>.')

# Constants for units
unit_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s</b> '
    'for this <b>%s</b> layer type. We need to know what units the '
    'data are in. For example in a raster layer, each cell might '
    'represent depth in metres or depth in feet. If the dataset '
    'is a vector layer, each polygon might represent an inundated '
    'area, while areas with no polygon coverage would be assumed '
    'to be dry.')   # (subcategory, category)

# Constants for subcategory-unit relations
# These texts below will be inserted as the fourth variable
# to the field_question_subcategory_unit constant.
flood_metres_depth_question = QApplication.translate(
    'WizardDialog',
    'flood depth in meters')
flood_feet_depth_question = QApplication.translate(
    'WizardDialog',
    'flood depth in feet')
flood_wetdry_question = QApplication.translate(
    'WizardDialog',
    'flood extent as wet/dry')
tsunami_metres_depth_question = QApplication.translate(
    'WizardDialog',
    'tsunami depth in meters')
tsunami_feet_depth_question = QApplication.translate(
    'WizardDialog',
    'tsunami depth in feet')
tsunami_wetdry_question = QApplication.translate(
    'WizardDialog',
    'tsunami extent as wet/dry')
earthquake_mmi_question = QApplication.translate(
    'WizardDialog',
    'earthquake intensity in MMI')
tephra_kgm2_question = QApplication.translate(
    'WizardDialog',
    'tephra intensity in kg/m<sup>2</sup>')
volcano_volcano_categorical_question = QApplication.translate(
    'WizardDialog',
    'volcano hazard categorical level')
population_number_question = QApplication.translate(
    'WizardDialog',
    'the number of people')
population_density_question = QApplication.translate(
    'WizardDialog',
    'people density in people/km<sup>2</sup>')
road_road_type_question = QApplication.translate(
    'WizardDialog',
    'type for your road')
structure_building_type_question = QApplication.translate(
    'WizardDialog',
    'type for your building')

# Constants for field selection
field_question_subcategory_unit = QApplication.translate(
    'WizardDialog',
    'You have selected a <b>%s %s</b> layer measured in '
    '<b>%s</b>, and the selected layer is a vector layer. Please '
    'select the attribute in this layer that represents %s.')
    # (category, subcategory, unit, subcategory-unit relation))

field_question_aggregation = QApplication.translate(
    'WizardDialog',
    'You have selected an aggregation layer, and it is a vector '
    'layer. Please select the attribute in this layer that represents '
    'names of the aggregation areas.')

# Constants for classify values for categorized units
classify_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s %s</b> measured in <b>%s</b> categorical '
    'unit, and the data column is <b>%s</b>. Below on the left you '
    'can see all unique values found in that column. Please drag them '
    'to the right panel in order to classify them to appropriate '
    'categories.')   # (subcategory, category, unit, field)

# Constants: tab numbers for steps
step_category = 1
step_subcategory = 2
step_unit = 3
step_field = 4
step_classify = 5
step_aggregation = 6
step_source = 7
step_title = 8


# Aggregations' keywords
female_ratio_attribute_key = DEFAULTS['FEMALE_RATIO_ATTR_KEY']
female_ratio_default_key = DEFAULTS['FEMALE_RATIO_KEY']
youth_ratio_attribute_key = DEFAULTS['YOUTH_RATIO_ATTR_KEY']
youth_ratio_default_key = DEFAULTS['YOUTH_RATIO_KEY']
adult_ratio_attribute_key = DEFAULTS['ADULT_RATIO_ATTR_KEY']
adult_ratio_default_key = DEFAULTS['ADULT_RATIO_KEY']
elderly_ratio_attribute_key = DEFAULTS['ELDERLY_RATIO_ATTR_KEY']
elderly_ratio_default_key = DEFAULTS['ELDERLY_RATIO_KEY']


def get_question_text(constant):
    """Find a constant by name and return its value.

    :param constant: The name of the constant to look for.
    :type constant: string

    :returns: The value of the constant or red error message.
    :rtype: string
    """
    try:
        return eval(constant)
    except NameError:
        return '<b>MISSING CONSTANT: %s</b>' % constant


class WizardDialog(QtGui.QDialog, Ui_WizardDialogBase):

    """Dialog implementation class for the InaSAFE keywords wizard."""

    def __init__(self, parent=None, iface=None, dock=None, layer=None):
        """Constructor for the dialog.

        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: QGIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param dock: Dock widget instance that we can notify of changes to
            the keywords. Optional.
        :type dock: Dock
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('InaSAFE')
        # Note the keys should remain untranslated as we need to write
        # english to the keywords file.
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.suppress_warning_dialog = False
        self.keyword_io = KeywordIO()
        self.layer = layer or self.iface.mapCanvas().currentLayer()
        self.layer_type = is_raster_layer(self.layer) and 'raster' or 'vector'
        if self.layer_type == 'vector':
            if is_point_layer(self.layer):
                self.data_type = 'point'
            elif is_polygon_layer(self.layer):
                self.data_type = 'polygon'
            else:
                self.data_type = 'line'
        else:
            self.data_type = 'numeric'
        try:
            self.existing_keywords = self.keyword_io.read_keywords(self.layer)
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            self.existing_keywords = None
        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)
        self.update_category_tab()
        self.auto_select_one_item(self.lstCategories)
        self.set_existing_options(step_category)
        # noinspection PyUnresolvedReferences
        self.treeClasses.itemChanged.connect(self.update_dragged_item_flags)
        self.pbnCancel.released.connect(self.reject)
        self.go_to_step(1)
        self.set_tool_tip()

        # string constants
        self.global_default_string = metadata.global_default_attribute['name']
        self.global_default_data = metadata.global_default_attribute['id']
        self.do_not_use_string = metadata.do_not_use_attribute['name']
        self.do_not_use_data = metadata.do_not_use_attribute['id']
        self.defaults = breakdown_defaults()

    def selected_category(self):
        """Obtain the category selected by user.

        :returns: Metadata of the selected category.
        :rtype: dict, None
        """
        item = self.lstCategories.currentItem()

        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory.
        :rtype: dict, None
        """
        item = self.lstSubcategories.currentItem()
        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit.
        :rtype: dict, None
        """
        item = self.lstUnits.currentItem()
        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_field(self):
        """Obtain the field selected by user.

        :returns: Keyword of the selected field.
        :rtype: string, None
        """
        item = self.lstFields.currentItem()
        if item:
            return item.text()
        else:
            return None

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
                value_list += [tree_leaf.text(0)]
            if value_list:
                value_map[tree_branch.text(0)] = value_list
        return value_map

    def get_aggregation_attributes(self):
        """Obtain the value of aggregation attributes set by user.

        :returns: The key and value of aggregation attributes.
        :rtype: dict
        """
        aggregation_attributes = dict()

        current_index = self.cboFemaleRatioAttribute.currentIndex()
        data = self.cboFemaleRatioAttribute.itemData(current_index)
        aggregation_attributes[female_ratio_attribute_key] = data

        value = self.dsbFemaleRatioDefault.value()
        aggregation_attributes[female_ratio_default_key] = value

        current_index = self.cboYouthRatioAttribute.currentIndex()
        data = self.cboYouthRatioAttribute.itemData(current_index)
        aggregation_attributes[youth_ratio_attribute_key] = data

        value = self.dsbYouthRatioDefault.value()
        aggregation_attributes[youth_ratio_default_key] = value

        current_index = self.cboAdultRatioAttribute.currentIndex()
        data = self.cboAdultRatioAttribute.itemData(current_index)
        aggregation_attributes[adult_ratio_attribute_key] = data

        value = self.dsbAdultRatioDefault.value()
        aggregation_attributes[adult_ratio_default_key] = value

        current_index = self.cboElderlyRatioAttribute.currentIndex()
        data = self.cboElderlyRatioAttribute.itemData(current_index)
        aggregation_attributes[elderly_ratio_attribute_key] = data

        value = self.dsbElderlyRatioDefault.value()
        aggregation_attributes[elderly_ratio_default_key] = value

        return aggregation_attributes

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

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboFemaleRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the female ratio attribute is changed.

        When the user changes the female ratio attribute
        (cboFemaleRatioAttribute), it will change the enabled value of
        dsbFemaleRatioDefault. If value is 'Use default', enable
        dsbFemaleRatioDefault. Otherwise, disabled it.
        """
        value = self.cboFemaleRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbFemaleRatioDefault.setEnabled(True)
        else:
            self.dsbFemaleRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboYouthRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the youth ratio attribute is changed.

        When the user changes the youth ratio attribute
        (cboYouthRatioAttribute), it will change the enabled value of
        dsbYouthRatioDefault. If value is 'Use default', enable
        dsbYouthRatioDefault. Otherwise, disabled it.
        """
        value = self.cboYouthRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbYouthRatioDefault.setEnabled(True)
        else:
            self.dsbYouthRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboAdultRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the adult ratio attribute
        (cboAdultRatioAttribute), it will change the enabled value of
        dsbAdultRatioDefault. If value is 'Use default', enable
        dsbAdultRatioDefault. Otherwise, disabled it.
        """
        value = self.cboAdultRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbAdultRatioDefault.setEnabled(True)
        else:
            self.dsbAdultRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboElderlyRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the elderly ratio attribute
        (cboElderlyRatioAttribute), it will change the enabled value of
        dsbElderlyRatioDefault. If value is 'Use default', enable
        dsbElderlyRatioDefault. Otherwise, disabled it.
        """
        value = self.cboElderlyRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbElderlyRatioDefault.setEnabled(True)
        else:
            self.dsbElderlyRatioDefault.setEnabled(False)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Update category description label and subcategory widgets.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.lstSubcategories.clear()
        category = self.selected_category()
        # Exit if no selection
        if not category:
            return
        # Set description label
        self.lblDescribeCategory.setText(category["description"])
        self.lblIconCategory.setPixmap(
            QPixmap(':/plugins/inasafe/keyword-category-%s.svg'
                    % (category['id'] or 'notset')))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_lstSubcategories_itemSelectionChanged(self):
        """Update subcategory description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.lstUnits.clear()
        subcategory = self.selected_subcategory()
        # Exit if no selection
        if not subcategory:
            return
        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])
        self.lblIconSubcategory.setPixmap(QPixmap(
            ':/plugins/inasafe/keyword-subcategory-%s.svg'
            % (subcategory['id'] or 'notset')))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_lstUnits_itemSelectionChanged(self):
        """Update unit description label and field widgets.

        .. note:: This is an automatic Qt slot
           executed when the unit selection changes.
        """
        self.lstFields.clear()
        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return
        self.lblDescribeUnit.setText(unit['description'])
        # Enable the next button
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_lstFields_itemSelectionChanged(self):
        """Update field description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.treeClasses.clear()
        field = self.selected_field()
        # Exit if no selection
        if not field:
            return

        fields = self.layer.dataProvider().fields()
        field_type = fields.field(field).typeName()
        field_index = fields.indexFromName(self.selected_field())
        unique_values = self.layer.uniqueValues(field_index)[0:48]
        unique_values_str = [i and unicode(i) or 'NULL' for i in unique_values]
        if unique_values != self.layer.uniqueValues(field_index):
            unique_values_str += ['...']
        desc = '<br/>%s: %s<br/><br/>' % (self.tr('Field type'), field_type)
        desc += self.tr('Unique values: %s') % ', '.join(unique_values_str)
        self.lblDescribeField.setText(desc)
        # Enable the next button
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_leTitle_textChanged(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the title value changes.
        """
        self.pbnNext.setEnabled(bool(self.leTitle.text()))

    def update_category_tab(self):
        """Set widgets on the Category tab."""
        self.lstCategories.clear()
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setPixmap(QPixmap())
        self.lblSelectCategory.setText(
            category_question % self.layer.name())
        categories = ImpactFunctionManager().categories_for_layer(
            self.layer_type, self.data_type)
        if self.data_type == 'polygon':
            categories += ['aggregation']
        if self.data_type == 'point':
            categories = ['hazard']
        for category in categories:
            if type(category) != dict:
                # pylint: disable=W0612
                # noinspection PyUnresolvedReferences
                category = eval('metadata.%s_definition' % category)
                # pylint: enable=W0612
            item = QListWidgetItem(category['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, unicode(category))
            self.lstCategories.addItem(item)

    def update_subcategory_tab(self):
        """Set widgets on the Subcategory tab."""
        category = self.selected_category()
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % category['id']))
        for i in ImpactFunctionManager().subcategories_for_layer(
                category['id'], self.layer_type, self.data_type):
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            item.setData(QtCore.Qt.UserRole, unicode(i))
            self.lstSubcategories.addItem(item)

    def update_unit_tab(self):
        """Set widgets on the Unit tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        self.lstFields.clear()
        for i in ImpactFunctionManager().units_for_layer(
                subcategory['id'], self.layer_type, self.data_type):
            if (self.layer_type == 'raster' and
                    i['constraint'] == 'categorical'):
                continue
            else:
                item = QListWidgetItem(i['name'], self.lstUnits)
                item.setData(QtCore.Qt.UserRole, unicode(i))
                self.lstUnits.addItem(item)

    def update_field_tab(self):
        """Set widgets on the Field tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        if subcategory and unit:
            subcategory_unit_relation = get_question_text(
                '%s_%s_question' % (subcategory['id'], unit['id']))
        else:
            subcategory_unit_relation = self.tr(
                '<b><font color="red">ERROR! '
                'Missing subcategory or unit!</font></b>')
        if category['id'] == 'aggregation':
            question_text = field_question_aggregation
        else:
            # unique values, continuous or categorical data
            question_text = field_question_subcategory_unit % (
                category['name'],
                subcategory['name'],
                unit['name'],
                subcategory_unit_relation)
        self.lblSelectField.setText(question_text)
        self.lstFields.clear()
        default_item = None
        for field in self.layer.dataProvider().fields():
            field_name = field.name()
            item = QListWidgetItem(field_name, self.lstFields)
            item.setData(QtCore.Qt.UserRole, field_name)
            # Select the item if it match the unit's default_attribute
            if unit and unit['id'] == 'building_generic':
                pass
            else:
                if unit and 'default_attribute' in unit \
                        and field_name == unit['default_attribute']:
                    default_item = item
                # For continuous data, gray out id, gid, fid and text fields
                if unit and unit['constraint'] == 'continuous':
                    field_type = field.type()
                    if field_type > 9 or re.match(
                            '.{0,2}id$', field_name, re.I):
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

    def update_classify_tab(self):
        """Set widgets on the Classify tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        default_classes = unit['classes']
        field = self.selected_field()
        field_index = self.layer.dataProvider().fields().indexFromName(
            self.selected_field())
        field_type = self.layer.dataProvider().fields()[field_index].type()
        self.lblClassify.setText(classify_question %
                                (subcategory['name'], category['name'],
                                 unit['name'], field.upper()))
        # Assign unique values to classes
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['name']] = list()
        for value in self.layer.uniqueValues(field_index):
            value_as_string = value and unicode(value) or 'NULL'
            assigned = False
            for default_class in default_classes:
                if (field_type > 9
                    and value_as_string in default_class['string_defaults']) \
                        or (field_type < 10
                            and (default_class['numeric_default_min'] <=
                                 value < default_class[
                                 'numeric_default_max'])):
                    assigned_values[default_class['name']] += [value_as_string]
                    assigned = True
            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [value_as_string]
        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

    def go_to_step(self, step):
        """Set the stacked widget to the given step.

        :param step: The step number to be moved to.
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step - 1)
        self.lblStep.setText(self.tr('step %d') % step)
        self.pbnBack.setEnabled(step > 1)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnNext_released(self):
        """Handle the Next button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        current_step = self.get_current_step()

        if current_step == step_aggregation:
            good_age_ratio, sum_age_ratios = self.age_ratios_are_valid()
            if not good_age_ratio:
                message = self.tr(
                    'The sum of age ratio default is %s and it is more '
                    'than 1. Please adjust the age ratio default so that they '
                    'will not more than 1.' % sum_age_ratios)
                if not self.suppress_warning_dialog:
                    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                    QtGui.QMessageBox.warning(
                        self, self.tr('InaSAFE'), message)
                return

        # Determine the new step to be switched
        new_step = self.compute_next_step(current_step)

        # Prepare the next tab
        if new_step == step_subcategory:
            self.update_subcategory_tab()
            self.set_existing_options(step_subcategory)
            self.auto_select_one_item(self.lstSubcategories)
        elif new_step == step_unit:
            self.update_unit_tab()
            self.set_existing_options(step_unit)
            self.auto_select_one_item(self.lstUnits)
        elif new_step == step_field:
            self.update_field_tab()
            self.set_existing_options(step_field)
            self.auto_select_one_item(self.lstFields)
        elif new_step == step_classify:
            self.update_classify_tab()
            self.set_existing_options(step_classify)
        elif new_step in [step_source, step_aggregation]:
            self.set_existing_options(new_step)
        elif new_step is None:
            # Complete
            self.accept()
            return
        # Set Next button label
        if new_step == self.stackedWidget.count():
            self.set_existing_options(self.stackedWidget.count())
            self.pbnNext.setText(self.tr('Finish'))
        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnBack_released(self):
        """Handle the Back button release.

        .. note:: This is an automatic Qt slot
           executed when the Back button is released.
        """
        current_step = self.get_current_step()
        new_step = self.compute_previous_step(current_step)
        # Set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnHelp_released(self):
        """Handle the Help button release.

        .. note:: This is an automatic Qt slot
           executed when the Back button is released.
        """
        show_context_help('keywords_wizard')

    def is_ready_to_next_step(self, step):
        """Check if the present step is complete.

        :param step: The present step number.
        :type step: int

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        if step == step_category:
            return bool(self.selected_category())
        if step == step_subcategory:
            return bool(self.selected_subcategory())
        if step == step_unit:
            return bool(self.selected_unit())
        if step == step_field:
            return bool(self.selected_field() or not self.lstFields.count())
        if step == step_classify:
            # Allow to not classify any values
            return True
        if step == step_source:
            # The source_* keywords are not required
            return True
        if step == step_aggregation:
            # Not required
            return True
        if step == step_title:
            return bool(self.leTitle.text())

    def compute_next_step(self, current_step):
        """Determine the next step to be switched to.

        :param current_step: The present step number.
        :type current_step: int

        :returns: The next step number or None if finished.
        :rtype: int
        """
        if current_step == step_category:
            category = self.selected_category()
            if category['id'] == 'aggregation':
                new_step = step_field
            elif ImpactFunctionManager().subcategories_for_layer(
                    category['id'], self.layer_type, self.data_type):
                new_step = step_subcategory
            else:
                new_step = step_field
        elif current_step == step_subcategory:
            subcategory = self.selected_subcategory()
            # skip field and classify step if point layer and it's a volcano
            if self.data_type == 'point' and subcategory['id'] == 'volcano':
                new_step = step_source
            elif ImpactFunctionManager().units_for_layer(
                    subcategory['id'], self.layer_type, self.data_type):
                new_step = step_unit
            else:
                new_step = step_field
        elif current_step == step_field:
            unit = self.selected_unit()
            if unit and unit['constraint'] == 'categorical':
                new_step = step_classify
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_aggregation
            else:
                new_step = step_source
        elif current_step == step_classify:
            new_step = step_source
        elif current_step == step_unit:
            unit = self.selected_unit()
            if unit and unit['id'] == 'building_generic':
                new_step = step_source
            else:
                new_step = current_step + 1
        elif current_step in (step_aggregation, step_source):
            new_step = current_step + 1
        elif current_step == step_title:
            new_step = None
        else:
            raise Exception('Unexpected number of steps')
        # Skip the field (and classify) tab if raster layer
        if new_step == step_field and is_raster_layer(self.layer):
            new_step = step_source

        return new_step

    def compute_previous_step(self, current_step):
        """Determine the previous step to be switched to (by the Back button).

        :param current_step: The present step number.
        :type current_step: int

        :returns: The previous step number.
        :rtype: int
        """
        if current_step == step_source:
            if self.selected_mapping():
                new_step = step_classify
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_aggregation
            elif self.selected_field():
                new_step = step_field
            elif self.selected_unit():
                new_step = step_unit
            elif self.selected_subcategory():
                new_step = step_subcategory
            else:
                new_step = step_category
        elif current_step == step_field:
            if self.selected_unit():
                new_step = step_unit
            elif self.selected_subcategory():
                new_step = step_subcategory
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_category
            else:
                new_step = step_category
        elif current_step == step_aggregation:
            new_step = step_field
        else:
            new_step = current_step - 1
        return new_step

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        keywords = {}
        if self.selected_category():
            keywords['category'] = self.selected_category()['id']
            if keywords['category'] == 'aggregation':
                keywords['category'] = 'postprocessing'
                keywords.update(self.get_aggregation_attributes())
        if self.selected_subcategory():
            keywords['subcategory'] = self.selected_subcategory()['id']
        if self.selected_unit():
            keywords['unit'] = self.selected_unit()['id']
        if self.lstFields.currentItem():
            if 'category' in keywords.keys():
                if keywords['category'] != 'postprocessing':
                    key_field = 'field'
                else:
                    key_field = 'aggregation attribute'
                keywords[key_field] = self.lstFields.currentItem().text()
        if self.leSource.text():
            keywords['source'] = self.leSource.text()
        if self.leSource_url.text():
            keywords['source_url'] = self.leSource_url.text()
        if self.leSource_scale.text():
            keywords['source_scale'] = self.leSource_scale.text()
        if self.leSource_date.text():
            keywords['source_date'] = self.leSource_date.text()
        if self.leTitle.text():
            keywords['title'] = self.leTitle.text()
        value_map = self.selected_mapping()
        if value_map:
            keywords['value_map'] = json.dumps(value_map)
        return keywords

    def accept(self):
        """Automatic slot executed when the Finish button is pressed.

        It will write out the keywords for the layer that is active.
        This method is based on the KeywordsDialog class.
        """
        current_keywords = self.get_keywords()
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=current_keywords)
        except InaSAFEError, e:
            error_message = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s') % error_message.to_html())))
        if self.dock is not None:
            # noinspection PyUnresolvedReferences
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)

    def get_existing_keyword(self, keyword):
        """Obtain an existing keyword's value.

        :param keyword: A keyword from keywords.
        :type keyword: str

        :returns: The value of the keyword.
        :rtype: str
        """
        if self.existing_keywords is None:
            return None
        if keyword is not None:
            return self.existing_keywords.get(keyword, None)
        else:
            return None

    def set_existing_options(self, current_step):
        """Set options in wizard based on existing keywords.

        :param current_step: The present step number of the wizard.
        :type current_step: int
        """
        if current_step == step_category:
            category_keyword = self.get_existing_keyword('category')
            if category_keyword == 'postprocessing':
                category_keyword = 'aggregation'
            if category_keyword is None:
                return
            categories = []
            for index in xrange(self.lstCategories.count()):
                item = self.lstCategories.item(index)
                category = eval(item.data(QtCore.Qt.UserRole))
                categories.append(category['id'])
            if category_keyword in categories:
                self.lstCategories.setCurrentRow(
                    categories.index(category_keyword))

        elif current_step == step_subcategory:
            subcategory_keyword = self.get_existing_keyword('subcategory')
            if subcategory_keyword is None:
                return
            subcategories = []
            for index in xrange(self.lstSubcategories.count()):
                item = self.lstSubcategories.item(index)
                subcategory = eval(item.data(QtCore.Qt.UserRole))
                subcategories.append(subcategory['id'])
            if subcategory_keyword in subcategories:
                self.lstSubcategories.setCurrentRow(
                    subcategories.index(subcategory_keyword))

        elif current_step == step_unit:
            unit_id = self.get_existing_keyword('unit')
            unit_id = metadata.old_to_new_unit_id(unit_id)
            if unit_id is None:
                return
            units = []
            for index in xrange(self.lstUnits.count()):
                item = self.lstUnits.item(index)
                unit = eval(item.data(QtCore.Qt.UserRole))
                units.append(unit['id'])
            if unit_id in units:
                self.lstUnits.setCurrentRow(units.index(unit_id))

        elif current_step == step_field:
            if self.selected_category()['id'] != 'aggregation':
                field = self.get_existing_keyword('field')
            else:
                field = self.get_existing_keyword('aggregation attribute')
            if field is None:
                return
            fields = []
            for index in xrange(self.lstFields.count()):
                fields.append(str(self.lstFields.item(index).text()))
            if field in fields:
                self.lstFields.setCurrentRow(fields.index(field))

        elif current_step == step_classify:
            unit_id = self.get_existing_keyword('unit')
            unit_name = metadata.old_to_new_unit_id(unit_id)
            # Do not continue if user select different unit
            if unit_name != self.selected_unit()['name']:
                return

            field = self.get_existing_keyword('field')
            # Do not continue if user select different field
            if field != self.selected_field():
                return

            # Do not continue if there is no value_map in existing keywords
            value_map = self.get_existing_keyword('value_map')

            if value_map is None:
                return

            # Assign unique values to classes
            unit = self.selected_unit()
            default_classes = unit['classes']
            unassigned_values = list()
            assigned_values = dict()
            for default_class in default_classes:
                assigned_values[default_class['name']] = list()
            if type(value_map) == str:
                try:
                    value_map = json.loads(value_map)
                except ValueError:
                    return
            field_index = self.layer.dataProvider().fields().indexFromName(
                self.selected_field())
            for unique_value in self.layer.uniqueValues(field_index):
                value_as_string = (
                    unique_value and unicode(unique_value) or 'NULL')
                # check in value map
                assigned = False
                for key, value in value_map.iteritems():
                    if value_as_string in value:
                        assigned_values[key] += [value_as_string]
                        assigned = True
                if not assigned:
                    unassigned_values += [value_as_string]
            self.populate_classified_values(
                unassigned_values, assigned_values, default_classes)

        elif current_step == step_aggregation:
            self.set_existing_aggregation_attributes()

        elif current_step == step_source:
            source = self.get_existing_keyword('source')
            self.leSource.setText(source)
            source_scale = self.get_existing_keyword('source_scale')
            self.leSource_scale.setText(source_scale)
            source_date = self.get_existing_keyword('source_date')
            self.leSource_date.setText(source_date)
            source_url = self.get_existing_keyword('source_url')
            self.leSource_url.setText(source_url)

        elif current_step == step_title:
            title = self.layer.name()
            self.leTitle.setText(title)

    def set_existing_aggregation_attributes(self):
        """Set values in aggregation step wizard based on existing keywords."""
        self.defaults = breakdown_defaults()

        female_ratio_default = self.get_existing_keyword(
            female_ratio_default_key)
        if female_ratio_default:
            self.dsbFemaleRatioDefault.setValue(
                float(female_ratio_default))
        else:
            self.dsbFemaleRatioDefault.setValue(self.defaults['FEMALE_RATIO'])

        youth_ratio_default = self.get_existing_keyword(
            youth_ratio_default_key)
        if youth_ratio_default:
            self.dsbYouthRatioDefault.setValue(float(youth_ratio_default))
        else:
            self.dsbYouthRatioDefault.setValue(self.defaults['YOUTH_RATIO'])

        adult_ratio_default = self.get_existing_keyword(
            adult_ratio_default_key)
        if adult_ratio_default:
            self.dsbAdultRatioDefault.setValue(float(adult_ratio_default))
        else:
            self.dsbAdultRatioDefault.setValue(self.defaults['ADULT_RATIO'])

        elderly_ratio_default = self.get_existing_keyword(
            elderly_ratio_default_key)
        if elderly_ratio_default:
            self.dsbElderlyRatioDefault.setValue(float(elderly_ratio_default))
        else:
            self.dsbElderlyRatioDefault.setValue(
                self.defaults['ELDERLY_RATIO'])

        ratio_attribute_keys = [
            female_ratio_attribute_key,
            youth_ratio_attribute_key,
            adult_ratio_attribute_key,
            elderly_ratio_attribute_key]

        cbo_ratio_attributes = [
            self.cboFemaleRatioAttribute,
            self.cboYouthRatioAttribute,
            self.cboAdultRatioAttribute,
            self.cboElderlyRatioAttribute]

        for i in range(len(cbo_ratio_attributes)):
            self.populate_cbo_aggregation_attribute(
                ratio_attribute_keys[i], cbo_ratio_attributes[i])

    # noinspection PyUnresolvedReferences,PyStatementEffect
    def populate_cbo_aggregation_attribute(
            self, ratio_attribute_key, cbo_ratio_attribute):
        """Populate the combo box cbo_ratio_attribute for ratio_attribute_key.

        :param ratio_attribute_key: A ratio attribute key that saved in
               keywords.
        :type ratio_attribute_key: str

        :param cbo_ratio_attribute: A combo box that wants to be populated.
        :type cbo_ratio_attribute: QComboBox
        """
        cbo_ratio_attribute.clear()
        ratio_attribute = self.get_existing_keyword(ratio_attribute_key)
        fields, attribute_position = layer_attribute_names(
            self.layer, [QtCore.QVariant.Double], ratio_attribute)

        cbo_ratio_attribute.addItem(
            self.global_default_string, self.global_default_data)
        cbo_ratio_attribute.addItem(
            self.do_not_use_string, self.do_not_use_data)
        for field in fields:
            cbo_ratio_attribute.addItem(field, field)
        # For backward compatibility, still use Use default
        if (ratio_attribute == self.global_default_data or
                ratio_attribute == self.tr('Use default')):
            cbo_ratio_attribute.setCurrentIndex(0)
        elif ratio_attribute == self.do_not_use_data:
            cbo_ratio_attribute.setCurrentIndex(1)
        elif ratio_attribute is None or attribute_position is None:
            # current_keyword was not found in the attribute table.
            # Use default
            cbo_ratio_attribute.setCurrentIndex(0)
        else:
            # + 2 is because we add use defaults and don't use
            cbo_ratio_attribute.setCurrentIndex(attribute_position + 2)

    def populate_classified_values(
            self, unassigned_values, assigned_values, default_classes):
        """Populate lstUniqueValues and treeClasses.from the parameters.

        :param unassigned_values: List of values that haven't been assigned
            to a class. It will be put in self.lstUniqueValues.
        :type unassigned_values: list

        :param assigned_values: Dictionary with class as the key and list of
            value as the the value of the dictionary. It will be put in
            self.treeClasses.
        :type assigned_values: dict

        :param default_classes: Default classes from unit.
        :type default_classes: list
        """
        # Populate the unique values list
        self.lstUniqueValues.clear()
        for value in unassigned_values:
            list_item = QtGui.QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(QtCore.Qt.ItemIsEnabled |
                               QtCore.Qt.ItemIsSelectable |
                               QtCore.Qt.ItemIsDragEnabled)
            list_item.setText(value)
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
            tree_branch.setFlags(QtCore.Qt.ItemIsDropEnabled |
                                 QtCore.Qt.ItemIsEnabled)
            tree_branch.setExpanded(True)
            tree_branch.setFont(0, bold_font)
            tree_branch.setText(0, default_class['name'])
            if 'description' in default_class:
                tree_branch.setToolTip(0, default_class['description'])
            # Assign known values
            for value in assigned_values[default_class['name']]:
                tree_leaf = QtGui.QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(QtCore.Qt.ItemIsEnabled |
                                   QtCore.Qt.ItemIsSelectable |
                                   QtCore.Qt.ItemIsDragEnabled)
                tree_leaf.setText(0, value)

    def set_tool_tip(self):
        """Set tool tip as helper text for some objects."""

        title_tooltip = self.tr('Title of the layer.')
        source_tooltip = self.tr(
            'Please record who is the custodian of this layer i.e. '
            'OpenStreetMap')
        date_tooltip = self.tr(
            'When was this data collected or downloaded i.e. 1-May-2014')
        scale_tooltip = self.tr('What is the scale of this layer?')
        url_tooltip = self.tr(
            'Does the custodians have their own website '
            'i.e. www.openstreetmap.org')

        self.lblTitle.setToolTip(title_tooltip)
        self.lblSource.setToolTip(source_tooltip)
        self.lblDate.setToolTip(date_tooltip)
        self.lblScale.setToolTip(scale_tooltip)
        self.lblURL.setToolTip(url_tooltip)

        self.leTitle.setToolTip(title_tooltip)
        self.leSource.setToolTip(source_tooltip)
        self.leSource_date.setToolTip(date_tooltip)
        self.leSource_scale.setToolTip(scale_tooltip)
        self.leSource_url.setToolTip(url_tooltip)

    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def auto_select_one_item(self, list_widget):
        """Select item in the list in list_widget if it's the only item.

        :param list_widget: The list widget that want to be checked.
        :type list_widget: QListWidget
        """
        if list_widget.count() == 1 and list_widget.currentRow() == -1:
            list_widget.setCurrentRow(0)

    def age_ratios_are_valid(self):
        """Return true if the sum of age ratios is good, otherwise False.

        Good means their sum does not exceed 1.

        :returns: Tuple of boolean and float. Boolean represent good or not
            good, while float represent the summation of age ratio. If some
            ratio do not use global default, the summation is set to 0.
        :rtype: tuple

        """
        youth_ratio_index = self.cboYouthRatioAttribute.currentIndex()
        adult_ratio_index = self.cboAdultRatioAttribute.currentIndex()
        elderly_ratio_index = self.cboElderlyRatioAttribute.currentIndex()

        ratio_indexes = [
            youth_ratio_index, adult_ratio_index, elderly_ratio_index]

        if ratio_indexes.count(0) == len(ratio_indexes):
            youth_ratio_default = self.dsbYouthRatioDefault.value()
            adult_ratio_default = self.dsbAdultRatioDefault.value()
            elderly_ratio_default = self.dsbElderlyRatioDefault.value()

            sum_ratio_default = youth_ratio_default + adult_ratio_default
            sum_ratio_default += elderly_ratio_default
            if sum_ratio_default > 1:
                return False, sum_ratio_default
            else:
                return True, sum_ratio_default
        return True, 0

    def get_current_step(self):
        """Return current step of the wizard.

        :returns: Current step of the wizard.
        :rtype: int
        """
        return self.stackedWidget.currentIndex() + 1
