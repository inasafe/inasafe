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
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QListWidgetItem, QPixmap
from PyQt4.QtGui import QApplication

# from third_party.odict import OrderedDict
from safe.api import ImpactFunctionManager as IFM

from safe_qgis.safe_interface import InaSAFEError
from safe_qgis.ui.wizard_dialog_base import Ui_WizardDialogBase
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_point_layer,
    is_polygon_layer,
    is_raster_layer)


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
    'area, while ares with no polygon coverage would be assumed '
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
earthquake_question = QApplication.translate(
    'WizardDialog',
    'earthquake intensity in MMI')
tephra_kgm2_question = QApplication.translate(
    'WizardDialog',
    'tephra intensity in kg/m<sup>2</sup>')
population_number_question = QApplication.translate(
    'WizardDialog',
    'the number of people')
population_density_question = QApplication.translate(
    'WizardDialog',
    'people density in people/km<sup>2</sup>')
road_roadclass_question = QApplication.translate(
    'WizardDialog',
    'type for your road')

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
step_source = 6
step_title = 7


def get_question_text(constant):
    """Find a constant by name and return its value.

    :param constant: The name of the constant to look for
    :type constant: string

    :returns: The value of the constant or red error message
    :rtype: string

    """
    try:
        return eval(constant)
    except NameError:
        return '<b>MISSING CONSTANT: %s</b>' % constant


