# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'borysjurgiel.pl'
__date__ = '24/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import sys
import os
import shutil
# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

# noinspection PyPackageRequirements
from PyQt4.QtCore import Qt

from qgis.core import QgsVectorLayer

from safe.common.testing import get_qgis_app
from safe_qgis.safe_interface import unique_filename
from safe_qgis.safe_interface import TESTDATA, BOUNDDATA, HAZDATA
from safe_qgis.tools.wizard_dialog import (
    WizardDialog,
    step_source,
    step_title,
    step_classify)
from safe_qgis.utilities.keyword_io import KeywordIO


# Get QGis app handle
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def clone_csv_layer():
    """Helper function that copies a test csv layer and returns it."""
    path = 'test_buildings.csv'
    temp_path = unique_filename()
    # copy to temp file
    source_path = os.path.join(TESTDATA, path)
    shutil.copy2(source_path, temp_path)
    # return a single predefined layer
    layer = QgsVectorLayer(temp_path, '', 'delimitedtext')
    return layer


def clone_shp_layer(
        name='tsunami_polygon', include_keywords=False, directory=TESTDATA):
    """Helper function that copies a test shplayer and returns it.

    :param name: The default name for the shp layer.
    :type name: str

    :param include_keywords: Include keywords file if True.
    :type include_keywords: bool

    :param directory: Directory where the file is located.
    :type directory: str

    """
    extensions = ['.shp', '.shx', '.dbf', '.prj']
    if include_keywords:
        extensions.append('.keywords')
    temp_path = unique_filename()
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(directory, name + ext)
        if os.path.exists(src_path):
            trg_path = temp_path + ext
            shutil.copy2(src_path, trg_path)
    # return a single predefined layer
    layer = QgsVectorLayer(temp_path + '.shp', 'TestLayer', 'ogr')
    return layer


def remove_temp_file(file_path):
    """Helper function that removes temp file created during test.

    Also its keywords file will be removed.

    :param file_path: File path to be removed.
    :type file_path: str
    """
    file_path = file_path[:-4]
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.keywords']
    for ext in extensions:
        if os.path.exists(file_path + ext):
            os.remove(file_path + ext)


