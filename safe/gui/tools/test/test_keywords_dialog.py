# coding=utf-8
"""
InaSAFE uDisaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os
import shutil
from collections import OrderedDict
# noinspection PyPackageRequirements
from nose import SkipTest

from qgis.core import (
    QgsRasterLayer,
    QgsMapLayerRegistry)
from PyQt4 import QtGui

from safe.test.utilities import (
    test_data_path,
    clone_shp_layer,
    clone_raster_layer,
    temp_dir,
    get_qgis_app)
from safe.gui.tools.keywords_dialog import KeywordsDialog
from safe.utilities.gis import qgis_version
from safe.defaults import get_defaults

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def make_keywordless_layer():
    """Helper function that returns a single predefined keywordless layer."""
    path = 'keywordless_layer.tif'
    base_path = test_data_path('hazard')
    full_path = os.path.abspath(os.path.join(base_path, path))
    title = 'Keywordless Layer'
    # noinspection PyCallingNonCallable
    layer = QgsRasterLayer(full_path, title)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList,PyUnresolvedReferences
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    else:
        # noinspection PyArgumentList,PyUnresolvedReferences
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    return layer


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI."""

    def setUp(self):
        """Create fresh dialog for each test."""
        IFACE.setActiveLayer(None)

    def tearDown(self):
        """Destroy the dialog after each test."""
        # Clear all the loaded layers in Map Registry
        # noinspection PyArgumentList,PyUnresolvedReferences
        for layer in QgsMapLayerRegistry.instance().mapLayers():
            # noinspection PyArgumentList,PyUnresolvedReferences
            QgsMapLayerRegistry.instance().removeMapLayer(layer)

    # This is how you skip a test when using unittest ...
    @unittest.skip(
        'Skipping as this test hangs Jenkins if docs are not found.')
    def test_show_help(self):
        """Test that help button works"""
        # ... and this is how you skip it using nosetests
        # prevent unreachable code errors in pylint
        # pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins.")
        # noinspection PyUnreachableCode
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        button.click()
        message = 'Help dialog was not created when help button pressed'
        self.assertTrue(dialog.helpDialog is not None, message)
        # pylint: enable=W0101

    def test_on_rad_hazard_toggled(self):
        """Test hazard radio button toggle behaviour works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.radHazard
        button.setChecked(False)
        button.click()
        message = (
            'Toggling the hazard radio did not add a category '
            'to the keywords list.')
        self.assertEqual(
            dialog.get_value_for_key('category'), 'hazard',
            message)

    def test_on_rad_postprocessing_toggled(self):
        """Test postprocessing radio button toggle behaviour works"""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        defaults = get_defaults()
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        # Click hazard/exposure button first so that it won't take default
        # from keywords file
        dialog.radExposure.click()

        # Now click the postprocessing button
        button = dialog.radPostprocessing
        button.click()
        message = (
            'Toggling the postprocessing radio did not add a '
            'category to the keywords list.')
        self.assertEqual(
            dialog.get_value_for_key('category'), 'postprocessing', message)

        message = (
            'Toggling the postprocessing radio did not add an '
            'aggregation attribute to the keywords list.')
        self.assertEqual(
            dialog.get_value_for_key(defaults['AGGR_ATTR_KEY']),
            'KAB_NAME',
            message)

        message = (
            'Toggling the postprocessing radio did not add a '
            'female ratio attribute to the keywords list.')
        self.assertEqual(
            dialog.get_value_for_key(defaults['FEMALE_RATIO_ATTR_KEY']),
            dialog.global_default_string,
            message)

        message = (
            'Toggling the postprocessing radio did not add a '
            'female ratio default value to the keywords list.')
        self.assertEqual(
            float(dialog.get_value_for_key(defaults['FEMALE_RATIO_KEY'])),
            defaults['FEMALE_RATIO'],
            message)

    def test_on_dsb_female_ratio_default_value_changed(self):
        """Test hazard radio button toggle behaviour works"""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        defaults = get_defaults()
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        button = dialog.radPostprocessing
        button.setChecked(False)
        button.click()
        female_ratio_box = dialog.cboFemaleRatioAttribute

        # set to Don't use
        index = female_ratio_box.findText(dialog.do_not_use_string)
        message = (dialog.do_not_use_string + ' not found')
        self.assertNotEqual(index, -1, message)
        female_ratio_box.setCurrentIndex(index)

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not add it to the keywords list.')
        self.assertEqual(dialog.get_value_for_key(
            defaults['FEMALE_RATIO_ATTR_KEY']), dialog.do_not_use_string,
            message)

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not disable dsbFemaleRatioDefault.')
        is_enabled = dialog.dsbFemaleRatioDefault.isEnabled()
        assert not is_enabled, message

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not remove the keyword.')
        assert (dialog.get_value_for_key(defaults['FEMALE_RATIO']) is None), \
            message

        # set to PEREMPUAN attribute
        attribute = 'PEREMPUAN'
        index = female_ratio_box.findText(attribute)
        message = 'The attribute %s is not found in the layer' % attribute
        self.assertNotEqual(index, -1, message)

        female_ratio_box.setCurrentIndex(index)
        message = (
            'Toggling the female ratio attribute combo to %s'
            ' did not add it to the keywords list.') % attribute
        self.assertEqual(
            dialog.get_value_for_key(defaults['FEMALE_RATIO_ATTR_KEY']),
            attribute,
            message)

        message = (
            'Toggling the female ratio attribute combo to %s'
            ' did not disable dsbFemaleRatioDefault.') % attribute
        is_enabled = dialog.dsbFemaleRatioDefault.isEnabled()
        self.assertFalse(is_enabled, message)

        message = (
            'Toggling the female ratio attribute combo to %s'
            ' did not remove the keyword.') % attribute
        self.assertIsNone(
            dialog.get_value_for_key(defaults['FEMALE_RATIO']), message)

    def test_on_radExposure_toggled(self):
        """Test exposure radio button toggle behaviour works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        # Set other radio button checked first so that radExposure is not
        # toggled
        dialog.radHazard.setChecked(True)
        # Then click the radExposure
        button = dialog.radExposure
        button.click()
        message = (
            'Toggling the exposure radio did not add a category '
            'to the keywords list.')
        assert dialog.get_value_for_key('category') == 'exposure', message

    def test_on_subcategory_currentindexchanged(self):
        """Test subcategory combo change event works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.radHazard
        button.setChecked(True)
        button = dialog.radExposure
        button.click()
        combo = dialog.cboSubcategory
        combo.setCurrentIndex(1)  # change from 'Not set' to 'structure'
        message = (
            'Changing the subcategory did not add %s to the keywords list' %
            combo.currentText())
        key = dialog.get_value_for_key('subcategory')

        self.assertTrue(key is not None, message)
        assert key in str(combo.currentText()), message

    def test_set_subcategory_list(self):
        """Test set subcategory list works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        subcategory_list = OrderedDict([
            ('population [density]', 'population [density]'),
            ('population [count]', 'population [count]'),
            ('building', 'building'),
            ('building [osm]', 'building [osm]'),
            ('building [sigab]', 'building [sigab]'),
            ('road', 'road')])
        selected_item = 'building'
        dialog.set_subcategory_list(subcategory_list, selected_item)
        result = str(dialog.cboSubcategory.currentText())
        message = ('\nGot: %s\nExpected: %s\n' % (result, selected_item))

        self.assertTrue(result == selected_item, message)

    def test_on_pbn_add_to_list1_clicked(self):
        """Test adding an item to the list using predefined form works"""
        dialog = KeywordsDialog(PARENT, IFACE, layer=None)
        dialog.reset(False)
        dialog.radPredefined.setChecked(True)
        dialog.cboKeyword.setCurrentIndex(2)
        expected_result = 'foo'
        dialog.lePredefinedValue.setText(expected_result)
        dialog.on_pbnAddToList1_clicked()
        result = dialog.get_value_for_key('datatype')
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_on_pbn_add_to_list2_clicked(self):
        """Test adding an item to the list using user defined form works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.radUserDefined.setChecked(True)
        dialog.leKey.setText('foo')
        dialog.leValue.setText('bar')
        expected_result = 'bar'
        dialog.lePredefinedValue.setText(expected_result)
        dialog.on_pbnAddToList2_clicked()
        result = dialog.get_value_for_key('foo')
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_on_pbn_remove_clicked(self):
        """Test pressing remove works on key list"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)

        result = dialog.lstKeywords.count()
        expected_result = 0
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

        dialog.add_list_entry('bar', 'foo')
        result = dialog.lstKeywords.count()
        expected_result = 1
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_add_list_entry(self):
        """Test add entry to list works."""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'foo')
        result = dialog.get_value_for_key('bar')
        expected_result = 'foo'
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def Xtest_add_warnings_for_colons(self):
        """Test add add warning fot colons."""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'fo:o')
        result = dialog.get_value_for_key('bar')
        expected_result = 'fo.o'
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)
        #
        # Check the user gets a message if they put colons in the value
        #
        expected_result = 'Colons are not allowed, replaced with "."'
        result = str(dialog.lblMessage.text())
        message = (
            'lblMessage error \nGot: %s\nExpected: %s\n' %
            (result, expected_result))
        self.assertEqual(result, expected_result, message)
        #
        # Check the user gets a message if they put colons in the key
        #
        dialog.add_list_entry('ba:r', 'foo')
        expected_result = 'Colons are not allowed, replaced with "."'
        result = str(dialog.lblMessage.text())
        message = (
            'lblMessage error \nGot: %s\nExpected: %s\n' %
            (result, expected_result))
        self.assertEqual(result, expected_result, message)

    def test_set_category(self):
        """Test set category works."""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.set_category('hazard')
        expected_result = 'hazard'
        result = dialog.get_value_for_key('category')
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_reset(self):
        """Test form reset works."""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.leTitle.setText('Foo')
        dialog.reset(False)
        expected_result = ''
        result = dialog.leTitle.text()
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_remove_iItem_by_key(self):
        """Test remove item by its key works."""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'foo')
        dialog.remove_item_by_key('bar')
        result = dialog.lstKeywords.count()
        expected_result = 0
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_remove_item_by_value(self):
        """Test remove_item_by_value works."""
        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        dialog.remove_item_by_value('hazard')

        keywords = dialog.get_keywords()
        expected_keywords = {
            'title': 'A tsunami in Padang (Mw 8.8)',
            'subcategory': 'tsunami',
            'unit': 'm'}
        message = 'The keywords should be %s, but it returns %s' % (
            expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

    def test_get_value_for_key(self):
        """Test get_value_for_key works."""
        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        key = 'category'
        expected_value = 'hazard'
        value = dialog.get_value_for_key(key)
        message = 'The value for key %s should be %s, but it returns %s' % (
            key, expected_value, value)
        self.assertEqual(value, expected_value, message)

    def test_load_state_from_keywords(self):
        """Test load_state_from_keywords works."""
        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        dialog.load_state_from_keywords()
        keywords = dialog.get_keywords()
        expected_keywords = {
            'title': 'A tsunami in Padang (Mw 8.8)',
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'm'}
        message = 'The keyword should be %s, but it returns %s' % (
            expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

    def test_layer_without_keywords(self):
        """Test load state from keywords works."""
        layer = make_keywordless_layer()
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        dialog.load_state_from_keywords()

    def test_add_user_defined_keyword(self):
        """Test add user defined keyword when ok button is pressed."""
        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        # Set the keywords dialog
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        dialog.radUserDefined.setChecked(True)
        dialog.leKey.setText('foo')
        dialog.leValue.setText('bar')
        ok_button = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        ok_button.click()

        expected_result = 'bar'
        result = dialog.get_value_for_key('foo')
        message = 'The key %s should have value %s, but it returns %s' % (
            'foo', expected_result, result)
        self.assertEqual(result, expected_result, message)

    def test_check_aggregation(self):
        """Test for keywords dialog's behavior for aggregation layer."""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)

        # Load existing keywords
        keywords = dialog.get_keywords()
        expected_keywords = {
            u'category': u'postprocessing',
            u'aggregation attribute': u'KAB_NAME',
            u'title': u'D\xedstr\xedct\'s of Jakarta',
            u'elderly ratio attribute': u'Global default',
            u'youth ratio default': u'0.26',
            u'elderly ratio default': u'0.08',
            u'adult ratio attribute': u'Global default',
            u'female ratio attribute': u'PEREMPUAN',
            u'youth ratio attribute': u'Global default',
            u'adult ratio default': u'0.66'}
        message = 'Expected %s but I got %s' % (expected_keywords, keywords)
        self.assertDictEqual(expected_keywords, keywords, message)

        # Check age ratios are valid
        good_sum_ratio, _ = dialog.age_ratios_are_valid(keywords)
        message = 'Expected %s but I got %s' % (True, good_sum_ratio)
        self.assertEqual(True, good_sum_ratio, message)

        # Change youth ratio attribute to Don't Use
        dialog.cboYouthRatioAttribute.setCurrentIndex(1)
        keywords = dialog.get_keywords()
        expected_keywords = {
            u'category': u'postprocessing',
            u'aggregation attribute': u'KAB_NAME',
            u'title': u'D\xedstr\xedct\'s of Jakarta',
            u'elderly ratio attribute': u'Global default',
            u'elderly ratio default': u'0.08',
            u'adult ratio attribute': u'Global default',
            u'female ratio attribute': u'PEREMPUAN',
            u'youth ratio attribute': u'Don\'t use',
            u'adult ratio default': u'0.66'}
        message = 'Expected %s but I got %s' % (expected_keywords, keywords)
        self.assertDictEqual(expected_keywords, keywords, message)

        good_sum_ratio, _ = dialog.age_ratios_are_valid(keywords)
        message = 'Expected %s but I got %s' % (True, good_sum_ratio)
        self.assertEqual(True, good_sum_ratio, message)

        # Change youth ratio attribute to Global Default
        # Change youth ratio default to 0.99
        dialog.cboYouthRatioAttribute.setCurrentIndex(0)
        dialog.dsbYouthRatioDefault.setValue(0.99)
        keywords = dialog.get_keywords()
        expected_keywords = {
            u'category': u'postprocessing',
            u'aggregation attribute': u'KAB_NAME',
            u'title': u'D\xedstr\xedct\'s of Jakarta',
            u'elderly ratio attribute': u'Global default',
            u'elderly ratio default': u'0.08',
            u'adult ratio attribute': u'Global default',
            u'female ratio attribute': u'PEREMPUAN',
            u'youth ratio attribute': u'Global default',
            u'youth ratio default': u'0.99',
            u'adult ratio default': u'0.66'}
        message = 'Expected %s but I got %s' % (expected_keywords, keywords)
        self.assertDictEqual(expected_keywords, keywords, message)

        good_sum_ratio, _ = dialog.age_ratios_are_valid(keywords)
        message = 'Expected %s but I got %s' % (False, good_sum_ratio)
        self.assertEqual(False, good_sum_ratio, message)

        # We need to delete reference to layer on Windows before removing
        # the files
        del layer
        del dialog.layer
        # Using clone_shp_layer the files are saved in testing dir under
        # InaSAFE temp dir
        shutil.rmtree(temp_dir(sub_dir='testing'))

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