class WizardDialog(QtGui.QDialog, Ui_WizardDialogBase):
    """Dialog implementation class for the InaSAFE keywords wizard."""

    def __init__(self, parent, iface, dock=None, layer=None):
        """Constructor for the dialog.

        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: Quantum GIS QGisAppInterface instance.
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

        self.update_category_tab()

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)

        self.treeClasses.itemChanged.connect(self.update_dragged_item_flags)
        self.pbnCancel.released.connect(self.reject)

        self.go_to_step(1)

    def selected_category(self):
        """Obtain the category selected by user.

        :returns: metadata of the selected category
        :rtype: dict or None
        """
        item = self.lstCategories.currentItem()
        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: metadata of the selected subcategory
        :rtype: dict or None
        """
        item = self.lstSubcategories.currentItem()
        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: metadata of the selected unit
        :rtype: dict or None
        """
        item = self.lstUnits.currentItem()
        try:
            return eval(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def selected_field(self):
        """Obtain the field selected by user.

        :returns: keyword of the selected field
        :rtype: string or None
        """
        item = self.lstFields.currentItem()
        if item:
            return item.text()
        else:
            return None

    def selected_mapping(self):
        """Obtain the value-to-class mapping set by user.

        :returns: the complete mapping as a dict of lists
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

    def update_dragged_item_flags(self, item, column):
        """A slot executed when thee item change. Check if it looks like
        an item  dragged from QListWidget to QTreeWidget and disable the
        drop flag. For some reasons the flag is set when dragging.
        """
        if int(item.flags() & QtCore.Qt.ItemIsDropEnabled) \
                and int(item.flags() & QtCore.Qt.ItemIsDragEnabled):
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Automatic slot executed when category change. Set description label
           and subcategory widgets according to the selected category
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

    def on_lstSubcategories_itemSelectionChanged(self):
        """Automatic slot executed when subcategory change. Set description
          label and unit widgets according to the selected category
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

    def on_lstUnits_itemSelectionChanged(self):
        """Automatic slot executed when unit change. Set description label
           and field widgets according to the selected category
        """
        self.lstFields.clear()

        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return
        self.lblDescribeUnit.setText(unit['description'])

        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_lstFields_itemSelectionChanged(self):
        """Automatic slot executed when field change.
           Unlocks the Next button.
        """
        self.treeClasses.clear()

        field = self.selected_field()
        # Exit if no selection
        if not field:
            return

        fields = self.layer.dataProvider().fields()
        field_type = fields.field(field).typeName()
        field_idx = fields.indexFromName(self.selected_field())
        unique_values = self.layer.uniqueValues(field_idx)[0:48]
        unique_values_str = [i and unicode(i) or 'NULL' for i in unique_values]
        if unique_values != self.layer.uniqueValues(field_idx):
            unique_values_str += ['...']
        desc = '<br/>%s: %s<br/><br/>' % (self.tr('Field type'), field_type)
        desc += self.tr('Unique values: %s') % ', '.join(unique_values_str)
        self.lblDescribeField.setText(desc)

        # Enable the next button
        self.pbnNext.setEnabled(True)

    def on_leTitle_textChanged(self):
        """Automatic slot executed when the title change.
           Unlocks the Next button.
        """
        # Enable the next button
        self.pbnNext.setEnabled(bool(self.leTitle.text()))

    def update_category_tab(self):
        """Set widgets on the Category tab
        """
        self.lstCategories.clear()
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setPixmap(QPixmap())
        self.lblSelectCategory.setText(
            category_question % self.layer.name())
        categories = IFM().categories_for_layer(
            self.layer_type, self.data_type)
        if self.data_type == 'polygon':
            categories += ['aggregation']
        for category in categories:
            if type(category) != dict:
                from safe import metadata
                category = eval('metadata.%s_definition' % category)
            item = QListWidgetItem(category['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, unicode(category))
            self.lstCategories.addItem(item)

    def update_subcategory_tab(self):
        """Set widgets on the Subcategory tab
        """
        category = self.selected_category()
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % category['id']))
        for i in IFM().subcategories_for_layer(
                category['id'], self.layer_type, self.data_type):
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            item.setData(QtCore.Qt.UserRole, unicode(i))
            self.lstSubcategories.addItem(item)

    def update_unit_tab(self):
        """Set widgets on the Unit tab
        """
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        self.lstFields.clear()
        for i in IFM().units_for_layer(
                subcategory['id'], self.layer_type, self.data_type):
            item = QListWidgetItem(i['name'], self.lstUnits)
            item.setData(QtCore.Qt.UserRole, unicode(i))
            self.lstUnits.addItem(item)

    def update_field_tab(self):
        """Set widgets on the Field tab (lblSelectField and lstFields)
        """
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
            if unit and 'default_attribute' in unit \
                    and field_name == unit['default_attribute']:
                default_item = item
            # For continuous data, gray out id, gid, fid and text fields
            if unit and unit['constraint'] == 'continuous':
                field_type = field.type()
                if field_type > 9 or re.match('.{0,2}id$', field_name, re.I):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

    def update_classify_tab(self):
        """Set widgets on the Classify tab
        """
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        default_classes = unit['classes']
        field = self.selected_field()
        field_idx = self.layer.dataProvider().fields().indexFromName(
            self.selected_field())
        field_type = self.layer.dataProvider().fields()[field_idx].type()
        self.lblClassify.setText(classify_question %
                                (subcategory['name'], category['name'],
                                 unit['name'], field.upper()))

        # Assign unique values to classes
        unassigned_values = list()
        assigned_values = dict()
        for cls in default_classes:
            assigned_values[cls['name']] = list()
        for val in self.layer.uniqueValues(field_idx):
            val_str = val and unicode(val) or 'NULL'
            assigned = False
            for cls in default_classes:
                if (field_type > 9 and val_str in cls['string_defaults']) \
                        or (field_type < 10
                            and val >= cls['numeric_default_min']
                            and val <= cls['numeric_default_max']):
                    assigned_values[cls['name']] += [val_str]
                    assigned = True
            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [val_str]

        # Populate the unique vals list
        self.lstUniqueValues.clear()
        for val in unassigned_values:
            list_item = QtGui.QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(QtCore.Qt.ItemIsEnabled |
                               QtCore.Qt.ItemIsSelectable |
                               QtCore.Qt.ItemIsDragEnabled)
            list_item.setText(val)
            self.lstUniqueValues.addItem(list_item)

        # Populate assigned values tree
        self.treeClasses.clear()
        bold_font = QtGui.QFont()
        bold_font.setItalic(True)
        bold_font.setBold(True)
        bold_font.setWeight(75)
        self.treeClasses.invisibleRootItem().setFlags(QtCore.Qt.ItemIsEnabled)
        for cls in default_classes:
            # Create branch for class
            tree_branch = QtGui.QTreeWidgetItem(self.treeClasses)
            tree_branch.setFlags(QtCore.Qt.ItemIsDropEnabled |
                                 QtCore.Qt.ItemIsEnabled)
            tree_branch.setExpanded(True)
            tree_branch.setFont(0, bold_font)
            tree_branch.setText(0, cls['name'])
            if 'description' in cls:
                tree_branch.setToolTip(0, cls['description'])
            # Assign known values
            for val in assigned_values[cls['name']]:
                tree_leaf = QtGui.QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(QtCore.Qt.ItemIsEnabled |
                                   QtCore.Qt.ItemIsSelectable |
                                   QtCore.Qt.ItemIsDragEnabled)
                tree_leaf.setText(0, val)

    def go_to_step(self, step):
        """Set the stacked widget to the given step

        :param step: The step number to be moved to
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step-1)
        self.lblStep.setText(self.tr('step %d') % step)
        self.pbnBack.setEnabled(step > 1)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnNext_released(self):
        """Automatic slot executed when the pbnNext button is released."""
        current_step = self.stackedWidget.currentIndex() + 1
        # Determine the new step to be switched
        new_step = self.compute_next_step(current_step)

        # Prepare the next tab
        if new_step == step_subcategory:
            self.update_subcategory_tab()
        elif new_step == step_unit:
            self.update_unit_tab()
        elif new_step == step_field:
            self.update_field_tab()
        elif new_step == step_classify:
            self.update_classify_tab()
        elif new_step is None:
            # Complete
            self.accept()
            return

        # Set Next button label
        if new_step == self.stackedWidget.count():
            self.pbnNext.setText(self.tr('Finish'))
        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnBack_released(self):
        """Automatic slot executed when the pbnBack button is released."""
        current_step = self.stackedWidget.currentIndex() + 1
        new_step = self.compute_previous_step(current_step)
        # Set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)

    def is_ready_to_next_step(self, step):
        """Check if widgets are filled an new step can be enabled

        :param step: The present step number
        :type step: int

        :returns: True if new step may be enabled
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
        if step == step_title:
            return bool(self.leTitle.text())

    def compute_next_step(self, current_step):
        """Determine the next step to be switched to

        :param current_step: The present step number
        :type current_step: int

        :returns: The next step number or None if finished
        :rtype: int
        """
        if current_step == step_category:
            category = self.selected_category()
            if category['id'] == 'aggregation':
                new_step = step_field
            elif IFM().subcategories_for_layer(
                    category['id'], self.layer_type, self.data_type):
                new_step = step_subcategory
            else:
                new_step = step_field
        elif current_step == step_subcategory:
            subcategory = self.selected_subcategory()
            if IFM().units_for_layer(
                    subcategory['id'], self.layer_type, self.data_type):
                new_step = step_unit
            else:
                new_step = step_field
        elif current_step == step_field:
            subcategory = self.selected_subcategory()
            unit = self.selected_unit()
            if unit and unit['constraint'] == 'categorical':
                new_step = step_classify
            else:
                new_step = step_source
        elif current_step in (step_unit, step_classify, step_source):
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
        """Determine the previous step to be switched to (by the Back button)

        :param current_step: The present step number
        :type current_step: int

        :returns: The previous step number
        :rtype: int
        """
        if current_step == step_source:
            if self.selected_mapping():
                new_step = step_classify
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
            else:
                new_step = step_category
        else:
            new_step = current_step - 1
        return new_step

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        my_keywords = {}
        if self.selected_category():
            my_keywords['category'] = self.selected_category()['id']
        if self.selected_subcategory():
            my_keywords['subcategory'] = self.selected_subcategory()['id']
        if self.selected_unit():
            my_keywords['unit'] = self.selected_unit()['id']
        if self.lstFields.currentItem():
            my_keywords['field'] = self.lstFields.currentItem().text()
        if self.leSource.text():
            my_keywords['source'] = self.leSource.text()
        if self.leSource_url.text():
            my_keywords['source_url'] = self.leSource_url.text()
        if self.leSource_scale.text():
            my_keywords['source_scale'] = self.leSource_scale.text()
        if self.leSource_date.text():
            my_keywords['source_date'] = self.leSource_date.text()
        if self.leTitle.text():
            my_keywords['title'] = self.leTitle.text()
        value_map = self.selected_mapping()
        if value_map:
            my_keywords['value_map'] = str(value_map)
        return my_keywords

    def accept(self):
        """Automatic slot executed when the Finish button is pressed.

        It will write out the keywords for the layer that is active.
        This method is based on the KeywordsDialog class.
        """
        self.keyword_io = KeywordIO()
        my_keywords = self.get_keywords()
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=my_keywords)
        except InaSAFEError, e:
            myErrorMessage = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s') % myErrorMessage.to_html())))
        if self.dock is not None:
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)
