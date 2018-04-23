# coding=utf-8
"""
Test for Save Scenario Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '25/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import unittest

from safe.test.utilities import get_qgis_app, get_dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.gui_utilities import layer_from_combo
from safe.gui.tools.save_scenario import SaveScenarioDialog
from safe.test.utilities import (
    setup_scenario,
    set_canvas_crs,
    set_jakarta_extent,
    load_standard_layers,
    GEOCRS,
    standard_data_path)
from safe.common.utilities import unique_filename, temp_dir


class SaveScenarioTest(unittest.TestCase):
    """Test save scenario tool."""

    @classmethod
    def setUpClass(cls):
        cls.DOCK = get_dock()

    def setUp(self):
        """Fixture run before all tests."""
        os.environ['LANG'] = 'en'
        self.DOCK.show_only_visible_layers_flag = True
        load_standard_layers(self.DOCK)
        self.DOCK.hazard_layer_combo.setCurrentIndex(0)
        self.DOCK.exposure_layer_combo.setCurrentIndex(0)
        self.DOCK.run_in_thread_flag = False
        self.DOCK.show_only_visible_layers_flag = False
        self.DOCK.set_layer_from_title_flag = False
        self.DOCK.zoom_to_impact_flag = False
        self.DOCK.hide_exposure_flag = False

        # Create scenario dialog
        self.save_scenario_dialog = SaveScenarioDialog(IFACE, self.DOCK)

    def tearDown(self):
        """Fixture run after each test."""
        # noinspection PyArgumentList
        QgsProject.instance().removeAllMapLayers()
        self.DOCK.hazard_layer_combo.clear()
        self.DOCK.exposure_layer_combo.clear()
        # self.DOCK.aggregation_layer_combo.clear()
        # #dont do this because the aggregation_layer_combo
        # need to be able to react to the status changes of the other combos
        self.save_scenario_dialog = None

    @unittest.expectedFailure
    def test_validate_input(self):
        """Test validate input."""
        # Valid Case
        result, message = setup_scenario(
            self.DOCK,
            hazard='Classified Flood',
            exposure='Population')
        self.assertTrue(result, message)
        is_valid, message = self.save_scenario_dialog.validate_input()
        self.assertTrue(is_valid)
        self.assertIsNone(message)

        # Change the hazard layer to None
        self.save_scenario_dialog.dock.hazard_layer_combo.setCurrentIndex(-1)
        is_valid, message = self.save_scenario_dialog.validate_input()
        self.assertFalse(is_valid)
        self.assertIsNotNone(message)

    @unittest.expectedFailure
    def test_save_scenario(self):
        """Test saving Current scenario."""
        result, message = setup_scenario(
            self.DOCK,
            hazard='Classified Flood',
            exposure='Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(dock=self.DOCK)

        # create unique file
        scenario_file = unique_filename(
            prefix='scenarioTest', suffix='.txt', dir=temp_dir('test'))

        self.save_scenario_dialog.save_scenario(
            scenario_file_path=scenario_file)
        with open(scenario_file) as f:
            data = f.readlines()
        title = data[0][:-1]
        exposure = data[1][:-1]
        hazard = data[2][:-1]
        extent = data[4][:-1]
        self.assertTrue(
            os.path.exists(scenario_file),
            'File %s does not exist' % scenario_file)
        self.assertTrue(
            title == '[Classified Flood]',
            'Title is not the same')
        self.assertTrue(
            exposure.startswith('exposure =') and exposure.endswith(
                'pop_binary_raster_20_20.asc'),
            'Exposure is not the same')
        self.assertTrue(
            hazard.startswith('hazard =') and hazard.endswith(
                'classified_flood_20_20.asc'),
            'Hazard is not the same')

        expected_extent = (
            'extent = 106.287500, -6.380000, 107.372500, -6.070000')
        self.assertEqual(expected_extent, expected_extent)

    @unittest.expectedFailure
    def test_relative_path(self):
        """Test we calculate the relative paths correctly when saving scenario.
        """
        result, message = setup_scenario(
            self.DOCK,
            hazard='Classified Flood',
            exposure='Population')
        self.assertTrue(result, message)
        fake_dir = standard_data_path()
        scenario_file = unique_filename(
            prefix='scenarioTest', suffix='.txt', dir=fake_dir)
        exposure_layer = layer_from_combo(
            self.DOCK.exposure_layer_combo).publicSource()
        hazard_layer = layer_from_combo(
            self.DOCK.hazard_layer_combo).publicSource()

        relative_exposure = self.save_scenario_dialog.relative_path(
            scenario_file, exposure_layer)
        relative_hazard = self.save_scenario_dialog.relative_path(
            scenario_file, hazard_layer)

        if 'win32' in sys.platform:
            # windows
            self.assertEqual(
                'exposure\\pop_binary_raster_20_20.asc',
                relative_exposure)
            self.assertEqual(
                'hazard\\classified_flood_20_20.asc',
                relative_hazard)

        else:
            self.assertEqual(
                'exposure/pop_binary_raster_20_20.asc',
                relative_exposure)
            self.assertEqual(
                'hazard/classified_flood_20_20.asc',
                relative_hazard)

if __name__ == '__main__':
    suite = unittest.makeSuite(SaveScenarioTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
