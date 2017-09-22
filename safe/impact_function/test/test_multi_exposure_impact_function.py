# coding=utf-8

"""Test for Multi Exposure Impact Function."""

import unittest
import logging

from safe.definitions.constants import (
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_SUCCESS,
    ANALYSIS_SUCCESS,
)
from safe.test.utilities import qgis_iface, load_test_vector_layer
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)


LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


qgis_iface()


class TestImpactFunction(unittest.TestCase):

    """Test Multi Exposure Impact Function."""

    def test_bad_multi(self):
        """Test that the 'prepare' state can failed."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        population_bis = load_test_vector_layer(
            'gisv4', 'exposure', 'population_multi_fields.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Same population exposure
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [population_layer, population_bis]
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_FAILED_BAD_INPUT)

        # Missing exposure layer
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = []
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_FAILED_BAD_INPUT)

        # Normal multi exposure
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [population_layer, roads_layer]
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_SUCCESS)

    def test_multi_exposure(self):
        """Test we can run a multi exposure analysis."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        building_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [
            building_layer, population_layer, roads_layer]
        impact_function.aggregation = aggregation_layer

        code, message = impact_function.prepare()
        self.assertEqual(code, PREPARE_SUCCESS, message)

        code, message = impact_function.run()
        self.assertEqual(code, ANALYSIS_SUCCESS, message)
