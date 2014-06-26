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

from safe.common.testing import TESTDATA, get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.tools.save_scenario import SaveScenarioDialog
from safe_qgis.utilities.utilities_for_testing import (
    setup_scenario,
    set_canvas_crs,
    set_jakarta_extent,
    load_standard_layers,
    GEOCRS)
from safe_qgis.safe_interface import (
    unique_filename,
    temp_dir)
from safe_qgis.widgets.dock import Dock

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

    def tearDown(self):
        """Fixture run after each test"""
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()
        #DOCK.cboAggregation.clear() #dont do this because the cboAggregation
        # need to be able to react to the status changes of the other combos
        self.save_scenario_dialog = None

    def test_validate_input(self):
        """Test validate input."""
        # Valid Case
        result, message = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
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
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

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
        self.assertTrue(title == '[Flood in Jakarta]', 'Title is not the same')
        self.assertTrue(
            exposure.startswith('exposure =') and exposure.endswith(
                'Population_Jakarta_geographic.asc'),
            'Exposure is not the same')
        self.assertTrue(
            hazard.startswith('hazard =') and hazard.endswith(
                'jakarta_flood_category_123.asc'),
            'Hazard is not the same')
        self.assertTrue(
            function == (
                'function = Categorised Hazard Population Impact Function'),
            'Impact function is not same')
        expected_extent = (
            'extent = 106.313333, -6.380000, 107.346667, -6.070000')
        self.assertEqual(expected_extent, extent)

    def test_relative_path(self):
        """Test we calculate the relative paths correctly when saving scenario.
        """
        result, message = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        self.assertTrue(result, message)
        fake_dir = os.path.dirname(TESTDATA)
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
                'test\\Population_Jakarta_geographic.asc',
                relative_exposure)
            self.assertEqual(
                'hazard\\jakarta_flood_category_123.asc',
                relative_hazard)

        else:
            self.assertEqual(
                'test/Population_Jakarta_geographic.asc',
                relative_exposure)
            self.assertEqual(
                'hazard/jakarta_flood_category_123.asc',
                relative_hazard)
