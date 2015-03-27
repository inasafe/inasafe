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
__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '25/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from qgis.core import (
    QgsVectorLayer,
    QgsMapLayerRegistry)

from safe.gui.tools.people_in_buildings_dialog import PeopleInBuildingsDialog

from safe.test.utilities import (
    test_data_path,
    load_layers,
    get_qgis_app)


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI."""

    def setUp(self):
        """Create fresh dialog for each test."""
        IFACE.setActiveLayer(None)
        buildings_layer = test_data_path(
            'exposure', 'people_in_buildings_buildings.shp')
        census_layer = test_data_path(
            'exposure', 'people_in_buildings_census.shp')
        load_layers([census_layer, buildings_layer])
        self.dialog = PeopleInBuildingsDialog(IFACE, PARENT)

    def tearDown(self):
        """Destroy the dialog after each test."""
        # Clear all the loaded layers in Map Registry
        # noinspection PyArgumentList,PyUnresolvedReferences
        for layer in QgsMapLayerRegistry.instance().mapLayers():
            # noinspection PyArgumentList,PyUnresolvedReferences
            QgsMapLayerRegistry.instance().removeMapLayer(layer)

    @staticmethod
    def _get_combobox_content(combo_box):
        """Get the options of a combo box.

        :param combo_box: The combo box to be considered.
        :type combo_box: QComboBox

        :returns: A list of all items.
        :rtype: list
        """
        items = [combo_box.itemText(i) for i in range(combo_box.count())]
        return items

    def _load_option_into_combo(self, combo, option):
        """Load a new option into a combo box.

        :param combo: The combo box to be updated.
        :type combo: QComboBox

        :param option: The option to be added.
        :type option: basestring
        """
        items = self._get_combobox_content(combo)
        message = 'Trying to load an invalid field %s into a combo box' % (
            option)
        self.assertIn(option, items, message)
        combo.setCurrentIndex(items.index(option))

    def _load_building_layer_details(self):
        """Load the buildings layer details"""
        buildings_combo = self.dialog.buildingLayerComboBox
        buildings_name = 'people_in_buildings_buildings'
        self._load_option_into_combo(buildings_combo, buildings_name)

    def _load_buildings_attributes(self):
        """Load the building layer attributes"""
        usage_column = self.dialog.usageColumnComboBox
        usage_name = 'TYPE'
        self._load_option_into_combo(usage_column, usage_name)
        levels_column = self.dialog.levelsColumnComboBox
        levels_name = 'LEVELS'
        self._load_option_into_combo(levels_column, levels_name)

    def _load_census_layer_details(self):
        """Load the buildings layer details"""
        census_combo = self.dialog.censusLayerComboBox
        census_name = 'people_in_buildings_census'
        self._load_option_into_combo(census_combo, census_name)

    def _load_census_attributes(self):
        """Load the building layer attributes"""
        population_count_column = self.dialog.populationCountComboBox
        column_name = 'population'
        self._load_option_into_combo(population_count_column, column_name)

    def test_0001_remove_previous_run_columns(self):
        """Assure the layer doesn't have the attributes before running.
        """
        buildings_layer = self.dialog._select_layer_by_name(
            'people_in_buildings_buildings')
        field_names = self.dialog._get_field_names(buildings_layer)
        for attribute_name in ['People_Rnd', 'People_Dec']:
            if attribute_name in field_names:
                provider = buildings_layer.dataProvider()
                field_index = provider.fieldNameIndex(attribute_name)
                provider.deleteAttributes([field_index])
        for attribute_name in ['People_Rnd', 'People_Dec']:
            provider = buildings_layer.dataProvider()
            field_index = provider.fieldNameIndex(attribute_name)
            message = 'Unable to remove field %s.' % (attribute_name)
            self.assertEqual(field_index, -1, message)

    def test_0001_load_layer(self):
        """Test that the correct layers are available to the UI.
        """
        self.dialog.load_layers_into_combo_box()
        buildings_options = self._get_combobox_content(
            self.dialog.buildingLayerComboBox)
        population_options =  self._get_combobox_content(
            self.dialog.censusLayerComboBox)
        buildings_name = 'people_in_buildings_buildings'
        population_name = 'people_in_buildings_census'
        message = (
            'The buildings layer %s has not been loaded into the people '
            'in buildings dialog' % buildings_name)
        self.assertIn(buildings_name, buildings_options, message)
        message = (
            'The population layer %s has not been loaded into the people '
            'in buildings dialog' % population_name)
        self.assertIn(population_name, population_options, message)
        message = 'The layers in the layer dropdowns should be equal'
        self.assertItemsEqual(buildings_options, population_options, message)

    def test_0002_building_layer_and_attributes(self):
        """Ensure the building attributes are being assigned to the
        """
        self._load_building_layer_details()
        buildings_name = 'people_in_buildings_buildings'
        buildings_combo = self.dialog.buildingLayerComboBox
        buildings_text = buildings_combo.currentText()
        message = 'The buildings layer was not selected.'
        self.assertEqual(buildings_name, buildings_text, message)
        self._load_buildings_attributes()
        usage_column = self.dialog.usageColumnComboBox
        usage_name = 'TYPE'
        usage_text = usage_column.currentText()
        message = 'The usage column was not selected.'
        self.assertEqual(usage_name, usage_text, message)
        levels_column = self.dialog.levelsColumnComboBox
        levels_name = 'LEVELS'
        levels_text = levels_column.currentText()
        message = 'The usage column was not selected.'
        self.assertEqual(levels_name, levels_text, message)

    def test_0003_population_layer_and_attributes(self):
        """Ensure the people attributes are being assigned to buildings layer.
        """
        self._load_census_layer_details()
        census_name = 'people_in_buildings_census'
        census_combo = self.dialog.censusLayerComboBox
        census_text = census_combo.currentText()
        message = 'The population layer was not selected.'
        self.assertEqual(census_name, census_text, message)
        self._load_census_attributes()
        usage_column = self.dialog.populationCountComboBox
        usage_name = 'population'
        usage_text = usage_column.currentText()
        message = 'The population column was not selected.'
        self.assertEqual(usage_name, usage_text, message)

    def test_0004_hit_apply(self):
        """Assert progress bar moves while calculating.
        """
        self._load_building_layer_details()
        self._load_buildings_attributes()
        self._load_census_layer_details()
        self._load_census_attributes()
        message = 'The progress bar should start at 0.'
        self.assertEqual(self.dialog.progressBar.value(), 0, message)
        self.dialog.estimate_people_in_buildings()
        message = 'The progress bar should end at 100.'
        self.assertEqual(self.dialog.progressBar.value(), 100, message)

    def test_0005_calculated_values_correct(self):
        """Confirm the newly added columns have the correct value.
        """
        buildings_layer = self.dialog._select_layer_by_name(
            'people_in_buildings_buildings')
        for building in buildings_layer.getFeatures():
            if building['BUILDING'] == 'Skyscraper':
                message = 'The people count is calculated incorrectly.'
                assert(building['People_Rnd'], 615, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
