# coding=utf-8
"""Tests for engine.core."""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe'
__filename__ = 'test_core'
__date__ = '12/29/15'
__copyright__ = 'imajimatika@gmail.com'


import unittest
from safe.test.utilities import get_qgis_app, test_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.earthquake.earthquake_building.\
    impact_function import EarthquakeBuildingFunction
from safe.test.utilities import test_data_path
from safe.storage.core import read_layer
from safe.storage.safe_layer import SafeLayer

from safe.engine.core import calculate_impact


class TestCore(unittest.TestCase):
    def test_calculate_impact(self):
        """Test calculating impact."""
        eq_path = test_data_path('hazard', 'earthquake.tif')
        building_path = test_data_path('exposure', 'buildings.shp')

        eq_layer = read_layer(eq_path)
        building_layer = read_layer(building_path)

        impact_function = EarthquakeBuildingFunction.instance()
        impact_function.hazard = SafeLayer(eq_layer)
        impact_function.exposure = SafeLayer(building_layer)
        impact_layer = calculate_impact(impact_function)

        self.assertIsNotNone(impact_layer)

if __name__ == '__main__':
    unittest.main()
