# coding=utf-8

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'test_tsunami_population_evacuation_raster'
__date__ = '23/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

import unittest

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.impact_function import \
    TsunamiEvacuationFunction
from safe.test.utilities import test_data_path, get_qgis_app, clip_layers
from safe.common.utilities import OrderedDict

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestTsunamiEvacuationRaster(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(TsunamiEvacuationFunction)

    def test_run(self):
        function = TsunamiEvacuationFunction.instance()

        hazard_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        exposure_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        # We need clipping for both layers to be in the same dimension
        clipped_hazard, clipped_exposure = clip_layers(
            hazard_path, exposure_path)

        hazard_layer = read_layer(clipped_hazard.source())
        exposure_layer = read_layer(clipped_exposure.source())

        # Let's set the extent to the hazard extent
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # print "keywords", keywords
        keywords = impact.get_keywords()
        evacuated = float(keywords['evacuated'])
        total_needs_full = keywords['total_needs']
        total_needs_weekly = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['weekly']
        ])
        total_needs_single = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['single']
        ])

        # #FIXME: This doesn't make sense due to clipping above. Update
        # clip_layers
        expected_evacuated = 1300
        self.assertEqual(evacuated, expected_evacuated)
        self.assertEqual(total_needs_weekly['Rice [kg]'], 3640)
        self.assertEqual(total_needs_weekly['Family Kits'], 260)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 22750)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 87100)
        self.assertEqual(total_needs_single['Toilets'], 65)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'tsunami',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'metres'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'exposure': 'population',
            'exposure_unit': 'count'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            TsunamiEvacuationFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
