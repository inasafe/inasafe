import unittest

from safe.test.utilities import get_qgis_app, standard_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.new_impact_function.impact_function import ImpactFunction
from safe.new_impact_function.algorithm.line import LineAlgorithm

from qgis.core import QgsVectorLayer


class TestImpactFunction(unittest.TestCase):
    """Test for Generic Polygon on Building Impact Function."""

    def test_impact_function_behaviour(self):
        """Test behaviour of impact function"""
        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_path = standard_data_path('exposure', 'roads.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Roads', 'ogr')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        self.assertEqual(impact_function.algorithm, LineAlgorithm)
        self.assertEqual(impact_function.name, 'Flood Polygon on Road Line')
        self.assertEqual(impact_function.title, 'be affected')

    def test_run_impact_function(self):
        """Test running impact function on test data."""
        # Set up test data
        hazard_path = standard_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_path = standard_data_path('exposure', 'building-points.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsVectorLayer(hazard_path, 'Flood', 'ogr')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Building Point', 'ogr')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.run()
        result = impact_function.impact_layer
        pass

if __name__ == '__main__':
    unittest.main()