# noinspection PyTypeChecker
class WizardDialogTest(unittest.TestCase):

    """Test the InaSAFE wizard GUI"""

    def test_keywords_creation_wizard(self):
        """Test how the widgets work."""
        expected_category_count = 3
        expected_categories = ['exposure', 'hazard', 'aggregation']
        chosen_category = 'hazard'

        expected_subcategory_count = 4
        expected_subcategories = ['volcano', 'earthquake', 'flood', 'tsunami']
        chosen_subcategory = "tsunami"

        expected_unit_count = 3
        expected_units = ['wetdry', 'metres_depth', 'feet_depth']
        expected_chosen_unit = 'feet_depth'

        expected_field_count = 5
        expected_fields = ['OBJECTID', 'GRIDCODE', 'Shape_Leng', 'Shape_Area',
                           'Category']
        expected_chosen_field = 'GRIDCODE'

        expected_keywords = {
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'feet_depth',
            'field': 'GRIDCODE',
            'source': 'some source',
            'title': 'some title'
        }

        layer = clone_shp_layer()

        # check the environment first
        message = 'Test layer is not readable. Check environment variables.'
        self.assertIsNotNone(layer.dataProvider(), message)

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # step 1 of 7 - select category
        count = dialog.lstCategories.count()
        message = ('Invalid category count! There should be %d while there '
                   'were: %d') % (expected_category_count, count)
        self.assertEqual(count, expected_category_count, message)

        # Get all the categories given by wizards and save the 'hazard' index
        categories = []
        hazard_index = -1
        for i in range(expected_category_count):
            category_name = eval(
                dialog.lstCategories.item(i).data(Qt.UserRole))['id']
            categories.append(category_name)
            if category_name == chosen_category:
                hazard_index = i
        # Check if categories is the same with expected_categories
        message = 'Invalid categories! It should be "%s" while it was %s' % (
            expected_categories, categories)
        self.assertEqual(set(categories), set(expected_categories), message)
        # Check if the Next button state is on the right state
        message = ('Invalid Next button state in step 1! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(
            not dialog.pbnNext.isEnabled(), message)
        # Select hazard one
        dialog.lstCategories.setCurrentRow(hazard_index)
        message = ('Invalid Next button state in step 1! Still disabled after '
                   'an item selected')
        self.assertTrue(
            dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 2 of 7 - select subcategory
        # Check the number of sub categories
        count = dialog.lstSubcategories.count()
        message = ('Invalid subcategory count! There should be %d and there '
                   'were: %d') % (expected_subcategory_count, count)
        self.assertEqual(count, expected_subcategory_count, message)

        # Get all the subcategories given and save the 'tsunami' index
        subcategories = []
        tsunami_index = -1
        for i in range(expected_subcategory_count):
            subcategory_name = eval(
                dialog.lstSubcategories.item(i).data(Qt.UserRole))['id']
            subcategories.append(subcategory_name)
            if subcategory_name == chosen_subcategory:
                tsunami_index = i
        # Check if subcategories is the same with expected_subcategories
        message = ('Invalid sub categories! It should be "%s" while it was '
                   '%s') % (expected_subcategories, subcategories)
        self.assertEqual(
            set(subcategories), set(expected_subcategories), message)
        # The Next button should be on disabled state first
        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 2! Enabled while there\'s nothing selected yet')
        # Set to tsunami subcategories
        dialog.lstSubcategories.setCurrentRow(tsunami_index)
        message = ('Invalid Next button state in step 2! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click next button
        dialog.pbnNext.click()

        # step 3 of 7 - select tsunami units
        # Check if the number of unit for tsunami is 3
        count = dialog.lstUnits.count()
        message = ('Invalid unit count! There should be %d while there were: '
                   '%d') % (expected_unit_count, count)
        self.assertEqual(count, expected_unit_count, message)
        # Get all the units given and save the 'feet_depth' index
        units = []
        feet_unit_index = -1
        for i in range(expected_unit_count):
            unit_name = eval(
                dialog.lstUnits.item(i).data(Qt.UserRole))['id']
            units.append(unit_name)
            if unit_name == expected_chosen_unit:
                feet_unit_index = i
        # Check if units is the same with expected_units
        message = ('Invalid units! It should be "%s" while it was '
                   '%s') % (expected_units, units)
        self.assertEqual(
            set(expected_units), set(units), message)
        # The button should be on disabled state first
        message = ('Invalid Next button state in step 3! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(
            not dialog.pbnNext.isEnabled(), message)
        dialog.lstUnits.setCurrentRow(feet_unit_index)
        message = ('Invalid Next button state in step 3! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(
            dialog.pbnNext.isEnabled(), message)

        dialog.pbnNext.click()

        # step 4 of 7 - select data field for tsunami feet
        count = dialog.lstFields.count()
        message = ('Invalid field count! There should be %d while there were: '
                   '%d') % (expected_field_count, count)
        self.assertEqual(count, expected_field_count, message)
        # Get all the fields given and save the 'GRIDCODE' index
        fields = []
        gridcode_index = -1
        for i in range(expected_field_count):
            field_name = dialog.lstFields.item(i).text()
            fields.append(field_name)
            if field_name == expected_chosen_field:
                gridcode_index = i
        # Check if fields is the same with expected_fields
        message = ('Invalid fields! It should be "%s" while it was '
                   '%s') % (expected_fields, fields)
        self.assertEqual(
            set(expected_fields), set(fields), message)
        # The button should be on disabled first
        message = ('Invalid Next button state in step 4! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(not dialog.pbnNext.isEnabled(), message)
        dialog.lstFields.setCurrentRow(gridcode_index)
        message = ('Invalid Next button state in step 4! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click next
        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        message = ('Invalid Next button state in step 6! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        dialog.leSource.setText('some source')
        dialog.pbnNext.click()

        # step 7 of 7 - enter title
        dialog.leTitle.setText('some title')
        message = ('Invalid Next button state in step 7! Still disabled '
                   'after a text entered')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        dialog.pbnNext.click()

        # test the resulting keywords
        keyword_io = KeywordIO()
        # noinspection PyTypeChecker
        keywords = keyword_io.read_keywords(layer)

        message = 'Invalid metadata!\n Was: %s\n Should be: %s' % (
            unicode(keywords), unicode(expected_keywords))

        self.assertEqual(keywords, expected_keywords, message)

        remove_temp_file(layer.source())

    def test_existed_keywords(self):
        """Test if keywords are already exist."""
        expected_field_count = 5
        expected_fields = [
            'OBJECTID', 'GRIDCODE', 'Shape_Leng', 'Shape_Area', 'Category']
        expected_chosen_field = 'GRIDCODE'

        layer = clone_shp_layer(include_keywords=True)

        # check the environment first
        message = 'Test layer is not readable. Check environment variables.'
        self.assertIsNotNone(layer.dataProvider(), message)

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # step 1 of 7 - select category
        expected_category_text = 'hazard'
        category_text = dialog.lstCategories.currentItem().text()
        message = 'Expect category text %s but I got %s' % (
            expected_category_text, category_text)
        self.assertEqual(expected_category_text, category_text, message)

        message = ('Invalid Next button state in step 1! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 2 of 7 - select subcategory
        # noinspection PyTypeChecker
        expected_subcategory_text = 'tsunami'
        subcategory_text = dialog.lstSubcategories.currentItem().text()
        message = 'Expect subcategory text %s but I got %s' % (
            expected_subcategory_text, subcategory_text)
        self.assertEqual(expected_subcategory_text, subcategory_text, message)

        message = ('Invalid Next button state in step 2! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 3 of 7 - select tsunami units
        expected_unit_text = 'metres'
        unit_text = dialog.lstUnits.currentItem().text()
        message = 'Expect unit text %s but I got %s' % (
            expected_unit_text, unit_text)
        self.assertEqual(expected_unit_text, unit_text, message)

        message = ('Invalid Next button state in step 2! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 4 of 7 - select data field for tsunami feet
        count = dialog.lstFields.count()
        message = ('Invalid field count! There should be %d while there were: '
                   '%d') % (expected_field_count, count)
        self.assertEqual(count, expected_field_count, message)
        # Get all the fields given and save the 'GRIDCODE' index
        fields = []
        gridcode_index = -1
        for i in range(expected_field_count):
            field_name = dialog.lstFields.item(i).text()
            fields.append(field_name)
            if field_name == expected_chosen_field:
                gridcode_index = i
        # Check if fields is the same with expected_fields
        message = ('Invalid fields! It should be "%s" while it was '
                   '%s') % (expected_fields, fields)
        self.assertEqual(
            set(expected_fields), set(fields), message)
        # The button should be on disabled first
        message = ('Invalid Next button state in step 4! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(not dialog.pbnNext.isEnabled(), message)
        dialog.lstFields.setCurrentRow(gridcode_index)
        message = ('Invalid Next button state in step 4! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click next
        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        message = ('Invalid Next button state in step 6! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        message = 'Source should be empty'
        self.assertEqual(dialog.leSource.text(), '', message)
        message = 'Source Url should be empty'
        self.assertEqual(dialog.leSource_url.text(), '', message)
        message = 'Source Date should be empty'
        self.assertEqual(dialog.leSource_date.text(), '', message)
        message = 'Source Scale should be empty'
        self.assertEqual(dialog.leSource_scale.text(), '', message)
        dialog.pbnNext.click()

        # step 7 of 7 - enter title
        message = 'Title should be %s but I got %s' % (
            dialog.layer.name(), dialog.leTitle.text())
        self.assertEqual(dialog.layer.name(), dialog.leTitle.text(), message)
        message = ('Invalid Next button state in step 7! Still disabled '
                   'after a text entered')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        dialog.pbnNext.click()

        remove_temp_file(layer.source())

    def test_existing_complex_keywords(self):
        layer = clone_shp_layer(include_keywords=True)
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)
        dialog.lstCategories.setCurrentRow(1)  # hazard
        dialog.pbnNext.click()
        dialog.lstSubcategories.setCurrentRow(3)  # volcano
        dialog.pbnNext.click()
        dialog.lstUnits.setCurrentRow(0)  # volcano categorical
        dialog.pbnNext.click()
        dialog.lstFields.setCurrentRow(1)  # GRIDCODE
        dialog.pbnNext.click()
        unit = dialog.selected_unit()
        default_classes = unit['classes']
        unassigned_values = []  # no need to check actually, not save in
        # file
        assigned_values = {
            'high': ['4.0', '5.0'],
            'medium': ['3.0'],
            'low': ['2.0']
        }
        dialog.populate_classified_values(
            unassigned_values, assigned_values, default_classes)
        dialog.pbnNext.click()

        source = 'Source'
        source_scale = 'Source Scale'
        source_url = 'Source Url'
        source_date = 'Source Date'

        dialog.leSource.setText(source)
        dialog.leSource_scale.setText(source_scale)
        dialog.leSource_url.setText(source_url)
        dialog.leSource_date.setText(source_date)
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # finish

        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # step 1 of 7 - select category
        expected_category_text = 'hazard'
        category_text = dialog.lstCategories.currentItem().text()
        message = 'Expect category text %s but I got %s' % (
            expected_category_text, category_text)
        self.assertEqual(expected_category_text, category_text, message)

        # Click Next
        dialog.pbnNext.click()

        # step 2 of 7 - select subcategory
        # noinspection PyTypeChecker
        expected_subcategory_text = 'volcano'
        subcategory_text = dialog.lstSubcategories.currentItem().text()
        message = 'Expect subcategory text %s but I got %s' % (
            expected_subcategory_text, subcategory_text)
        self.assertEqual(expected_subcategory_text, subcategory_text, message)

        # Click Next
        dialog.pbnNext.click()

        # step 3 of 7 - select volcano units
        expected_unit_text = 'volcano categorical'
        unit_text = dialog.lstUnits.currentItem().text()
        message = 'Expect unit text %s but I got %s' % (
            expected_unit_text, unit_text)
        self.assertEqual(expected_unit_text, unit_text, message)

        # Click Next
        dialog.pbnNext.click()

        # step 4 of 7 - select field
        expected_unit_text = 'GRIDCODE'
        unit_text = dialog.lstFields.currentItem().text()
        message = 'Expect unit text %s but I got %s' % (
            expected_unit_text, unit_text)
        self.assertEqual(expected_unit_text, unit_text, message)

        # Click Next
        dialog.pbnNext.click()

        for index in range(dialog.lstUniqueValues.count()):
            message = ('%s Should be in unassigned values' %
                       dialog.lstUniqueValues.item(index).text())
            self.assertIn(
                dialog.lstUniqueValues.item(index).text(),
                unassigned_values,
                message)
        real_assigned_values = dialog.selected_mapping()
        self.assertDictEqual(real_assigned_values, assigned_values)

        # Click Next
        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        message = ('Invalid Next button state in step 6! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        message = 'Source should be %s' % source
        self.assertEqual(dialog.leSource.text(), source, message)
        message = 'Source Url should be %s' % source_url
        self.assertEqual(dialog.leSource_url.text(), source_url, message)
        message = 'Source Date should be %s' % source_date
        self.assertEqual(dialog.leSource_date.text(), source_date, message)
        message = 'Source Scale should be %s' % source_scale
        self.assertEqual(dialog.leSource_scale.text(), source_scale, message)
        dialog.pbnNext.click()

        dialog.pbnCancel.click()

        remove_temp_file(layer.source())

    # noinspection PyTypeChecker
    def test_existing_aggregation_keywords(self):
        """Test for case existing keywords in aggregation layer."""
        layer = clone_shp_layer(
            name='kabupaten_jakarta',
            include_keywords=True,
            directory=BOUNDDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)
        category = dialog.lstCategories.currentItem().text()
        expected_category = 'aggregation'
        message = 'Expected %s but I got %s.' % (expected_category, category)
        self.assertEqual(expected_category, category, message)

        dialog.pbnNext.click()

        expected_aggregation_attribute = 'KAB_NAME'
        aggregation_attribute = dialog.lstFields.currentItem().text()
        message = 'Expected %s but I got %s.' % (
            expected_aggregation_attribute, aggregation_attribute)
        self.assertEqual(
            expected_aggregation_attribute, aggregation_attribute, message)

        dialog.pbnNext.click()

        expected_aggregation_attributes = {
            'elderly ratio attribute': 'Use default',
            'youth ratio default': 0.26,
            'elderly ratio default': 0.08,
            'adult ratio attribute': 'Use default',
            'female ratio attribute': 'Use default',
            'youth ratio attribute': 'Use default',
            'female ratio default': 0.5,
            'adult ratio default': 0.66
        }
        aggregation_attributes = dialog.get_aggregation_attributes()
        message = 'Expected %s but I got %s.' % (
            expected_aggregation_attributes, aggregation_attributes)
        self.assertDictEqual(
            expected_aggregation_attributes, aggregation_attributes, message)
        dialog.cboFemaleRatioAttribute.setCurrentIndex(2)
        expected_female_attribute_key = 'PEREMPUAN'
        female_attribute_key = dialog.cboFemaleRatioAttribute.currentText()
        message = 'Expected %s but I got %s.' % (
            expected_female_attribute_key, female_attribute_key)
        self.assertEqual(
            expected_female_attribute_key, female_attribute_key, message)
        is_enabled = dialog.dsbFemaleRatioDefault.isEnabled()
        message = 'Expected disabled but I got enabled.'
        self.assertEqual(is_enabled, False, message)

        remove_temp_file(layer.source())

    # noinspection PyTypeChecker
    def test_unit_building_generic(self):
        """Test for case existing building generic unit for structure."""
        layer = clone_shp_layer(
            name='building_Maumere',
            include_keywords=True,
            directory=TESTDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        dialog.pbnNext.click()  # go to subcategory step 2
        dialog.pbnNext.click()  # go to unit step 3
        dialog.lstUnits.setCurrentRow(1)  # select no type
        dialog.pbnNext.click()  # should be in step source
        current_index = dialog.stackedWidget.currentIndex() + 1
        expected_current_index = step_source
        message = 'Expected %s but I got %s.' % (
            expected_current_index, current_index)
        self.assertEqual(expected_current_index, current_index, message)
        dialog.pbnNext.click()  # should be in step title
        current_index = dialog.stackedWidget.currentIndex() + 1
        expected_current_index = step_title
        message = 'Expected %s but I got %s.' % (
            expected_current_index, current_index)
        self.assertEqual(expected_current_index, current_index, message)

        dialog.pbnNext.click()  # finishing

        remove_temp_file(layer.source())

    def test_default_attributes_value(self):
        """Checking that default attributes is set to the CIA's one."""
        layer = clone_shp_layer(
            name='kecamatan_jakarta',
            include_keywords=True,
            directory=BOUNDDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        dialog.pbnNext.click()  # choose aggregation go to field step
        dialog.pbnNext.click()  # choose KEC_NAME go to aggregation step

        ratio_attribute = dialog.cboFemaleRatioAttribute.currentText()
        message = 'Expected Use default but I got %s' % ratio_attribute
        self.assertEqual('Use default', ratio_attribute, message)

        ratio_attribute = dialog.cboElderlyRatioAttribute.currentText()
        message = 'Expected Use default but I got %s' % ratio_attribute
        self.assertEqual('Use default', ratio_attribute, message)

        ratio_attribute = dialog.cboAdultRatioAttribute.currentText()
        message = 'Expected Use default but I got %s' % ratio_attribute
        self.assertEqual('Use default', ratio_attribute, message)

        ratio_attribute = dialog.cboYouthRatioAttribute.currentText()
        message = 'Expected Use default but I got %s' % ratio_attribute
        self.assertEqual('Use default', ratio_attribute, message)

        default_value = dialog.dsbFemaleRatioDefault.value()
        expected_default_value = 0.50
        message = ('Expected %s but I got %s' % (
            expected_default_value, default_value))
        self.assertEqual(expected_default_value, default_value, message)

        default_value = dialog.dsbYouthRatioDefault.value()
        expected_default_value = 0.26
        message = ('Expected %s but I got %s' % (
            expected_default_value, default_value))
        self.assertEqual(expected_default_value, default_value, message)

        default_value = dialog.dsbAdultRatioDefault.value()
        expected_default_value = 0.66
        message = ('Expected %s but I got %s' % (
            expected_default_value, default_value))
        self.assertEqual(expected_default_value, default_value, message)

        default_value = dialog.dsbElderlyRatioDefault.value()
        expected_default_value = 0.08
        message = ('Expected %s but I got %s' % (
            expected_default_value, default_value))
        self.assertEqual(expected_default_value, default_value, message)

        remove_temp_file(layer.source())

    def test_unknown_unit(self):
        """Checking that it works for unknown unit."""
        layer = clone_shp_layer(
            name='Marapi_evac_zone_3000m',
            include_keywords=True,
            directory=HAZDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        dialog.pbnNext.click()  # choose hazard go to subcategory  step
        dialog.pbnNext.click()  # choose volcano  go to unit step
        dialog.lstUnits.setCurrentRow(0)  # Choose volcano categorical
        expected_unit = 'volcano categorical'
        unit = dialog.lstUnits.currentItem().text()
        message = ('Expected %s but I got %s' % (
            expected_unit, unit))
        self.assertEqual(expected_unit, unit, message)

        dialog.pbnNext.click()  # choose volcano  go to field step
        dialog.lstFields.setCurrentRow(0)  # Choose Radius
        expected_fields = 'Radius'
        fields = dialog.lstFields.currentItem().text()
        message = ('Expected %s but I got %s' % (
            expected_fields, fields))
        self.assertEqual(expected_fields, fields, message)

        dialog.pbnNext.click()  # choose volcano  go to classify step
        current_step = dialog.stackedWidget.currentIndex() + 1
        expected_step = step_classify
        message = ('Expected %s but I got %s' % (
            expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

        dialog.pbnNext.click()  # choose volcano  go to source step
        current_step = dialog.stackedWidget.currentIndex() + 1
        expected_step = step_source
        message = ('Expected %s but I got %s' % (
            expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

        dialog.pbnNext.click()  # choose volcano  go to title step
        current_step = dialog.stackedWidget.currentIndex() + 1
        expected_step = step_title
        message = ('Expected %s but I got %s' % (
            expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

        remove_temp_file(layer.source())

    def test_point_layer(self):
        """Wizard for point layer."""
        layer = clone_shp_layer(
            name='Marapi',
            include_keywords=True,
            directory=HAZDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        dialog.pbnNext.click()  # choose hazard go to subcategory  step
        dialog.pbnNext.click()  # choose volcano  go to source step

        current_step = dialog.stackedWidget.currentIndex() + 1
        expected_step = step_source
        message = ('Expected %s but I got %s' % (
            expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

        dialog.pbnNext.click()  # choose volcano  go to title step

        current_step = dialog.stackedWidget.currentIndex() + 1
        expected_step = step_title
        message = ('Expected %s but I got %s' % (
            expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

        remove_temp_file(layer.source())

    def test_auto_select_one_item(self):
        """Test auto select if there is only one item in a list."""
        layer = clone_shp_layer(
            name='Marapi_evac_zone_3000m',
            include_keywords=True,
            directory=HAZDATA)
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        dialog.pbnNext.click()  # choose hazard go to subcategory  step
        dialog.pbnNext.click()  # choose volcano  go to unit  step

        message = 'It should auto select, but it does not.'
        self.assertTrue(dialog.lstUnits.currentRow() == 0, message)
        num_item = dialog.lstUnits.count()
        message = 'There is should be only one item, I got %s' % num_item
        self.assertTrue(num_item == 1, message)

        dialog.pbnNext.click()  # choose volcano  go to field  step
        message = 'It should auto select, but it does not.'
        self.assertTrue(dialog.lstFields.currentRow() == 0, message)
        num_item = dialog.lstFields.count()
        message = 'There is should be only one item, I got %s' % num_item
        self.assertTrue(num_item == 1, message)

        remove_temp_file(layer.source())
    # def test_integrated_point(self):
    #     """Test for point layer and all possibilities."""
    #     layer = clone_shp_layer(
    #         name='Marapi',
    #         directory=HAZDATA)
    #     dialog = WizardDialog(PARENT, IFACE, None, layer)


if __name__ == '__main__':
    suite = unittest.makeSuite(WizardDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
