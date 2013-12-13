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

__author__ = 'tim@linfiniti.com'
__date__ = '21/02/2011'
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
from nose import SkipTest
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from PyQt4 import QtGui

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsMapLayerRegistry)

from third_party.odict import OrderedDict
from safe.common.testing import get_qgis_app
from safe_qgis.utilities.utilities_for_testing import (
    test_data_path)
from safe_qgis.safe_interface import (
    read_file_keywords,
    unique_filename,
    HAZDATA, TESTDATA)
from safe_qgis.tools.keywords_dialog import KeywordsDialog
from safe_qgis.exceptions import KeywordNotFoundError
from safe_qgis.utilities.utilities import qgis_version
from safe_qgis.utilities.defaults import breakdown_defaults


# Get QGis app handle
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def make_padang_layer():
    """Helper function that returns a single predefined layer"""
    path = 'Shakemap_Padang_2009.asc'
    full_path = os.path.join(HAZDATA, path)
    title = read_file_keywords(full_path, 'title')
    # title = 'An earthquake in Padang like in 2009'
    layer = QgsRasterLayer(full_path, title)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    return layer


def clone_padang_layer():
    """Helper function that copies padang keyword for testing and return it."""
    path = 'Shakemap_Padang_2009'
    extensions = [
        '.asc', '.asc.aux.xml', '.keywords', '.lic', '.prj', '.qml', '.sld']
    temp_path = unique_filename()
    # copy to temp file
    for ext in extensions:
        source_path = os.path.join(HAZDATA, path + ext)
        dest_path = os.path.join(HAZDATA, temp_path + ext)
        shutil.copy2(source_path, dest_path)
    # return a single predefined layer
    path = temp_path + '.asc'
    full_path = os.path.join(HAZDATA, path)
    title = read_file_keywords(full_path, 'title')
    layer = QgsRasterLayer(full_path, title)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    return layer, temp_path


def make_polygon_layer():
    """Helper function that returns a single predefined layer"""
    path = 'kabupaten_jakarta_singlepart_3_good_attr.shp'
    full_path = os.path.join(TESTDATA, path)
    try:
        title = read_file_keywords(full_path, 'title')
    except KeywordNotFoundError:
        title = 'kabupaten_jakarta_singlepart_3_good_attr'
    layer = QgsVectorLayer(full_path, title, 'ogr')
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    return layer


def make_point_layer():
    """Helper function that returns a single predefined layer"""
    path = 'test_buildings.shp'
    full_path = os.path.join(TESTDATA, path)
    try:
        title = read_file_keywords(full_path, 'title')
    except KeywordNotFoundError:
        title = 'kabupaten_jakarta_singlepart_3_good_attr'
    layer = QgsVectorLayer(full_path, title, 'ogr')
    # noinspection PyArgumentList
    QgsMapLayerRegistry.instance().addMapLayer(layer)
    return layer


def remove_temp_file(file_name='temp_Shakemap_Padang_2009'):
    """Helper function that removes temp file that created during test
    :param file_name: File to remove.
    """
    #file_name = 'temp_Shakemap_Padang_2009'
    extensions = [
        '.asc', '.asc.aux.xml', '.keywords', '.lic', '.prj', '.qml', '.sld']
    for ext in extensions:
        os.remove(os.path.join(HAZDATA, file_name + ext))


def make_keywordless_layer():
    """Helper function that returns a single predefined keywordless layer"""
    path = 'keywordless_layer.tif'
    base_path = test_data_path('hazard')
    full_path = os.path.abspath(os.path.join(base_path, path))
    title = 'Keywordless Layer'
    layer = QgsRasterLayer(full_path, title)
    if qgis_version() >= 10800:  # 1.8 or newer
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])
    else:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    return layer


