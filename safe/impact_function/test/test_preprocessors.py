# coding=utf-8
"""Test for Pre Processors."""

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.core import QgsCoordinateReferenceSystem

from safe.definitions.constants import (
    PREPARE_SUCCESS,
)
from safe.definitions.hazard import hazard_generic
from safe.impact_function.impact_function import ImpactFunction
from safe.test.utilities import load_test_vector_layer, load_test_raster_layer
from safe.processors.pre_processors import (
    pre_processors_nearby_places, pre_processor_earthquake_contour)


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPreProcessors(unittest.TestCase):

    """Test Pre Processors."""

    def test_pre_processors_nearby_places(self):
        """Test the pre_processors_nearby_places"""
        hazard_layer = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)

        # The exposure is not place but buildings
        self.assertFalse(
            pre_processors_nearby_places['condition'](impact_function))

        hazard_layer = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'places.geojson')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)

        # EQ on places, it must be OK.
        self.assertTrue(
            pre_processors_nearby_places['condition'](impact_function))

    def test_pre_processors_earthquake_contour(self):
        """Test the pre_processors_earthquake_contour"""
        hazard_layer = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)

        self.assertTrue(
            pre_processor_earthquake_contour['condition'](impact_function))

        hazard_layer = load_test_raster_layer(
            'hazard', 'classified_flood_20_20.asc')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'places.geojson')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)

        # not ok, since the hazard is flood, not earthquake
        self.assertFalse(
            pre_processor_earthquake_contour['condition'](impact_function))


if __name__ == '__main__':
    unittest.main()
