from unittest import TestCase

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsMapLayerRegistry

from PyQt4 import QtCore

from safe.impact_functions import register_impact_functions
from safe.test.utilities import (
    test_data_path,
    load_layer,
    set_canvas_crs,
    GEOCRS,
    setup_scenario,
    get_qgis_app)
from safe.utilities.keyword_io import KeywordIO

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.widgets.dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.widgets.dock import Dock


# noinspection PyArgumentList
class TestDockRegressions(TestCase):
    """Regression tests for the InaSAFE GUI."""

    @classmethod
    def setUpClass(cls):
        cls.dock = Dock(IFACE)

    def setUp(self):
        """Fixture run before all tests.

        These tests require that you manually load the layers you need.
        """
        register_impact_functions()

        self.dock.show_only_visible_layers_flag = True
        self.dock.cboHazard.setCurrentIndex(0)
        self.dock.cboExposure.setCurrentIndex(0)
        self.dock.cboFunction.setCurrentIndex(0)
        self.dock.run_in_thread_flag = False
        self.dock.show_only_visible_layers_flag = False
        self.dock.set_layer_from_title_flag = False
        self.dock.zoom_to_impact_flag = False
        self.dock.hide_exposure_flag = False
        self.dock.show_intermediate_layers = False
        self.dock.user_extent = None
        self.dock.user_extent_crs = None
        # For these tests we will generally use explicit overlap
        # between hazard, exposure and view, so make that default
        # see also safe/test/utilities.py where this is globally
        # set to HazardExposure
        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', 'HazardExposure')
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        self.dock.cboHazard.clear()
        self.dock.cboExposure.clear()

    # noinspection PyUnusedLocal
    def test_regression_2553_no_resample(self):
        """Test for regression 2553 (no resampling).

        see :

        https://github.com/inasafe/inasafe/issues/2553

        We want to verify that population with resampling should produce
        a result within a reasonable range of the same analysis but doing
        population with no resampling.

        """
        hazard_path = test_data_path(
            'hazard', 'continuous_flood_unaligned_big_size.tif')
        exposure_path = test_data_path(
            'exposure', 'people_allow_resampling_false.tif')

        hazard_layer, hazard_layer_purpose = load_layer(hazard_path)
        # Check if there is a regression about keywords being updated from
        # another layer - see #2605
        keywords = KeywordIO(hazard_layer)
        self.assertIn('flood unaligned', keywords.to_message().to_text())

        exposure_layer, exposure_layer_purpose = load_layer(
            exposure_path)
        keywords = KeywordIO(exposure_layer)
        self.assertIn(
            '*Allow resampling*, false------',
            keywords.to_message().to_text())

        QgsMapLayerRegistry.instance().addMapLayers(
            [hazard_layer, exposure_layer])

        # Count the total value of all exposure pixels
        # this is arse about face but width is actually giving height
        height = exposure_layer.width()
        # this is arse about face but height is actually giving width
        width = exposure_layer.height()
        provider = exposure_layer.dataProvider()
        # Bands count from 1!
        block = provider.block(1, provider.extent(), height, width)
        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)

        # This is the nicer way but wierdly it gets nan for every cell
        total_population = 0.0
        cell_count = 0
        row = 0
        # Iterate down each column to match the layout produced by r.stats
        while row < width:
            column = 0
            while column < height:
                cell_count += 1
                value = block.value(row, column)
                if value > 0:
                    total_population += value
                column += 1
            row += 1
        print "Total value of all cells is: %d" % total_population
        print "Number of cells counted: %d" % cell_count

        # 131 computed using r.sum
        self.assertAlmostEqual(total_population, 131.0177006121)

        result, message = setup_scenario(
            self.dock,
            hazard='flood unaligned',
            exposure='People never resample',
            function='Need evacuation',
            function_id='FloodEvacuationRasterHazardFunction')
        self.assertTrue(result, message)
        # Press RUN
        self.dock.accept()

        safe_layer = self.dock.impact_function.impact_layer
        keywords = safe_layer.get_keywords()
        evacuated = float(keywords['evacuated'])
        self.assertLess(evacuated, total_population)
        expected_evacuated = 131.0
        self.assertEqual(evacuated, expected_evacuated)

    # noinspection PyUnusedLocal
    def test_regression_2553_with_resample(self):
        """Test for regression 2553 (with resampling).

        see :

        https://github.com/inasafe/inasafe/issues/2553

        We want to verify that population with resampling should produce
        a result within a reasonable range of the same analysis but doing
        population with no resampling.

        """
        hazard_path = test_data_path(
            'hazard', 'continuous_flood_unaligned_big_size.tif')
        exposure_path = test_data_path(
            'exposure', 'people_allow_resampling_true.tif')
        hazard_layer, hazard_layer_purpose = load_layer(hazard_path)
        # Check if there is a regression about keywords being updated from
        # another layer - see #2605
        keywords = KeywordIO(hazard_layer)
        self.assertIn('flood unaligned', keywords.to_message().to_text())
        # check we have the right layer properties
        exposure_layer, exposure_layer_purpose = load_layer(
            exposure_path)
        keywords = KeywordIO(exposure_layer)
        self.assertNotIn(
            '*Allow resampling*, false------',
            keywords.to_message().to_text())

        QgsMapLayerRegistry.instance().addMapLayers(
            [hazard_layer, exposure_layer])

        # Count the total value of all exposure pixels
        # this is arse about face but width is actually giving height
        height = exposure_layer.width()
        # this is arse about face but height is actually giving width
        width = exposure_layer.height()
        provider = exposure_layer.dataProvider()
        # Bands count from 1!
        block = provider.block(1, provider.extent(), height, width)
        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)

        # This is the nicer way but wierdly it gets nan for every cell
        total_population = 0.0
        cell_count = 0
        row = 0
        # Iterate down each column to match the layout produced by r.stats
        while row < width:
            column = 0
            while column < height:
                cell_count += 1
                value = block.value(row, column)
                if value > 0:
                    total_population += value
                column += 1
            row += 1
        print "Total value of all cells is: %d" % total_population
        print "Number of cells counted: %d" % cell_count

        result, message = setup_scenario(
            self.dock,
            hazard='flood unaligned',
            exposure='People allow resampling',
            function='Need evacuation',
            function_id='FloodEvacuationRasterHazardFunction')
        self.assertTrue(result, message)
        # Press RUN
        self.dock.accept()

        safe_layer = self.dock.impact_function.impact_layer
        keywords = safe_layer.get_keywords()
        evacuated = float(keywords['evacuated'])
        self.assertLess(evacuated, total_population)
        expected_evacuated = 127.0
        self.assertEqual(evacuated, expected_evacuated)