def clear_layers():
    """Clear all the loaded layers"""
    # noinspection PyArgumentList
    for layer in QgsMapLayerRegistry.instance().mapLayers():
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeMapLayer(layer)


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI"""

    def setUp(self):
        """Create fresh dialog for each test"""
        pass

    def tearDown(self):
        """Destroy the dialog after each test"""
        clear_layers()

    # This is how you skip a test when using unittest ...
    @unittest.skip(
        'Skipping as this test hangs Jenkins if docs are not found.')
    def test_show_help(self):
        """Test that help button works"""
        # ... and this is how you skip it using nosetests
        #prevent unreachable code errors in pylint
        #pylint: disable=W0101
        raise SkipTest("This test hangs Jenkins.")
        # noinspection PyUnreachableCode
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.buttonBox.button(QtGui.QDialogButtonBox.Help)
        button.click()
        message = 'Help dialog was not created when help button pressed'
        self.assertTrue(dialog.helpDialog is not None, message)
        #pylint: enable=W0101

    def test_on_advanced_mode_toggled(self):
        """Test advanced button toggle behaviour works"""
        make_padang_layer()
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.pbnAdvanced
        button.setChecked(False)
        button.click()
        state = dialog.grpAdvanced.isHidden()
        expected_state = False
        message = (
            'Advanced options did not become visible when'
            ' the advanced button was clicked\nGot'
            '%s\nExpected\n%s\n' % (state, expected_state))

        self.assertEqual(state, expected_state, message)

        # Now hide advanced again and test...
        button.click()
        state = dialog.grpAdvanced.isHidden()
        expected_state = True

        message = (
            'Advanced options did not become hidden when'
            ' the advanced button was clicked again\nGot'
            '%s\nExpected\n%s\n' % (state, expected_state))
        self.assertTrue(not dialog.grpAdvanced.isVisible(), message)

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
        """Test hazard radio button toggle behaviour works"""
        layer = make_polygon_layer()
        defaults = breakdown_defaults()
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        button = dialog.radPostprocessing
        button.setChecked(False)
        button.click()
        message = (
            'Toggling the postprocessing radio did not add a '
            'category to the keywords list.')
        self.assertEqual(dialog.get_value_for_key(
            'category'), 'postprocessing', message)

        message = (
            'Toggling the postprocessing radio did not add an '
            'aggregation attribute to the keywords list.')
        self.assertEqual(dialog.get_value_for_key(
            defaults['AGGR_ATTR_KEY']), 'KAB_NAME', message)

        message = (
            'Toggling the postprocessing radio did not add a '
            'female ratio attribute to the keywords list.')

        self.assertEqual(dialog.get_value_for_key(
            defaults['FEM_RATIO_ATTR_KEY']), dialog.tr('Use default'),
            message)

        message = (
            'Toggling the postprocessing radio did not add a '
            'female ratio default value to the keywords list.')
        self.assertEqual(float(dialog.get_value_for_key(
            defaults['FEM_RATIO_KEY'])), defaults['FEM_RATIO'], message)

    def test_on_dsb_female_ratio_default_value_changed(self):
        """Test hazard radio button toggle behaviour works"""
        layer = make_polygon_layer()
        defaults = breakdown_defaults()
        dialog = KeywordsDialog(PARENT, IFACE, layer=layer)
        button = dialog.radPostprocessing
        button.setChecked(False)
        button.click()
        female_ratio_box = dialog.cboFemaleRatioAttribute

        #set to Don't use
        index = female_ratio_box.findText(dialog.tr('Don\'t use'))
        message = (dialog.tr('Don\'t use') + ' not found')
        self.assertNotEqual(index, -1, message)
        female_ratio_box.setCurrentIndex(index)

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not add it to the keywords list.')
        self.assertEqual(dialog.get_value_for_key(
            defaults['FEM_RATIO_ATTR_KEY']), dialog.tr('Don\'t use'),
            message)

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not disable dsbFemaleRatioDefault.')
        is_enabled = dialog.dsbFemaleRatioDefault.isEnabled()
        assert not is_enabled, message

        message = (
            'Toggling the female ratio attribute combo to'
            ' "Don\'t use" did not remove the keyword.')
        assert (dialog.get_value_for_key(defaults['FEM_RATIO']) is None), \
            message

        #set to TEST_REAL
        index = female_ratio_box.findText('TEST_REAL')
        message = 'TEST_REAL not found'
        assert (index != -1), message
        female_ratio_box.setCurrentIndex(index)

        message = (
            'Toggling the female ratio attribute combo to "TEST_REAL"'
            ' did not add it to the keywords list.')
        assert dialog.get_value_for_key(
            defaults['FEM_RATIO_ATTR_KEY']) == 'TEST_REAL', message

        message = (
            'Toggling the female ratio attribute combo to "TEST_REAL"'
            ' did not disable dsbFemaleRatioDefault.')
        is_enabled = dialog.dsbFemaleRatioDefault.isEnabled()
        assert not is_enabled, message

        message = (
            'Toggling the female ratio attribute combo to "TEST_REAL"'
            ' did not remove the keyword.')
        assert (dialog.get_value_for_key(defaults['FEM_RATIO']) is
                None), message

    def Xtest_on_radExposure_toggled(self):
        """Test exposure radio button toggle behaviour works"""

        # Cannot get this test to work, but it works fine in the safe_qgis
        dialog = KeywordsDialog(PARENT, IFACE)
        button = dialog.radExposure
        button.setChecked(False)
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
            'Changing the subcategory did not add %s '
            'to the keywords list' %
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
        dialog = KeywordsDialog(PARENT, IFACE)
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
        # print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_on_pbn_remove_clicked(self):
        """Test pressing remove works on key list"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)

        result = dialog.lstKeywords.count()
        expected_result = 0
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

        dialog.add_list_entry('bar', 'foo')
        result = dialog.lstKeywords.count()
        expected_result = 1
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_add_list_entry(self):
        """Test add entry to list works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'foo')
        result = dialog.get_value_for_key('bar')
        expected_result = 'foo'
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_add_warnings_for_colons(self):
        """Test add entry to list works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'fo:o')
        result = dialog.get_value_for_key('bar')
        expected_result = 'fo.o'
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)
        #
        # Check the user gets a message if they put colons in the value
        #
        expected_result = 'Colons are not allowed, replaced with "."'
        result = str(dialog.lblMessage.text())
        message = (
            'lblMessage error \nGot: %s\nExpected: %s\n' %
            (result, expected_result))
        #print 'Dict', dialog.getKeywords()
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
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_set_category(self):
        """Test set category works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.set_category('hazard')
        expected_result = 'hazard'
        result = dialog.get_value_for_key('category')
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_reset(self):
        """Test form reset works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.leTitle.setText('Foo')
        dialog.reset(False)
        expected_result = ''
        result = dialog.leTitle.text()
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_remove_iItem_by_key(self):
        """Test remove item by its key works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.reset(False)
        dialog.add_list_entry('bar', 'foo')
        dialog.remove_item_by_key('bar')
        result = dialog.lstKeywords.count()
        expected_result = 0
        message = '\nGot: %s\nExpected: %s\n' % (result, expected_result)
        #print 'Dict', dialog.getKeywords()
        self.assertEqual(result, expected_result, message)

    def test_remove_item_by_value(self):
        """Test remove item by its value works"""
        make_padang_layer()
        dialog = KeywordsDialog(PARENT, IFACE)
        dialog.remove_item_by_value('hazard')

        keywords = dialog.get_keywords()
        expected_keywords = {
            'source': 'USGS',
            'title': 'An earthquake in Padang like in 2009',
            'subcategory': 'earthquake',
            'unit': 'MMI'}
        self.assertEqual(keywords, expected_keywords)

    def test_get_value_for_key(self):
        """Test get value for key works"""
        make_padang_layer()
        dialog = KeywordsDialog(PARENT, IFACE)
        expected_value = 'hazard'
        value = dialog.get_value_for_key('category')
        self.assertEqual(value, expected_value)

    def test_load_state_from_keywords(self):
        """Test load state from keywords works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        layer = make_padang_layer()
        dialog.layer = layer
        dialog.load_state_from_keywords()
        keywords = dialog.get_keywords()

        expected_keywords = {
            'title': 'An earthquake in Padang like in 2009',
            'category': 'hazard',
            'source': 'USGS',
            'subcategory': 'earthquake',
            'unit': 'MMI'}
        self.assertEqual(keywords, expected_keywords)

    def test_layer_without_keywords(self):
        """Test load state from keywords works"""
        dialog = KeywordsDialog(PARENT, IFACE)
        layer = make_keywordless_layer()
        dialog.layer = layer
        dialog.load_state_from_keywords()

    def test_add_keyword_when_press_ok_button(self):
        """Test add keyword when ok button is pressed."""
        #_, path = makePadangLayerClone()
        clone_padang_layer()
        dialog = KeywordsDialog(PARENT, IFACE)

        dialog.radUserDefined.setChecked(True)
        dialog.leKey.setText('foo')
        dialog.leValue.setText('bar')
        ok_button = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        ok_button.click()

        # delete temp file
        # removeTempFile(path)

        expected_result = 'bar'
        result = dialog.get_value_for_key('foo')
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
