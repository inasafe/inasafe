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

import os
import shutil
import sys
import unittest

from PyQt4 import QtCore
from PyQt4.QtCore import Qt

# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe.common.utilities import temp_dir
from safe.test.utilities import (
    clone_raster_layer,
    clone_shp_layer,
    get_qgis_app,
    standard_data_path)

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.tools.wizard
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from definitionsv4.definitions_v3 import inasafe_keyword_version
from safe.impact_functions.loader import register_impact_functions
from safe.gui.tools.wizard.wizard_dialog import WizardDialog
from safe.gui.tools.wizard.wizard_utils import get_question_text
from safe.utilities.keyword_io import KeywordIO, definition


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
        self.assertItemsEqual(expected_list, real_list)

    def check_current_step(self, expected_step):
        """Helper function to check the current step is expected_step

        :param expected_step: The expected current step.
        :type expected_step: WizardStep instance
        """
        current_step = expected_step.parent.get_current_step()
        self.assertEqual(expected_step, current_step)

    def check_current_text(self, expected_text, list_widget):
        """Check the current text in list widget is expected_text

        :param expected_text: The expected current step.
        :type expected_text: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        # noinspection PyUnresolvedReferences
        current_text = list_widget.currentItem().text()
        self.assertEqual(expected_text, current_text)

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

    def test_get_missing_question_text(self):
        """Test how the wizard copes with importing missing texts."""
        constant = '_dummy_missing_constant'
        expected_text = '<b>MISSING CONSTANT: %s</b>' % constant
        text = get_question_text(constant)
        self.assertEqual(text, expected_text)

    def test_invalid_keyword_layer(self):
        layer = clone_raster_layer(
            name='invalid_keyword_xml',
            include_keywords=True,
            source_directory=standard_data_path('other'),
            extension='.tif')

        # check the environment first
        self.assertIsNotNone(layer.dataProvider())
        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        # It shouldn't raise any exception although the xml is invalid
        dialog.set_keywords_creation_mode(layer)

    def test_keywords_creation_wizard(self):
        """Test how the widgets work."""
        expected_category_count = 3
        expected_categories = ['hazard', 'exposure', 'aggregation']
        chosen_category = 'hazard'

        expected_hazard_category_count = 2
        expected_hazard_categories = ['Single event', 'Multiple event']
        chosen_hazard_category = 'Single event'

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

        expected_classification_count = 2
        expected_classification = 'Flood classes'

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
            'source': 'some source',
            'title': 'some title',
            'keyword_version': inasafe_keyword_version
        }

        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))

        # check the environment first
        self.assertIsNotNone(layer.dataProvider())

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 of 9 - select category
        count = dialog.step_kw_purpose.lstCategories.count()
        self.assertEqual(count, expected_category_count)

        # Get all the categories given by wizards and save the 'hazard' index
        categories = []
        hazard_index = -1
        for i in range(expected_category_count):
            category_name = dialog.step_kw_purpose.lstCategories.item(i).data(
                Qt.UserRole)
            categories.append(category_name)
            if category_name == chosen_category:
                hazard_index = i
        # Check if categories is the same with expected_categories
        self.assertItemsEqual(categories, expected_categories)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.step_kw_purpose.lstCategories.selectedItems()))
        # Select hazard one
        dialog.step_kw_purpose.lstCategories.setCurrentRow(hazard_index)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 2 of 9 - select subcategory
        # Check the number of sub categories
        count = dialog.step_kw_subcategory.lstSubcategories.count()
        self.assertEqual(count, expected_subcategory_count)

        # Get all the subcategories given and save the 'flood' index
        subcategories = []
        tsunami_index = -1
        for i in range(expected_subcategory_count):
            subcategory_name = dialog.step_kw_subcategory.lstSubcategories.\
                item(i).data(Qt.UserRole)
            subcategories.append(subcategory_name)
            if subcategory_name == chosen_subcategory:
                tsunami_index = i
        # Check if subcategories is the same with expected_subcategories
        self.assertItemsEqual(subcategories, expected_subcategories)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.step_kw_subcategory.lstSubcategories.selectedItems()),
            'Invalid Next button state in step 3! '
            'Enabled while there\'s nothing selected yet')
        # Set to tsunami subcategories
        dialog.step_kw_subcategory.lstSubcategories.setCurrentRow(
            tsunami_index)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click next button
        dialog.pbnNext.click()

        # step 3 of 9 - select hazard category
        count = dialog.step_kw_hazard_category.lstHazardCategories.count()
        self.assertEqual(count, expected_hazard_category_count)

        # Get all the categories given by wizards and save the 'hazard' index
        hazard_categories = []
        scenario_index = -1
        for i in range(expected_hazard_category_count):
            key = dialog.step_kw_hazard_category.lstHazardCategories.\
                item(i).data(Qt.UserRole)
            hazard_category_name = definition(key)['name']
            hazard_categories.append(hazard_category_name)
            if hazard_category_name == chosen_hazard_category:
                scenario_index = i
        # Check if categories is the same with expected_categories
        self.assertItemsEqual(hazard_categories, expected_hazard_categories)
        # The Next button should be on disabled state first unless the keywords
        # are already assigned
        self.assertTrue(
            not dialog.pbnNext.isEnabled() or
            len(dialog.step_kw_hazard_category.lstHazardCategories.
                selectedItems())
        )
        # Select hazard one
        dialog.step_kw_hazard_category.lstHazardCategories.setCurrentRow(
            scenario_index)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 4 of 9 - select classified mode
        # Check if the number of modes is 2
        self.check_current_step(dialog.step_kw_layermode)
        count = dialog.step_kw_layermode.lstLayerModes.count()
        self.assertEqual(count, expected_mode_count)
        # Get all the modes given and save the classified index
        modes = []
        for i in range(expected_mode_count):
            mode_name = dialog.step_kw_layermode.lstLayerModes.item(i).data(
                Qt.UserRole)
            modes.append(mode_name)
        # Check if units is the same with expected_units
        self.assertItemsEqual(expected_modes, modes)

        dialog.pbnNext.click()

        # step 5 of 9 - select classification scheme
        # Check if the number of classifications is 2
        count = dialog.step_kw_classification.lstClassifications.count()
        self.assertEqual(count, expected_classification_count)
        self.check_current_text(
            expected_classification,
            dialog.step_kw_classification.lstClassifications
        )
        # Click next
        dialog.pbnNext.click()

        # step 6 of 9 - select data field for flood
        self.check_current_step(dialog.step_kw_field)
        count = dialog.step_kw_field.lstFields.count()
        self.assertEqual(count, expected_field_count)
        # Get all the fields given and save the 'FLOODPRONE' index
        fields = []
        floodprone_index = -1
        for i in range(expected_field_count):
            field_name = dialog.step_kw_field.lstFields.item(i).text()
            fields.append(field_name)
            if field_name == expected_chosen_field:
                floodprone_index = i
        # Check if fields is the same with expected_fields
        self.assertItemsEqual(expected_fields, fields)
        dialog.step_kw_field.lstFields.setCurrentRow(floodprone_index)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click next
        dialog.pbnNext.click()

        # Click next
        dialog.pbnNext.click()

        # step 8 of 9 - enter source
        self.assertTrue(dialog.pbnNext.isEnabled())
        dialog.step_kw_source.leSource.setText('some source')
        dialog.pbnNext.click()

        # step 9 of 9 - enter title
        dialog.step_kw_title.leTitle.setText('some title')
        self.assertTrue(dialog.pbnNext.isEnabled())
        dialog.pbnNext.click()
        dialog.pbnNext.click()

        # test the resulting keywords
        keyword_io = KeywordIO()
        # noinspection PyTypeChecker
        keywords = keyword_io.read_keywords(layer)

        self.assertEqual(keywords, expected_keywords)

    def test_existing_keywords(self):
        """Test if keywords already exist."""
        expected_field_count = 6

        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))

        # check the environment first
        self.assertIsNotNone(layer.dataProvider())

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 - select layer purpose
        self.check_current_text('Hazard', dialog.step_kw_purpose.lstCategories)

        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 2 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 3 - select hazard category
        self.check_current_text(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 4 - select layer mode
        # noinspection PyTypeChecker
        self.check_current_text(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 5 - select flood classification
        self.check_current_text(
            'Flood classes', dialog.step_kw_classification.lstClassifications)
        self.assertTrue(dialog.pbnNext.isEnabled())
        # Click Next
        dialog.pbnNext.click()

        # step 6 - select field
        # noinspection PyTypeChecker
        self.check_current_text('FLOODPRONE', dialog.step_kw_field.lstFields)
        self.assertTrue(dialog.pbnNext.isEnabled())

        count = dialog.step_kw_field.lstFields.count()
        self.assertEqual(count, expected_field_count)

        # Click Next
        dialog.pbnNext.click()

        # Click Next
        dialog.pbnNext.click()

        # step 7 - enter source
        self.assertTrue(dialog.pbnNext.isEnabled())
        self.assertEqual(dialog.step_kw_source.leSource.text(), '')
        self.assertEqual(dialog.step_kw_source.leSource_url.text(), '')
        self.assertFalse(dialog.step_kw_source.ckbSource_date.isChecked())
        self.assertEqual(dialog.step_kw_source.leSource_scale.text(), '')
        dialog.pbnNext.click()

        # step 8 - enter title
        self.assertEqual(
            dialog.layer.name(), dialog.step_kw_title.leTitle.text())
        self.assertTrue(dialog.pbnNext.isEnabled())
        dialog.pbnNext.click()

    def test_existing_complex_keywords(self):
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # select hazard
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # select volcano
        self.select_from_list_widget(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # select multiple_event
        self.select_from_list_widget(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()

        # select volcano classified mode
        self.select_from_list_widget(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()

        # select volcano vector hazard classes classification
        self.select_from_list_widget(
            'Volcano classes',
            dialog.step_kw_classification.lstClassifications
        )
        dialog.pbnNext.click()

        # select KRB field
        self.select_from_list_widget('KRB', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()

        # select mapping
        classification = dialog.step_kw_classification.\
            selected_classification()
        default_classes = classification['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'low': ['Kawasan Rawan Bencana I'],
            'medium': ['Kawasan Rawan Bencana II'],
            'high': ['Kawasan Rawan Bencana III']
        }
        dialog.step_kw_classify.populate_classified_values(
            unassigned_values, assigned_values, default_classes)
        dialog.pbnNext.click()

        # select additional keywords
        self.check_current_step(dialog.step_kw_extrakeywords)
        dialog.pbnBack.click()
        dialog.pbnNext.click()
        first_field = 'KRB'
        index = dialog.step_kw_extrakeywords.cboExtraKeyword1.findData(
            first_field, Qt.UserRole)
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(index)
        self.assertEqual(index, 0)

        third_field = 'volcano'
        index = dialog.step_kw_extrakeywords.cboExtraKeyword1.findData(
            third_field, Qt.UserRole)
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(index)
        self.assertEqual(index, 2)

        dialog.pbnNext.click()

        self.check_current_step(dialog.step_kw_source)
        source = 'Source'
        source_scale = 'Source Scale'
        source_url = 'Source Url'
        source_date = QtCore.QDateTime.fromString(
            '06-12-2015 12:30',
            'dd-MM-yyyy HH:mm')
        source_license = 'Source License'

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.ckbSource_date.setChecked(True)
        dialog.step_kw_source.dtSource_date.setDateTime(source_date)
        dialog.step_kw_source.leSource_license.setText(source_license)
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # finish

        # noinspection PyTypeChecker
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        # step 1 - select layer purpose
        self.check_current_text('Hazard', dialog.step_kw_purpose.lstCategories)

        # Click Next
        dialog.pbnNext.click()

        # step 2 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)

        # Click Next
        dialog.pbnNext.click()

        # step 3 - select hazard category
        self.check_current_text(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories
        )

        # Click Next
        dialog.pbnNext.click()

        # step 4 - select layer mode
        self.check_current_text(
            'Classified', dialog.step_kw_layermode.lstLayerModes)

        # Click Next
        dialog.pbnNext.click()

        # step 5 - select classification
        self.check_current_text(
            'Volcano classes',
            dialog.step_kw_classification.lstClassifications
        )

        # Click Next
        dialog.pbnNext.click()

        # step 6 - select field
        self.check_current_text('KRB', dialog.step_kw_field.lstFields)

        # Click Next
        dialog.pbnNext.click()

        # step 7 - select mapping
        for index in range(dialog.step_kw_classify.lstUniqueValues.count()):
            self.assertIn(
                dialog.step_kw_classify.lstUniqueValues.item(index).text(),
                unassigned_values)
        real_assigned_values = dialog.step_kw_classify.selected_mapping()
        self.assertDictEqual(real_assigned_values, assigned_values)

        # Click Next
        dialog.pbnNext.click()

        # step 8 - additional keywords
        self.assertTrue(dialog.pbnNext.isEnabled())

        # Click Next
        dialog.pbnNext.click()

        # step 9 - enter source
        self.check_current_step(dialog.step_kw_source)
        self.assertTrue(dialog.pbnNext.isEnabled())

        self.assertEqual(dialog.step_kw_source.leSource.text(), source)
        self.assertEqual(dialog.step_kw_source.leSource_url.text(), source_url)
        self.assertEqual(
            dialog.step_kw_source.leSource_scale.text(), source_scale)
        self.assertEqual(
            dialog.step_kw_source.dtSource_date.dateTime(), source_date)
        self.assertEqual(
            dialog.step_kw_source.leSource_license.text(), source_license)
        dialog.pbnNext.click()

        dialog.pbnCancel.click()

    # noinspection PyTypeChecker
    def test_existing_aggregation_keywords(self):
        """Test for case existing keywords in aggregation layer."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=standard_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        category = dialog.step_kw_purpose.lstCategories.currentItem().text()
        expected_category = 'Aggregation'
        self.assertEqual(expected_category, category)

        dialog.pbnNext.click()

        self.check_current_text('KAB_NAME', dialog.step_kw_field.lstFields)

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
        aggregation_attributes = dialog.step_kw_aggregation.\
            get_aggregation_attributes()
        self.assertDictEqual(
            expected_aggregation_attributes, aggregation_attributes)

        dialog.step_kw_aggregation.cboFemaleRatioAttribute.setCurrentIndex(2)
        expected_female_attribute_key = 'PEREMPUAN'
        female_attribute_key = dialog.step_kw_aggregation.\
            cboFemaleRatioAttribute.currentText()
        self.assertEqual(expected_female_attribute_key, female_attribute_key)
        self.assertFalse(
            dialog.step_kw_aggregation.dsbFemaleRatioDefault.isEnabled())

    # noinspection PyTypeChecker
    def test_unit_building_generic(self):
        """Test for case existing building generic unit for structure."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # go to subcategory

        self.check_current_step(dialog.step_kw_subcategory)
        dialog.pbnNext.click()  # go to layer mode

        self.check_current_step(dialog.step_kw_layermode)
        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)
        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

        dialog.pbnNext.click()  # finishing

    def test_default_attributes_value(self):
        """Checking that default attributes is set to the CIA's one."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=standard_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose aggregation go to field step
        dialog.pbnNext.click()  # choose KAB_NAME go to aggregation step

        ratio_attribute = dialog.step_kw_aggregation.cboElderlyRatioAttribute.\
            currentText()
        self.assertEqual('Global default', ratio_attribute)

        ratio_attribute = dialog.step_kw_aggregation.cboAdultRatioAttribute.\
            currentText()
        self.assertEqual('Global default', ratio_attribute)

        ratio_attribute = dialog.step_kw_aggregation.cboYouthRatioAttribute.\
            currentText()
        self.assertEqual('Global default', ratio_attribute)

        default_value = dialog.step_kw_aggregation.dsbYouthRatioDefault.value()
        expected_default_value = 0.26
        self.assertEqual(expected_default_value, default_value)

        default_value = dialog.step_kw_aggregation.dsbAdultRatioDefault.value()
        expected_default_value = 0.66
        self.assertEqual(expected_default_value, default_value)

        default_value = dialog.step_kw_aggregation.dsbElderlyRatioDefault.\
            value()
        expected_default_value = 0.08
        self.assertEqual(expected_default_value, default_value)

    def test_unknown_unit(self):
        """Checking that it works for unknown unit."""
        layer = clone_shp_layer(
            name='volcano_krb',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose volcano
        dialog.pbnNext.click()  # choose Multiple event
        dialog.step_kw_unit.lstUnits.setCurrentRow(1)
        self.check_current_text(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # choose classified

        # check if in step classification
        self.check_current_step(dialog.step_kw_classification)
        dialog.pbnNext.click()  # accept classification

        dialog.step_kw_field.lstFields.setCurrentRow(0)  # Choose KRB
        self.check_current_text('KRB', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()  # choose KRB

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)
        dialog.pbnNext.click()  # accept mapping

        # check if in step extra keywords
        self.check_current_step(dialog.step_kw_extrakeywords)
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(2)
        dialog.pbnNext.click()  # accept extra keywords

        # check if in step source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()  # accept source

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

    def test_point_layer(self):
        """Wizard for point layer."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose hazard
        dialog.pbnNext.click()  # choose Multiple event
        dialog.pbnNext.click()  # choose volcano
        dialog.step_kw_layermode.lstLayerModes.setCurrentRow(0)  # choose none
        dialog.pbnNext.click()  # choose none
        # choose NAME
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(4)
        dialog.pbnNext.click()  # choose NAME

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # choose volcano  go to title step

        # check if in step title
        self.check_current_step(dialog.step_kw_title)
        dialog.accept()

    def test_auto_select_one_item(self):
        """Test auto select if there is only one item in a list."""
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        dialog.pbnNext.click()  # choose exposure
        self.assertEquals(
            dialog.step_kw_subcategory.lstSubcategories.currentRow(), 0)
        num_item = dialog.step_kw_subcategory.lstSubcategories.count()
        self.assertTrue(num_item == 3)

    def test_integrated_point(self):
        """Test for point layer and all possibilities."""
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)

        self.check_current_text('Hazard', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        expected_subcategories = ['Volcano']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories)

        self.check_current_text(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # go to hazard category

        expected_hazard_categories = ['Multiple event', 'Single event']
        self.check_list(
            expected_hazard_categories,
            dialog.step_kw_hazard_category.lstHazardCategories)

        self.check_current_text(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # go to layer mode

        self.check_current_step(dialog.step_kw_layermode)

        # select the Classified mode
        dialog.step_kw_layermode.lstLayerModes.setCurrentRow(0)

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(dialog.step_kw_extrakeywords)
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(4)
        expected_field = 'NAME (String)'
        actual_field = dialog.step_kw_extrakeywords.cboExtraKeyword1.\
            currentText()
        self.assertEqual(actual_field, expected_field)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # go to title

        # check if in step title
        self.check_current_step(dialog.step_kw_title)

        dialog.pbnCancel.click()

    def test_integrated_raster(self):
        """Test for raster layer and all possibilities."""
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        # check if hazard option is selected
        expected_category = -1
        category_index = dialog.step_kw_purpose.lstCategories.currentRow()
        self.assertEqual(expected_category, category_index)

        # choosing hazard
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # Go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        # check the values of subcategories options
        expected_subcategories = [
            u'Earthquake',
            u'Flood',
            u'Volcanic ash',
            u'Tsunami',
            u'Volcano',
            u'Generic']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # check if no option is selected
        expected_subcategory_index = -1
        subcategory_index = dialog.step_kw_subcategory.lstSubcategories.\
            currentRow()
        self.assertEqual(expected_subcategory_index, subcategory_index)

        # choosing flood
        self.select_from_list_widget(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to hazard category

        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of subcategories options
        expected_layer_modes = ['Continuous', 'Classified']
        self.check_list(
            expected_layer_modes, dialog.step_kw_layermode.lstLayerModes)

        # check if the default option is selected
        expected_layer_mode = 'Continuous'
        layer_mode = dialog.step_kw_layermode.lstLayerModes.\
            currentItem().text()
        self.assertEqual(expected_layer_mode, layer_mode)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(dialog.step_kw_unit)

        # check the values of units options
        expected_units = [u'Feet', u'Metres', u'Generic']
        self.check_list(expected_units, dialog.step_kw_unit.lstUnits)

        # choosing metres
        self.select_from_list_widget('Metres', dialog.step_kw_unit.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to step unit
        dialog.pbnBack.click()  # back to step data_type
        dialog.pbnBack.click()  # back to step hazard_category
        dialog.pbnBack.click()  # back to step subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        # check if flood is selected
        expected_subcategory = 'Flood'
        subcategory = dialog.step_kw_subcategory.lstSubcategories.\
            currentItem().text()
        self.assertEqual(expected_subcategory, subcategory)

        # choosing earthquake
        self.select_from_list_widget(
            'Earthquake', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to hazard category

        # choosing Single event
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of subcategories options
        expected_layer_modes = ['Continuous', 'Classified']
        self.check_list(
            expected_layer_modes, dialog.step_kw_layermode.lstLayerModes)

        # check if the default option is selected
        expected_layer_mode = 'Continuous'
        layer_mode = dialog.step_kw_layermode.lstLayerModes.currentItem().\
            text()
        self.assertEqual(expected_layer_mode, layer_mode)

        dialog.pbnNext.click()  # Go to unit

        # check if in step unit
        self.check_current_step(dialog.step_kw_unit)

        # check the values of units options
        # Notes, I changed this because this is how the metadata works. We
        # should find another method to filter the unit based on hazard type
        # or change the data test keywords. Ismail.
        expected_units = [u'Generic', u'MMI']
        self.check_list(expected_units, dialog.step_kw_unit.lstUnits)

        # choosing MMI
        self.select_from_list_widget('MMI', dialog.step_kw_unit.lstUnits)

        dialog.pbnNext.click()  # Go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

    def test_integrated_line(self):
        """Test for line layer and all possibilities."""
        layer = clone_shp_layer(
            name='roads',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Exposure']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        self.check_current_text(
            'Exposure', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # go to subcategory

        # check if in step subcategory
        self.check_current_step(dialog.step_kw_subcategory)

        expected_subcategories = ['Road']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        self.check_current_text(
            'Road', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # go to laywr mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        expected_modes = ['Classified']
        self.check_list(expected_modes, dialog.step_kw_layermode.lstLayerModes)

        self.check_current_text(
            expected_modes[0], dialog.step_kw_layermode.lstLayerModes)

        dialog.pbnNext.click()  # go to fields
        expected_fields = ['NAME', 'OSM_TYPE', 'TYPE']
        self.check_list(expected_fields, dialog.step_kw_field.lstFields)
        self.select_from_list_widget('TYPE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)

        dialog.pbnNext.click()  # go to source

        # check if in step source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnNext.click()  # go to title step

        dialog.pbnCancel.click()  # cancel

    def test_integrated_polygon(self):
        """Test for polygon layer and all possibilities."""
        layer = clone_shp_layer(
            name='flood_multipart_polygons',
            source_directory=standard_data_path('hazard'),
            include_keywords=False)
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)

        expected_categories = ['Hazard', 'Exposure', 'Aggregation']
        self.check_list(
            expected_categories, dialog.step_kw_purpose.lstCategories)

        # choosing exposure
        self.select_from_list_widget(
            'Exposure', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # Go to subcategory

        # check number of subcategories
        expected_subcategories = ['Structure', 'Population', 'Land cover']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # check if automatically select the only option

        self.select_from_list_widget(
            'Structure', dialog.step_kw_subcategory.lstSubcategories)

        self.check_current_text(
            'Structure', dialog.step_kw_subcategory.lstSubcategories)

        dialog.pbnNext.click()  # Go to layer mode

        # check if in step layer mode
        self.check_current_step(dialog.step_kw_layermode)

        # check the values of modes options
        expected_modes = ['Classified']
        self.check_list(expected_modes, dialog.step_kw_layermode.lstLayerModes)

        # choosing classified
        self.select_from_list_widget(
            'Classified', dialog.step_kw_layermode.lstLayerModes)

        dialog.pbnNext.click()  # Go to field

        # check if in step extrakeywords
        self.check_current_step(dialog.step_kw_field)
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        # check if in step classify
        self.check_current_step(dialog.step_kw_classify)

        dialog.pbnNext.click()  # Go to source

        # check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to classify step
        dialog.pbnBack.click()  # back to field step
        dialog.pbnBack.click()  # back to layer_mode step
        dialog.pbnBack.click()  # back to subcategory step
        dialog.pbnBack.click()  # back to category step

        # choosing hazard
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()  # Go to subcategory

        # check the values of subcategories options
        # expected_subcategories = ['flood', 'tsunami']
        # Notes: IS, the generic IF makes the expected sub categories like this
        expected_subcategories = [
            'Flood',
            'Tsunami',
            'Earthquake',
            'Volcano',
            'Volcanic ash',
            'Generic']
        self.check_list(
            expected_subcategories,
            dialog.step_kw_subcategory.lstSubcategories
        )

        # select flood
        self.select_from_list_widget(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()  # go to hazard category

        # choosing Single event scenario
        self.select_from_list_widget(
            'Single event', dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()  # Go to mode

        # select classified
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(dialog.step_kw_classification)

        expected_values = ['Flood classes', 'Generic classes']
        self.check_list(
            expected_values, dialog.step_kw_classification.lstClassifications)
        self.select_from_list_widget(
            'Flood classes', dialog.step_kw_classification.lstClassifications)

        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        expected_fields = [
            'OBJECTID',
            'KAB_NAME',
            'KEC_NAME',
            'KEL_NAME',
            'RW',
            'FLOODPRONE']
        self.check_list(expected_fields, dialog.step_kw_field.lstFields)

        # select FLOODPRONE
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # go to classify

        self.check_current_step(dialog.step_kw_classify)

        # check unclassified
        expected_unique_values = []  # no unclassified values
        self.check_list(
            expected_unique_values, dialog.step_kw_classify.lstUniqueValues)

        # check classified
        root = dialog.step_kw_classify.treeClasses.invisibleRootItem()
        expected_classes = ['wet', 'dry']
        child_count = root.childCount()
        self.assertEqual(len(expected_classes), child_count)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            self.assertIn(class_name, expected_classes)
            if class_name == 'wet':
                expected_num_child = 1
                num_child = item.childCount()
                self.assertEqual(expected_num_child, num_child)
            if class_name == 'dry':
                expected_num_child = 1
                num_child = item.childCount()
                self.assertEqual(expected_num_child, num_child)

        dialog.pbnNext.click()  # Go to source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # back to classify
        dialog.pbnBack.click()  # back to field
        dialog.pbnBack.click()  # back to classification
        dialog.pbnBack.click()  # back to layer mode
        dialog.pbnBack.click()  # back to hazard category
        dialog.pbnBack.click()  # back to subcategory

        # Currently we don't have any continuous units for polygons to test.
        # self.select_from_list_widget('metres', dialog.step_kw_unit.lstUnits)
        # dialog.pbnNext.click()  # go to field

        # check in field step
        # self.check_current_step(dialog.step_kw_field)

        # check if all options are disabled
        # for i in range(dialog.step_kw_field.lstFields.count()):
        #    item_flag = dialog.step_kw_field.lstFields.item(i).flags()
        #    self.assertTrue(item_flag & ~QtCore.Qt.ItemIsEnabled)

        # dialog.pbnBack.click()  # back to unit
        # dialog.pbnBack.click()  # back to subcategory

        # self.select_from_list_widget(
        # 'tsunami', dialog.step_kw_subcategory.lstSubcategories)
        # dialog.pbnNext.click()  # go to unit
        # self.check_current_step(dialog.step_kw_unit)

        # back again since tsunami similar to flood
        # dialog.pbnBack.click()  # back to subcategory

        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Volcano', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()  # go to hazard category

        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Multiple event',
            dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()  # go to mode

        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Classified', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()  # go to classifications

        self.check_current_step(dialog.step_kw_classification)
        self.select_from_list_widget(
            'Volcano classes',
            dialog.step_kw_classification.lstClassifications)
        dialog.pbnNext.click()  # go to field

        self.check_current_step(dialog.step_kw_field)
        self.select_from_list_widget(
            'FLOODPRONE', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()  # go to classify

        self.check_current_step(dialog.step_kw_classify)

        # check unclassified
        expected_unique_values = ['NO', 'YES']  # Unclassified value
        self.check_list(
            expected_unique_values, dialog.step_kw_classify.lstUniqueValues)

        # check classified
        root = dialog.step_kw_classify.treeClasses.invisibleRootItem()
        expected_classes = [
            'Low Hazard Zone',
            'Medium Hazard Zone',
            'High Hazard Zone'
        ]
        child_count = root.childCount()
        self.assertEqual(len(expected_classes), child_count)
        for i in range(child_count):
            item = root.child(i)
            class_name = item.text(0)
            self.assertIn(class_name, expected_classes)
            expected_num_child = 0
            num_child = item.childCount()
            self.assertEqual(expected_num_child, num_child)

        dialog.pbnNext.click()  # go to extra keywords
        self.check_current_step(dialog.step_kw_extrakeywords)
        dialog.step_kw_extrakeywords.cboExtraKeyword1.setCurrentIndex(5)
        dialog.step_kw_extrakeywords.cboExtraKeyword2.setCurrentIndex(1)

        dialog.pbnNext.click()  # go to source
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnCancel.click()

    def test_sum_ratio_behavior(self):
        """Test for wizard's behavior related sum of age ratio."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=standard_data_path('boundaries'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)
        dialog.suppress_warning_dialog = True

        self.check_current_text(
            'Aggregation', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()  # Go to field step

        self.check_current_text('KAB_NAME', dialog.step_kw_field.lstFields)

        dialog.pbnNext.click()  # Go to aggregation step

        dialog.step_kw_aggregation.dsbYouthRatioDefault.setValue(1.0)

        dialog.pbnNext.click()  # Try to go to source step

        # check if still in aggregation step
        self.check_current_step(dialog.step_kw_aggregation)

        # set don't use
        dialog.step_kw_aggregation.cboYouthRatioAttribute.setCurrentIndex(1)

        dialog.pbnNext.click()  # Try to go to  source step

        # check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnBack.click()  # Go to aggregation step

        # check if in aggregation step
        self.check_current_step(dialog.step_kw_aggregation)
        # set global default
        dialog.step_kw_aggregation.cboYouthRatioAttribute.setCurrentIndex(0)

        dialog.step_kw_aggregation.dsbYouthRatioDefault.setValue(0.0)

        dialog.pbnNext.click()  # Try to go to source step

        # check if in source step
        self.check_current_step(dialog.step_kw_source)

        dialog.pbnCancel.click()

    def test_allow_resample(self):
        """Test the allow resample step"""

        # Initialize dialog
        layer = clone_raster_layer(
            name='people_allow_resampling_false',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        dialog = WizardDialog()
        dialog.set_keywords_creation_mode(layer)
        dialog.suppress_warning_dialog = True

        # step_kw_purpose
        self.check_current_step(dialog.step_kw_purpose)
        self.select_from_list_widget(
            'Exposure', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # step_kw_subcategory
        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Population', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # step_kw_layermode
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Continuous', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()

        # step_kw_unit
        self.check_current_step(dialog.step_kw_unit)
        self.select_from_list_widget('Count', dialog.step_kw_unit.lstUnits)
        dialog.pbnNext.click()

        # step_kw_resample
        self.check_current_step(dialog.step_kw_resample)
        dialog.step_kw_resample.chkAllowResample.setChecked(True)
        dialog.pbnNext.click()

        # step_kw_source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()

        # step_kw_title
        self.check_current_step(dialog.step_kw_title)
        dialog.pbnNext.click()

        # step_kw_summary
        self.check_current_step(dialog.step_kw_summary)
        dialog.pbnNext.click()

if __name__ == '__main__':
    suite = unittest.makeSuite(WizardDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
