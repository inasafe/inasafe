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

from qgis.core import QgsMapLayerRegistry

from safe.impact_functions import register_impact_functions
from safe.utilities.gis import qgis_version
from safe.gui.tools.save_scenario import SaveScenarioDialog
from safe.test.utilities import (
    setup_scenario,
    set_canvas_crs,
    set_jakarta_extent,
    load_standard_layers,
    GEOCRS,
    get_qgis_app,
    test_data_path)
from safe.common.utilities import unique_filename, temp_dir
from safe.impact_functions.impact_function_manager import ImpactFunctionManager

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.widgets.dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.widgets.dock import Dock


DOCK = Dock(IFACE)


class SaveScenarioTest(unittest.TestCase):
    """Test save scenario tool."""

    def setUp(self):
        """Fixture run before all tests."""
        os.environ['LANG'] = 'en'
        DOCK.show_only_visible_layers_flag = True
        load_standard_layers(DOCK)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.run_in_thread_flag = False
        DOCK.show_only_visible_layers_flag = False
        DOCK.set_layer_from_title_flag = False
        DOCK.zoom_to_impact_flag = False
        DOCK.hide_exposure_flag = False
        DOCK.show_intermediate_layers = False

        # Create scenario dialog
        self.save_scenario_dialog = SaveScenarioDialog(IFACE, DOCK)
        # register impact functions
        register_impact_functions()
        self.impact_function_manager = ImpactFunctionManager()

    def tearDown(self):
        """Fixture run after each test"""
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()
        # DOCK.cboAggregation.clear() #dont do this because the cboAggregation
        # need to be able to react to the status changes of the other combos
        self.save_scenario_dialog = None

    def test_validate_input(self):
        """Test validate input."""
        # Valid Case
        result, message = setup_scenario(
            DOCK,
            hazard='Classified Flood',
            exposure='Population',
            function='Be affected in each hazard class',
            function_id='ClassifiedRasterHazardPopulationFunction')
        self.assertTrue(result, message)
        is_valid, message = self.save_scenario_dialog.validate_input()
        self.assertTrue(is_valid)
        self.assertIsNone(message)

        # Change the hazard layer to None
        self.save_scenario_dialog.dock.cboHazard.setCurrentIndex(-1)
        is_valid, message = self.save_scenario_dialog.validate_input()
        self.assertFalse(is_valid)
        self.assertIsNotNone(message)

    def test_save_scenario(self):
        """Test saving Current scenario."""
        result, message = setup_scenario(
            DOCK,
            hazard='Classified Flood',
            exposure='Population',
            function='Be affected in each hazard class',
            function_id='ClassifiedRasterHazardPopulationFunction')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(dock=DOCK)

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
        function = data[3][:-1]
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
        self.assertTrue(
            function == (
                'function = ClassifiedRasterHazardPopulationFunction'),
            'Impact function is not same')

        # TODO: figure out why this changed between releases
        if qgis_version() < 20400:
            # For QGIS 2.0
            expected_extent = (
                'extent = 106.313333, -6.380000, 107.346667, -6.070000')
            self.assertEqual(expected_extent, extent)
        else:
            # for QGIS 2.4
            expected_extent = (
                'extent = 106.287500, -6.380000, 107.372500, -6.070000')
            self.assertEqual(expected_extent, expected_extent)

    def test_relative_path(self):
        """Test we calculate the relative paths correctly when saving scenario.
        """
        result, message = setup_scenario(
            DOCK,
            hazard='Classified Flood',
            exposure='Population',
            function='Be affected in each hazard class',
            function_id='ClassifiedRasterHazardPopulationFunction')
        self.assertTrue(result, message)
        fake_dir = test_data_path()
        scenario_file = unique_filename(
            prefix='scenarioTest', suffix='.txt', dir=fake_dir)
        exposure_layer = str(DOCK.get_exposure_layer().publicSource())
        hazard_layer = str(DOCK.get_hazard_layer().publicSource())

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
