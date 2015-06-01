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

import unittest
import sys
import os
import shutil

from qgis.core import QgsMapLayerRegistry
from PyQt4 import QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import Qt

# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe.impact_functions import register_impact_functions
from safe.common.utilities import temp_dir
from safe.test.utilities import (
    clone_raster_layer,
    clone_shp_layer,
    get_qgis_app,
    test_data_path)

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.tools.wizard_dialog
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.wizard_dialog import (
    WizardDialog,
    step_kw_source,
    step_kw_layermode,
    step_kw_title,
    step_kw_classification,
    step_kw_classify,
    step_kw_hazard_category,
    step_kw_subcategory,
    step_kw_unit,
    step_kw_extrakeywords,
    step_kw_aggregation,
    step_kw_field)
from safe.utilities.keyword_io import KeywordIO


# noinspection PyTypeChecker
class WizardDialogTest(unittest.TestCase):
    """Test the InaSAFE wizard GUI"""
    def setUp(self):
        # register impact functions
        register_impact_functions()

    def tearDown(self):
        """Run after each test."""
        # Remove the mess that we made on each test
        shutil.rmtree(temp_dir(sub_dir='test'))

    def check_list(self, expected_list, list_widget):
        """Helper function to check that list_widget is equal to expected_list.

        :param expected_list: List of expected values to be found.
        :type expected_list: list

        :param list_widget: List widget that wants to be checked.
        :type expected_list: QListWidget
        """
        real_list = []
        for i in range(list_widget.count()):
            real_list.append(list_widget.item(i).text())
        message = ('Expected %s but I got %s' % (expected_list, real_list))
        self.assertItemsEqual(expected_list, real_list, message)

    def check_current_step(self, expected_step, dialog):
        """Helper function to check the current step is expected_step

        :param expected_step: The expected current step.
        :type expected_step: int

        :param dialog: The dialog that contains a wizard.
        :type dialog: WizardDialog
        """
        current_step = dialog.get_current_step()
        message = ('Expected %s but I got %s' % (expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

    def check_current_text(self, expected_text, list_widget):
        """Check the current text in list widget is expected_text

        :param expected_text: The expected current step.
        :type expected_text: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        # noinspection PyUnresolvedReferences
        current_text = list_widget.currentItem().text()
        message = ('Expected %s but I got %s' % (expected_text, current_text))
        self.assertEqual(expected_text, current_text, message)

    # noinspection PyUnresolvedReferences
    def select_from_list_widget(self, option, list_widget):
        """Helper function to select option from list_widget

        :param option: Option to be chosen
        :type option: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == option:
                list_widget.setCurrentRow(i)
                return
        message = 'There is no %s in the list widget' % option
        raise Exception(message)

    def test_keywords_creation_wizard(self):
        """Test how the widgets work."""
        expected_category_count = 3
        expected_categories = ['hazard', 'exposure', 'aggregation']
        chosen_category = 'hazard'

        expected_hazard_category_count = 2
        expected_hazard_categories = ['Single Event', 'Multiple Event']
        chosen_hazard_category = 'Single Event'

        expected_subcategory_count = 6
        # expected_subcategories = ['flood', 'tsunami']
        # Notes: IS, the generic IF makes the expected sub categories like this
        expected_subcategories = [
            'flood',
            'tsunami',
            'earthquake',
            'volcano',
            'volcanic_ash',
            'generic']
        chosen_subcategory = 'flood'

        expected_mode_count = 1
        expected_modes = ['classified']

        expected_field_count = 6
        expected_fields = ['OBJECTID', 'KAB_NAME', 'KEC_NAME', 'KEL_NAME',
                           'RW', 'FLOODPRONE']
        expected_chosen_field = 'FLOODPRONE'

        expected_classification_count = 3
        expected_classification = 'flood vector hazard classes'

        expected_keywords = {
            'layer_geometry': 'polygon',
            'layer_purpose': 'hazard',
            'hazard_category': 'single_event',
            'hazard': 'flood',
            'field': 'FLOODPRONE',
            'layer_mode': 'classified',
            'vector_hazard_classification':
                'flood_vector_hazard_classes',
            'value_map': {'wet': ['YES'], 'dry': ['NO']},
            'affected_field': 'FLOODPRONE',
            'affected_value': 'YES',
            'hazard_zone_field': 'FLOODPRONE',
            'source': 'some source',
            'title': 'some title'
        }

        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            include_keywords=True,
            source_directory=test_data_path('hazard'))

        # check the environment first
        message = 'Test layer is not readable. Check environment variables.'
        self.assertIsNotNone(layer.dataProvider(), message)

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 of 9 - select category
        count = dialog.lstCategories.count()
        message = ('Invalid category count! There should be %d while there '
                   'were: %d') % (expected_category_count, count)
        self.assertEqual(count, expected_category_count, message)

        # Get all the categories given by wizards and save the 'hazard' index
        categories = []
        hazard_index = -1
        for i in range(expected_category_count):
            # pylint: disable=eval-used
            category_name = eval(
                dialog.lstCategories.item(i).data(Qt.UserRole))['key']
            # pylint: enable=eval-used
            categories.append(category_name)
            if category_name == chosen_category:
                hazard_index = i
        # Check if categories is the same with expected_categories
        message = 'Invalid categories! It should be "%s" while it was %s' % (
            expected_categories, categories)
        self.assertItemsEqual(categories, expected_categories, message)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        message = ('Invalid Next button state in step 1! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.lstCategories.selectedItems()), message)
        # Select hazard one
        dialog.lstCategories.setCurrentRow(hazard_index)
        message = ('Invalid Next button state in step 1! Still disabled after '
                   'an item selected')
        self.assertTrue(
            dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 2 of 9 - select hazard category
        count = dialog.lstHazardCategories.count()
        message = ('Invalid hazard category count! There should be %d while '
                   'there were: %d') % (expected_hazard_category_count, count)
        self.assertEqual(count, expected_hazard_category_count, message)

        # Get all the categories given by wizards and save the 'hazard' index
        hazard_categories = []
        scenario_index = -1
        for i in range(expected_hazard_category_count):
            # pylint: disable=eval-used
            hazard_category_name = eval(
                dialog.lstHazardCategories.item(i).data(Qt.UserRole))['name']
            # pylint: enable=eval-used
            hazard_categories.append(hazard_category_name)
            if hazard_category_name == chosen_hazard_category:
                scenario_index = i
        # Check if categories is the same with expected_categories
        message = ('Invalid hazard categories! It should be "%s" while it'
                   'was %s' % (expected_hazard_categories, hazard_categories))
        self.assertItemsEqual(
            hazard_categories, expected_hazard_categories, message)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        message = ('Invalid Next button state in step 2! Enabled while '
                   'there\'s nothing selected yet')
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.lstHazardCategories.selectedItems()), message)
        # Select hazard one
        dialog.lstHazardCategories.setCurrentRow(scenario_index)
        message = ('Invalid Next button state in step 2! Still disabled after '
                   'an item selected')
        self.assertTrue(
            dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 3 of 9 - select subcategory
        # Check the number of sub categories
        count = dialog.lstSubcategories.count()
        message = ('Invalid subcategory count! There should be %d and there '
                   'were: %d') % (expected_subcategory_count, count)
        self.assertEqual(count, expected_subcategory_count, message)

        # Get all the subcategories given and save the 'flood' index
        subcategories = []
        tsunami_index = -1
        for i in range(expected_subcategory_count):
            # pylint: disable=eval-used
            subcategory_name = eval(
                dialog.lstSubcategories.item(i).data(Qt.UserRole))['key']
            # pylint: enable=eval-used
            subcategories.append(subcategory_name)
            if subcategory_name == chosen_subcategory:
                tsunami_index = i
        # Check if subcategories is the same with expected_subcategories
        message = ('Invalid sub categories! It should be "%s" while it was '
                   '%s') % (expected_subcategories, subcategories)
        self.assertItemsEqual(subcategories, expected_subcategories, message)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.lstSubcategories.selectedItems()),
            'Invalid Next button state in step 3! '
            'Enabled while there\'s nothing selected yet')
        # Set to tsunami subcategories
        dialog.lstSubcategories.setCurrentRow(tsunami_index)
        message = ('Invalid Next button state in step 3! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click next button
        dialog.pbnNext.click()

        # step 4 of 9 - select classified mode
        # Check if the number of modes is 2
        self.check_current_step(step_kw_layermode, dialog)
        count = dialog.lstLayerModes.count()
        message = ('Invalid layer modes count! There should be %d while '
                   'there were: %d') % (expected_mode_count, count)
        self.assertEqual(count, expected_mode_count, message)
        # Get all the modes given and save the classified index
        modes = []
        for i in range(expected_mode_count):
            # pylint: disable=eval-used
            mode_name = eval(
                dialog.lstLayerModes.item(i).data(Qt.UserRole))['key']
            # pylint: enable=eval-used
            modes.append(mode_name)
        # Check if units is the same with expected_units
        message = ('Invalid modes! It should be "%s" while it was '
                   '%s') % (expected_modes, modes)
        self.assertItemsEqual(expected_modes, modes, message)

        dialog.pbnNext.click()

        # step 5 of 9 - select data field for flood
        self.check_current_step(step_kw_field, dialog)
        count = dialog.lstFields.count()
        message = ('Invalid field count! There should be %d while there were: '
                   '%d') % (expected_field_count, count)
        self.assertEqual(count, expected_field_count, message)
        # Get all the fields given and save the 'FLOODPRONE' index
        fields = []
        floodprone_index = -1
        for i in range(expected_field_count):
            field_name = dialog.lstFields.item(i).text()
            fields.append(field_name)
            if field_name == expected_chosen_field:
                floodprone_index = i
        # Check if fields is the same with expected_fields
        message = ('Invalid fields! It should be "%s" while it was '
                   '%s') % (expected_fields, fields)
        self.assertItemsEqual(expected_fields, fields, message)
        dialog.lstFields.setCurrentRow(floodprone_index)
        message = ('Invalid Next button state in step 5! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click next
        dialog.pbnNext.click()

        # step 6 of 9 - select classification scheme
        # Check if the number of classifications is 1
        count = dialog.lstClassifications.count()
        message = ('Invalid classification count! There should be %d while '
                   'there were: %d') % (expected_classification_count, count)
        self.assertEqual(count, expected_classification_count, message)
        self.check_current_text(expected_classification,
                                dialog.lstClassifications)
        # Click next
        dialog.pbnNext.click()

        # Click next
        dialog.pbnNext.click()

        # step 8 of 10 - set extra keywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(5)
        dialog.cboExtraKeyword2.setCurrentIndex(1)
        dialog.cboExtraKeyword3.setCurrentIndex(5)

        # Click next
        dialog.pbnNext.click()

        # step 9 of 10 - enter source
        message = ('Invalid Next button state in step 8! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        dialog.leSource.setText('some source')
        dialog.pbnNext.click()

        # step 10 of 10 - enter title
        dialog.leTitle.setText('some title')
        message = ('Invalid Next button state in step 9! Still disabled '
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

    def test_existing_keywords(self):
        """Test if keywords already exist."""
        expected_field_count = 6

        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            include_keywords=True,
            source_directory=test_data_path('hazard'))

        # check the environment first
        message = 'Test layer is not readable. Check environment variables.'
        self.assertIsNotNone(layer.dataProvider(), message)

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 - select layer purpose
        self.check_current_text('hazard', dialog.lstCategories)

        message = ('Invalid Next button state in step 1! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 2 - select hazard category
        self.check_current_text('Single Event', dialog.lstHazardCategories)

        message = ('Invalid Next button state in step 2! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 3 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text('flood', dialog.lstSubcategories)

        message = ('Invalid Next button state in step 3! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 4 - select layer mode
        # noinspection PyTypeChecker
        self.check_current_text('classified', dialog.lstLayerModes)

        message = ('Invalid Next button state in step 4! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # step 5 - select field
        # noinspection PyTypeChecker
        self.check_current_text('FLOODPRONE', dialog.lstFields)

        message = ('Invalid Next button state in step 5! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        count = dialog.lstFields.count()
        message = ('Invalid field count! There should be %d while there were: '
                   '%d') % (expected_field_count, count)
        self.assertEqual(count, expected_field_count, message)

        # Click Next
        dialog.pbnNext.click()

        # step 6 - select tsunami classification
        self.check_current_text('flood vector hazard classes',
                                dialog.lstClassifications)

        message = ('Invalid Next button state in step 6! Still disabled after '
                   'an item selected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        # Click Next
        dialog.pbnNext.click()

        # Click Next
        dialog.pbnNext.click()

        # step 8 - assign additional keywords
        expected_field = 'FLOODPRONE'
        indx = dialog.cboExtraKeyword1.findData(expected_field, Qt.UserRole)
        dialog.cboExtraKeyword1.setCurrentIndex(indx)
        message = 'The sixth field shoud be %s' % expected_field
        self.assertEqual(indx, 5, message)

        expected_value = 'YES'
        indx = dialog.cboExtraKeyword2.findData(expected_value, Qt.UserRole)
        dialog.cboExtraKeyword2.setCurrentIndex(indx)
        message = 'The second value shoud be %s' % expected_value
        self.assertEqual(indx, 1, message)

        expected_field = 'FLOODPRONE'
        indx = dialog.cboExtraKeyword3.findData(expected_field, Qt.UserRole)
        dialog.cboExtraKeyword3.setCurrentIndex(indx)
        message = 'The sixth field shoud be %s' % expected_field
        self.assertEqual(indx, 5, message)

        message = ('Invalid Next button state in step 8! Still disabled after '
                   'all fields are assigned')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        # Click Next
        dialog.pbnNext.click()

        # step 9 - enter source
        message = ('Invalid Next button state in step 8! Disabled while '
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

        # step 10 - enter title
        message = 'Title should be %s but I got %s' % (
            dialog.layer.name(), dialog.leTitle.text())
        self.assertEqual(dialog.layer.name(), dialog.leTitle.text(), message)
        message = ('Invalid Next button state in step 9! Still disabled '
                   'after a text entered')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)
        dialog.pbnNext.click()

    def test_existing_complex_keywords(self):
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # select hazard
        self.select_from_list_widget('hazard', dialog.lstCategories)
        dialog.pbnNext.click()

        # select multiple_event
        self.select_from_list_widget('Multiple Event',
                                     dialog.lstHazardCategories)
        dialog.pbnNext.click()

        # select volcano
        self.select_from_list_widget('volcano', dialog.lstSubcategories)
        dialog.pbnNext.click()

        # select volcano classified mode
        self.select_from_list_widget('classified', dialog.lstLayerModes)
        dialog.pbnNext.click()

        # select KRB field
        self.select_from_list_widget('KRB', dialog.lstFields)
        dialog.pbnNext.click()

        # select volcano vector hazard classes classification
        self.select_from_list_widget('volcano vector hazard classes',
                                     dialog.lstClassifications)
        dialog.pbnNext.click()

        # select mapping
        classification = dialog.selected_classification()
        default_classes = classification['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'low': ['Kawasan Rawan Bencana I'],
            'medium': ['Kawasan Rawan Bencana II'],
            'high': ['Kawasan Rawan Bencana III']
        }
        dialog.populate_classified_values(
            unassigned_values, assigned_values, default_classes)
        dialog.pbnNext.click()

        # select additional keywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        first_field = 'KRB'
        indx = dialog.cboExtraKeyword1.findData(first_field, Qt.UserRole)
        dialog.cboExtraKeyword1.setCurrentIndex(indx)
        message = 'The first field shoud be %s' % first_field
        self.assertEqual(indx, 0, message)

        third_field = 'volcano'
        indx = dialog.cboExtraKeyword2.findData(third_field, Qt.UserRole)
        dialog.cboExtraKeyword2.setCurrentIndex(indx)
        message = 'The third field shoud be %s' % third_field
        self.assertEqual(indx, 2, message)

        dialog.pbnNext.click()

        self.check_current_step(step_kw_source, dialog)
        source = 'Source'
        source_scale = 'Source Scale'
        source_url = 'Source Url'
        source_date = 'Source Date'
        source_license = 'Source License'

        dialog.leSource.setText(source)
        dialog.leSource_scale.setText(source_scale)
        dialog.leSource_url.setText(source_url)
        dialog.leSource_date.setText(source_date)
        dialog.leSource_license.setText(source_license)
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # finish

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 - select layer purpose
        self.check_current_text('hazard', dialog.lstCategories)

        # Click Next
        dialog.pbnNext.click()

        # step 2 - select hazard category
        self.check_current_text('Multiple Event', dialog.lstHazardCategories)

        # Click Next
        dialog.pbnNext.click()

        # step 3 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text('volcano', dialog.lstSubcategories)

        # Click Next
        dialog.pbnNext.click()

        # step - select layer mode
        self.check_current_text('classified', dialog.lstLayerModes)

        # Click Next
        dialog.pbnNext.click()

        # step 5 - select field
        self.check_current_text('KRB', dialog.lstFields)

        # Click Next
        dialog.pbnNext.click()

        # step 6 - select classification
        self.check_current_text('volcano vector hazard classes',
                                dialog.lstClassifications)

        # Click Next
        dialog.pbnNext.click()

        # step 7 - select mapping
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

        # step 8 - additional keywords
        message = ('Invalid Next button state in step 8! Disabled while '
                   'all data should be autoselected')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        # Click Next
        dialog.pbnNext.click()

        # step 9 - enter source
        self.check_current_step(step_kw_source, dialog)
        message = ('Invalid Next button state in step 9! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        message = 'Source should be %s' % source
        self.assertEqual(dialog.leSource.text(), source, message)
        message = 'Source Url should be %s' % source_url
        self.assertEqual(dialog.leSource_url.text(), source_url, message)
        message = 'Source Scale should be %s' % source_scale
        self.assertEqual(dialog.leSource_scale.text(), source_scale, message)
        message = 'Source Date should be %s' % source_date
        self.assertEqual(dialog.leSource_date.text(), source_date, message)
        message = 'Source License should be %s' % source_license
        self.assertEqual(dialog.leSource_license.text(),
                         source_license, message)
        dialog.pbnNext.click()

        dialog.pbnCancel.click()

    # noinspection PyTypeChecker
    def test_existing_aggregation_keywords(self):
        """Test for case existing keywords in aggregation layer."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        category = dialog.lstCategories.currentItem().text()
        expected_category = 'aggregation'
        message = 'Expected %s but I got %s.' % (expected_category, category)
        self.assertEqual(expected_category, category, message)

        dialog.pbnNext.click()

        self.check_current_text('KAB_NAME', dialog.lstFields)

        dialog.pbnNext.click()

        expected_aggregation_attributes = {
            'elderly ratio attribute': 'Global default',
            'youth ratio default': 0.26,
            'elderly ratio default': 0.08,
            'adult ratio attribute': 'Global default',
            'female ratio attribute': 'PEREMPUAN',
            'youth ratio attribute': 'Global default',
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

    # noinspection PyTypeChecker
    def test_unit_building_generic(self):
        """Test for case existing building generic unit for structure."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=test_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # go to subcategory
        dialog.pbnNext.click()  # go to layer mode
        dialog.lstLayerModes.setCurrentRow(0)  # select classified
        dialog.pbnNext.click()  # go to extra keywords

        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(1)  # choose TYPE
        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(step_kw_source, dialog)
        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(step_kw_title, dialog)

        dialog.pbnNext.click()  # finishing

    def test_default_attributes_value(self):
        """Checking that default attributes is set to the CIA's one."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose aggregation go to field step
        dialog.pbnNext.click()  # choose KAB_NAME go to aggregation step

        ratio_attribute = dialog.cboElderlyRatioAttribute.currentText()
        message = 'Expected Global default but I got %s' % ratio_attribute
        self.assertEqual('Global default', ratio_attribute, message)

        ratio_attribute = dialog.cboAdultRatioAttribute.currentText()
        message = 'Expected Global default but I got %s' % ratio_attribute
        self.assertEqual('Global default', ratio_attribute, message)

        ratio_attribute = dialog.cboYouthRatioAttribute.currentText()
        message = 'Expected Global default but I got %s' % ratio_attribute
        self.assertEqual('Global default', ratio_attribute, message)

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

    def test_unknown_unit(self):
        """Checking that it works for unknown unit."""
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose multiple event
        dialog.pbnNext.click()  # choose volcano
        dialog.lstUnits.setCurrentRow(1)
        self.check_current_text('classified', dialog.lstLayerModes)
        dialog.pbnNext.click()  # choose classified

        dialog.lstFields.setCurrentRow(0)  # Choose KRB
        self.check_current_text('KRB', dialog.lstFields)
        dialog.pbnNext.click()  # choose KRB

        # check if in step classification
        self.check_current_step(step_kw_classification, dialog)
        dialog.pbnNext.click()  # accept classification

        # check if in step classify
        self.check_current_step(step_kw_classify, dialog)
        dialog.pbnNext.click()  # accept mapping

        # check if in step extra keywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(0)
        dialog.cboExtraKeyword2.setCurrentIndex(2)
        dialog.pbnNext.click()  # accept extra keywords

        # check if in step source
        self.check_current_step(step_kw_source, dialog)
        dialog.pbnNext.click()  # accept source

        # check if in step title
        self.check_current_step(step_kw_title, dialog)

    def test_point_layer(self):
        """Wizard for point layer."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose multiple event
        dialog.pbnNext.click()  # choose volcano
        dialog.lstLayerModes.setCurrentRow(0)  # choose none
        dialog.pbnNext.click()  # choose none
        dialog.cboExtraKeyword1.setCurrentIndex(4)  # choose NAME
        dialog.pbnNext.click()  # choose NAME

        # check if in step source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnNext.click()  # choose volcano  go to title step

        # check if in step title
        self.check_current_step(step_kw_title, dialog)
        dialog.accept()

    def test_auto_select_one_item(self):
        """Test auto select if there is only one item in a list."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=test_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose exposure
        message = 'It should auto select, but it does not.'
        self.assertTrue(dialog.lstSubcategories.currentRow() == 0, message)
        num_item = dialog.lstSubcategories.count()
        message = 'There is should be only one item, I got %s' % num_item
        self.assertTrue(num_item == 1, message)

    def test_integrated_point(self):
        """Test for point layer and all possibilities."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['hazard', 'exposure']
        self.check_list(expected_categories, dialog.lstCategories)

        self.select_from_list_widget('hazard', dialog.lstCategories)

        self.check_current_text('hazard', dialog.lstCategories)

        dialog.pbnNext.click()  # go to hazard category

        expected_hazard_categories = ['Multiple Event']
        self.check_list(expected_hazard_categories, dialog.lstHazardCategories)

        self.check_current_text('Multiple Event', dialog.lstHazardCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(step_kw_subcategory, dialog)

        expected_subcategories = ['volcano']
        self.check_list(expected_subcategories, dialog.lstSubcategories)

        self.check_current_text('volcano', dialog.lstSubcategories)

        dialog.pbnNext.click()  # go to layer mode

        self.check_current_step(step_kw_layermode, dialog)
        dialog.lstLayerModes.setCurrentRow(0)  # select the None mode

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(4)
        expected_field = 'NAME (String)'
        actual_field = dialog.cboExtraKeyword1.currentText()
        message = ('Invalid volcano name field! There should be '
                   '%s while there were: %s') % (expected_field, actual_field)
        self.assertEqual(actual_field, expected_field, message)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(step_kw_title, dialog)

        dialog.pbnCancel.click()

    def test_integrated_raster(self):
        """Test for raster layer and all possibilities."""
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=test_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['hazard', 'exposure']
        self.check_list(expected_categories, dialog.lstCategories)

        # check if hazard option is selected
        expected_category = -1
        category_index = dialog.lstCategories.currentRow()
        message = ('Expected %s, but I got %s' %
                   (expected_category, category_index))
        self.assertEqual(expected_category, category_index, message)

        # choosing hazard
        self.select_from_list_widget('hazard', dialog.lstCategories)

        dialog.pbnNext.click()  # Go to hazard category

        self.check_current_step(step_kw_hazard_category, dialog)
        self.select_from_list_widget('Single Event',
                                     dialog.lstHazardCategories)
        dialog.pbnNext.click()  # Go to subcategory

        # check if in step subcategory
        self.check_current_step(step_kw_subcategory, dialog)

        # check the values of subcategories options
        expected_subcategories = [
            u'earthquake',
            u'flood',
            u'volcanic ash',
            u'tsunami',
            u'volcano',
            u'generic']
        self.check_list(expected_subcategories, dialog.lstSubcategories)

        # check if no option is selected
        expected_subcategory_index = -1
        subcategory_index = dialog.lstSubcategories.currentRow()
        message = ('Expected %s, but I got %s' %
                   (expected_subcategory_index, subcategory_index))
        self.assertEqual(
            expected_subcategory_index, subcategory_index, message)

        # choosing flood
        self.select_from_list_widget('flood', dialog.lstSubcategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(step_kw_layermode, dialog)

        # check the values of subcategories options
        expected_layermodes = ['continuous', 'classified']
        self.check_list(expected_layermodes, dialog.lstLayerModes)

        # check if the default option is selected
        expected_layermode_index = 0
        layermode_index = dialog.lstLayerModes.currentRow()
        message = ('Expected %s, but I got %s' %
                   (expected_layermode_index, layermode_index))
        self.assertEqual(
            expected_layermode_index, layermode_index, message)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(step_kw_unit, dialog)

        # check the values of units options
        # Notes, I changed this because this is how the metadata works. We
        # should find another method to filter the unit based on hazard type
        # or change the data test keywords. Ismail.
        expected_units = [
            u'feet', u'metres', u'generic', u'kg/m2', u'kilometres',
            u'millimetres', u'MMI']
        self.check_list(expected_units, dialog.lstUnits)

        # choosing metres
        self.select_from_list_widget('metres', dialog.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnBack.click()  # back to step unit
        dialog.pbnBack.click()  # back to step data_type
        dialog.pbnBack.click()  # back to step subcategory

        # check if in step subcategory
        self.check_current_step(step_kw_subcategory, dialog)

        # check if flood is selected
        expected_subcategory = 'flood'
        subcategory = dialog.lstSubcategories.currentItem().text()
        message = ('Expected %s, but I got %s' %
                   (expected_subcategory, subcategory))
        self.assertEqual(
            expected_subcategory, subcategory, message)

        # choosing earthquake
        self.select_from_list_widget('earthquake', dialog.lstSubcategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(step_kw_layermode, dialog)

        # check the values of subcategories options
        expected_layermodes = ['classified', 'continuous']
        self.check_list(expected_layermodes, dialog.lstLayerModes)

        # check if the default option is selected
        expected_layermode_index = 1
        layermode_index = dialog.lstLayerModes.currentRow()
        message = ('Expected %s, but I got %s' %
                   (expected_layermode_index, layermode_index))
        self.assertEqual(
            expected_layermode_index, layermode_index, message)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(step_kw_unit, dialog)

        # check the values of units options
        # Notes, I changed this because this is how the metadata works. We
        # should find another method to filter the unit based on hazard type
        # or change the data test keywords. Ismail.
        expected_units = [
            u'feet', u'generic', u'kg/m2', u'kilometres', u'metres',
            u'millimetres', u'MMI']
        self.check_list(expected_units, dialog.lstUnits)

        # choosing MMI
        self.select_from_list_widget('MMI', dialog.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(step_kw_source, dialog)

    def test_integrated_line(self):
        """Test for line layer and all possibilities."""
        layer = clone_shp_layer(
            name='roads',
            include_keywords=True,
            source_directory=test_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['exposure']
        self.check_list(expected_categories, dialog.lstCategories)

        self.check_current_text('exposure', dialog.lstCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(step_kw_subcategory, dialog)

        expected_subcategories = ['road']
        self.check_list(expected_subcategories, dialog.lstSubcategories)

        self.check_current_text('road', dialog.lstSubcategories)

        dialog.pbnNext.click()  # go to laywr mode

        # check if in step layer mode
        self.check_current_step(step_kw_layermode, dialog)

        expected_modes = ['none']
        self.check_list(expected_modes, dialog.lstLayerModes)

        self.check_current_text(expected_modes[0], dialog.lstLayerModes)

        # dialog.pbnNext.click()  # go to fields
        # expected_fields = ['NAME', 'OSM_TYPE', 'TYPE']
        # self.check_list(expected_fields, dialog.lstFields)
        # self.select_from_list_widget('TYPE', dialog.lstFields)

        dialog.pbnNext.click()  # go to source

        # check if in step extrakeywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(2)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnNext.click()  # go to title step

        dialog.pbnCancel.click()  # cancel

    def test_integrated_polygon(self):
        """Test for polygon layer and all possibilities."""
        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            source_directory=test_data_path('hazard'),
            include_keywords=False)
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['hazard', 'exposure', 'aggregation']
        self.check_list(expected_categories, dialog.lstCategories)

        # choosing exposure
        self.select_from_list_widget('exposure', dialog.lstCategories)

        dialog.pbnNext.click()  # Go to subcategory

        # check number of subcategories
        expected_subcategories = ['structure']
        self.check_list(expected_subcategories, dialog.lstSubcategories)

        # check if automatically select the only option
        self.check_current_text(
            expected_subcategories[0], dialog.lstSubcategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(step_kw_layermode, dialog)

        # check the values of modes options
        expected_modes = ['none']
        self.check_list(expected_modes, dialog.lstLayerModes)

        # choosing classified
        self.select_from_list_widget('none', dialog.lstLayerModes)

        dialog.pbnNext.click()  # Go to extra keywords

        # check if in step extrakeywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(5)

        dialog.pbnNext.click()  # Go to source

        # check if in source step
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnBack.click()  # back to extra_keywords step
        dialog.pbnBack.click()  # back to layer_mode step
        dialog.pbnBack.click()  # back to subcategory step
        dialog.pbnBack.click()  # back to category step

        # choosing hazard
        self.select_from_list_widget('hazard', dialog.lstCategories)
        dialog.pbnNext.click()  # Go to hazard category

        # choosing single event scenario
        self.select_from_list_widget('Single Event',
                                     dialog.lstHazardCategories)
        dialog.pbnNext.click()  # Go to subcategory

        # check the values of subcategories options
        # expected_subcategories = ['flood', 'tsunami']
        # Notes: IS, the generic IF makes the expected sub categories like this
        expected_subcategories = [
            'flood',
            'tsunami',
            'earthquake',
            'volcano',
            'volcanic ash',
            'generic']
        self.check_list(expected_subcategories, dialog.lstSubcategories)

        # select flood
        self.select_from_list_widget('flood', dialog.lstSubcategories)
        dialog.pbnNext.click()  # go to mode

        # select classified
        self.check_current_step(step_kw_layermode, dialog)
        self.select_from_list_widget('classified', dialog.lstLayerModes)
        dialog.pbnNext.click()  # go to field

        self.check_current_step(step_kw_field, dialog)
        expected_fields = [
            'OBJECTID', 'KAB_NAME', 'KEC_NAME', 'KEL_NAME', 'RW',
            'FLOODPRONE']
        self.check_list(expected_fields, dialog.lstFields)

        # select FLOODPRONE
        self.select_from_list_widget('FLOODPRONE', dialog.lstFields)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(step_kw_classification, dialog)

        expected_values = ['flood vector hazard classes',
                           'generic vector hazard classes',
                           'volcano vector hazard classes']
        self.check_list(expected_values, dialog.lstClassifications)
        self.select_from_list_widget('flood vector hazard classes',
                                     dialog.lstClassifications)
        dialog.pbnNext.click()  # go to classify

        self.check_current_step(step_kw_classify, dialog)

        # check unclassified
        expected_unique_values = []  # no unclassified values
        self.check_list(expected_unique_values, dialog.lstUniqueValues)

        # check classified
        root = dialog.treeClasses.invisibleRootItem()
        expected_classes = ['wet', 'dry']
        child_count = root.childCount()
        message = 'Child count must be %s' % len(expected_classes)
        self.assertEqual(len(expected_classes), child_count, message)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            message = '%s should not be in classes name' % class_name
            self.assertIn(class_name, expected_classes, message)
            if class_name == 'wet':
                expected_num_child = 1
                num_child = item.childCount()
                message = 'The child of wet should be %s' % expected_num_child
                self.assertEqual(expected_num_child, num_child, message)
            if class_name == 'dry':
                expected_num_child = 1
                num_child = item.childCount()
                message = 'The child of dry should be %s' % expected_num_child
                self.assertEqual(expected_num_child, num_child, message)

        dialog.pbnNext.click()  # Go to Extra keywords

        # check if in step extrakeywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(5)
        dialog.cboExtraKeyword2.setCurrentIndex(1)
        dialog.cboExtraKeyword3.setCurrentIndex(5)
        expected_field = 'FLOODPRONE (String)'
        expected_value = 'YES'
        actual_field = dialog.cboExtraKeyword1.currentText()
        actual_value = dialog.cboExtraKeyword2.currentText()
        message = ('Invalid field in the first extra keyword! There should be '
                   '%s while there were: %s') % (expected_field, actual_field)
        self.assertEqual(actual_field, expected_field, message)
        message = ('Invalid value in the 2nd extra keyword! There should be '
                   '%s while there were: %s') % (expected_value, actual_value)
        self.assertEqual(actual_value, expected_value, message)

        dialog.pbnNext.click()  # go to source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnBack.click()  # back to extra keywords
        dialog.pbnBack.click()  # back to classify
        dialog.pbnBack.click()  # back to classification
        dialog.pbnBack.click()  # back to field
        dialog.pbnBack.click()  # back to layer mode
        dialog.pbnBack.click()  # back to subcategory
        dialog.pbnBack.click()  # back to hazard category

        # Currently we don't have any continuous units for polygons to test.
        # self.select_from_list_widget('metres', dialog.lstUnits)
        # dialog.pbnNext.click()  # go to field

        # check in field step
        # self.check_current_step(step_kw_field, dialog)

        # check if all options are disabled
        # for i in range(dialog.lstFields.count()):
        #    item_flag = dialog.lstFields.item(i).flags()
        #    message = 'Item should be disabled'
        #    self.assertTrue(item_flag & ~QtCore.Qt.ItemIsEnabled, message)

        # dialog.pbnBack.click()  # back to unit
        # dialog.pbnBack.click()  # back to subcategory

        # self.select_from_list_widget('tsunami', dialog.lstSubcategories)
        # dialog.pbnNext.click()  # go to unit
        # self.check_current_step(step_kw_unit, dialog)

        # back again since tsunami similar to flood
        # dialog.pbnBack.click()  # back to subcategory

        self.check_current_step(step_kw_hazard_category, dialog)
        self.select_from_list_widget('Multiple Event',
                                     dialog.lstHazardCategories)
        dialog.pbnNext.click()  # go to subcategory

        self.check_current_step(step_kw_subcategory, dialog)
        self.select_from_list_widget('volcano', dialog.lstSubcategories)
        dialog.pbnNext.click()  # go to mode

        self.check_current_step(step_kw_layermode, dialog)
        self.select_from_list_widget('classified', dialog.lstLayerModes)
        dialog.pbnNext.click()  # go to fields

        self.check_current_step(step_kw_field, dialog)
        self.select_from_list_widget('FLOODPRONE', dialog.lstFields)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(step_kw_classification, dialog)
        self.select_from_list_widget(
            'volcano vector hazard classes', dialog.lstClassifications)
        dialog.pbnNext.click()  # go to classify

        self.check_current_step(step_kw_classify, dialog)

        # check unclassified
        expected_unique_values = ['NO', 'YES']  # Unclassified value
        self.check_list(expected_unique_values, dialog.lstUniqueValues)

        # check classified
        root = dialog.treeClasses.invisibleRootItem()
        expected_classes = ['low', 'medium', 'high']
        child_count = root.childCount()
        message = 'Child count must be %s' % len(expected_classes)
        self.assertEqual(len(expected_classes), child_count, message)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            message = '%s should not be in classes name' % class_name
            self.assertIn(class_name, expected_classes, message)
            expected_num_child = 0
            num_child = item.childCount()
            message = 'The child of wet should be %s' % expected_num_child
            self.assertEqual(expected_num_child, num_child, message)

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(step_kw_extrakeywords, dialog)
        dialog.cboExtraKeyword1.setCurrentIndex(5)
        dialog.cboExtraKeyword2.setCurrentIndex(1)

        dialog.pbnNext.click()  # go to source
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnCancel.click()

    def test_sum_ratio_behavior(self):
        """Test for wizard's behavior related sum of age ratio."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)
        dialog.suppress_warning_dialog = True

        self.check_current_text('aggregation', dialog.lstCategories)

        dialog.pbnNext.click()  # Go to unit step

        self.check_current_text('KAB_NAME', dialog.lstFields)

        dialog.pbnNext.click()  # Go to aggregation step

        dialog.dsbYouthRatioDefault.setValue(1.0)

        dialog.pbnNext.click()  # Try to go to  source step

        # check if still in aggregation step
        self.check_current_step(step_kw_aggregation, dialog)

        dialog.cboYouthRatioAttribute.setCurrentIndex(1)  # set don't use

        dialog.pbnNext.click()  # Try to go to  source step

        # check if in source step
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnBack.click()  # Go to aggregation step

        # check if in aggregation step
        self.check_current_step(step_kw_aggregation, dialog)
        dialog.cboYouthRatioAttribute.setCurrentIndex(0)  # set global default

        dialog.dsbYouthRatioDefault.setValue(0.0)

        dialog.pbnNext.click()  # Try to go to source step

        # check if in source step
        self.check_current_step(step_kw_source, dialog)

        dialog.pbnCancel.click()

    def test_input_function_centric_wizard(self):
        """Test the IFCW mode."""

        expected_test_layer_count = 2

        expected_hazards_count = 5
        expected_exposures_count = 3
        expected_flood_structure_functions_count = 4
        expected_raster_polygon_functions_count = 2
        expected_functions_count = 2
        chosen_if = 'FloodRasterBuildingFunction'

        expected_hazard_layers_count = 1
        expected_exposure_layers_count = 1
        expected_aggregation_layers_count = 0

        # expected_summary_key = 'minimum needs'
        # expected_summary_value_fragment = 'rice'

        expected_report_size = 4361  # as saved on Ubuntu
        # TS : changed tolerance from 120 to 160 because above change
        # causes fail on fedora
        # AG: updated the tolerance from 160 to 190
        tolerance = 190  # windows EOL etc

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.set_function_centric_mode()

        # Load test layers
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=test_data_path('exposure'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Check the environment first
        message = 'Test layers are not readable. Check environment variables.'
        self.assertIsNotNone(layer.dataProvider(), message)

        count = len(dialog.iface.mapCanvas().layers())
        message = 'Test layers are not loaded.'
        self.assertEqual(count, expected_test_layer_count, message)

        # step_fc_function_1: test function matrix dimensions
        col_count = dialog.tblFunctions1.columnCount()
        message = ('Invalid hazard count in the IF matrix! There should be '
                   '%d while there were: %d') % (expected_hazards_count,
                                                 col_count)
        self.assertEqual(col_count, expected_hazards_count, message)
        row_count = dialog.tblFunctions1.rowCount()
        message = ('Invalid exposures count in the IF matrix! There should be '
                   '%d while there were: %d') % (expected_exposures_count,
                                                 row_count)
        self.assertEqual(row_count, expected_exposures_count, message)

        # step_fc_function_1: test number of functions for flood x structure
        dialog.tblFunctions1.setCurrentCell(2, 1)
        count = len(dialog.selected_functions_1())
        message = ('Invalid functions count in the IF matrix 1! For flood '
                   'and structure there should be %d while there were: '
                   '%d') % (expected_flood_structure_functions_count, count)
        self.assertEqual(count, expected_flood_structure_functions_count,
                         message)

        # step_fc_function_1: press ok
        dialog.pbnNext.click()

        # step_fc_function_2: test number of functions for raster flood
        # and polygon structure
        dialog.tblFunctions2.setCurrentCell(3, 0)

        count = len(dialog.selected_functions_2())
        message = ('Invalid functions count in the IF matrix 2! For '
                   ' raster and polygon there should be %d while there'
                   ' were: %d') % (expected_raster_polygon_functions_count,
                                   count)
        self.assertEqual(count, expected_raster_polygon_functions_count,
                         message)

        # step_fc_function_2: press ok
        dialog.pbnNext.click()

        # step_fc_function_3: test number of available functions
        count = dialog.lstFunctions.count()
        message = ('Invalid functions count on the list! There should be %d '
                   'while there were: %d') % (expected_functions_count, count)
        self.assertEqual(count, expected_functions_count, message)

        # step_fc_function_3: test if chosen_if is on the list
        role = QtCore.Qt.UserRole
        flood_ifs = [dialog.lstFunctions.item(row).data(role)['id']
                     for row in range(count)]
        message = 'Expected flood impact function not found: %s' % chosen_if
        self.assertTrue(chosen_if in flood_ifs, message)

        # step_fc_function: select FloodRasterBuildingImpactFunction and
        # press ok
        chosen_if_row = flood_ifs.index(chosen_if)
        dialog.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas: test the lstCanvasHazLayers state
        # Note this step is tested prior to step_fc_hazlayer_origin
        # as the list is prepared prior to autoselecting the radiobuttons
        count = dialog.lstCanvasHazLayers.count()
        message = ('Invalid hazard layers count! There should be %d while '
                   'there were: %d') % (expected_hazard_layers_count, count)
        self.assertEqual(count, expected_hazard_layers_count, message)

        # step_fc_hazlayer_origin: test if the radiobuttons are autmatically
        # enabled and selected
        message = ('The rbHazLayerFromCanvas radio button has been not '
                   'automatically enabled')
        self.assertTrue(dialog.rbHazLayerFromCanvas.isEnabled(), message)
        message = ('The rbHazLayerFromCanvas radio button has been not '
                   'automatically selected')
        self.assertTrue(dialog.rbHazLayerFromCanvas.isChecked(), message)

        # step_fc_hazlayer_origin: press ok
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas: press ok
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: test the lstCanvasExpLayers state
        # Note this step is tested prior to step_fc_explayer_origin
        # as the list is prepared prior to autoselecting the radiobuttons
        count = dialog.lstCanvasExpLayers.count()
        message = ('Invalid exposure layers count! There should be %d while '
                   'there were: %d') % (expected_exposure_layers_count, count)
        self.assertEqual(count, expected_exposure_layers_count, message)

        # step_fc_explayer_origin: test if the radiobuttons are automatically
        # enabled and selected
        message = ('The rbExpLayerFromCanvas radio button has been not '
                   'automatically enabled')
        self.assertTrue(dialog.rbExpLayerFromCanvas.isEnabled(), message)
        message = ('The rbExpLayerFromCanvas radio button has been not '
                   'automatically selected')
        self.assertTrue(dialog.rbExpLayerFromCanvas.isChecked(), message)

        # step_fc_explayer_origin: press ok
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: press ok
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: test the lstCanvasAggLayers state
        # Note this step is tested prior to step_fc_agglayer_origin
        # as the list is prepared prior to auto selecting the radio buttons
        count = dialog.lstCanvasAggLayers.count()
        message = ('Invalid aggregation layers count! There should be %d '
                   'while there were: '
                   '%d') % (expected_aggregation_layers_count, count)
        self.assertEqual(count, expected_aggregation_layers_count, message)

        # step_fc_agglayer_origin: test if the radio buttons are automatically
        # enabled and selected
        message = ('The rbAggLayerFromCanvas radio button has been not '
                   'automatically disabled')
        self.assertTrue(not dialog.rbAggLayerFromCanvas.isEnabled(), message)
        message = ('The rbAggLayerFromBrowser radio button has been not '
                   'automatically selected')
        self.assertTrue(dialog.rbAggLayerFromBrowser.isChecked(), message)

        # step_fc_agglayer_origin: switch to no aggregation and press ok
        dialog.rbAggLayerNoAggregation.click()
        dialog.pbnNext.click()

        # step_fc_extent: switch to layer's extent and press ok
        dialog.rbExtentLayer.click()
        dialog.pbnNext.click()

        # step_fc_params: press ok (already covered by the relevant test)
        dialog.pbnNext.click()

        # step_fc_summary: test minimum needs text
        # summaries = dialog.lblSummary.text().split('<br/>')

        # #TODO: temporarily disable minimum needs test as they seem
        # #te be removed from params
        # minneeds = [s for s in summaries
        #            if expected_summary_key.upper() in s.upper()]
        # message = 'No minimum needs found in the summary text'
        # self.assertTrue(minneeds, message)
        # message = 'No rice found in the minimum needs in the summary text'
        # self.assertTrue(expected_summary_value_fragment.upper()
        #                in minneeds[0].upper(), message)

        # step_fc_summary: run analysis
        dialog.pbnNext.click()

        # step_fc_analysis: test the html output
        report_path = dialog.wvResults.report_path
        size = os.stat(report_path).st_size
        message = (
            'Expected generated report to be %d +- %dBytes, got %d. '
            'Please update expected_size if the generated output '
            'is acceptable on your system.'
            % (expected_report_size, tolerance, size))
        self.assertTrue(
            (expected_report_size - tolerance < size < expected_report_size +
             tolerance),
            message)

        # close the wizard
        dialog.pbnNext.click()

if __name__ == '__main__':
    suite = unittest.makeSuite(WizardDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
