# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Classified Hazard Land Cover Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from qgis.core import QgsVectorLayer, QgsRasterLayer

from safe.test.utilities import get_qgis_app, test_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.inundation.tsunami_raster_landcover. \
    impact_function import TsunamiRasterLandcoverFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.utilities import safe_to_qgis_layer


class TestClassifiedPolygonLandCoverFunction(unittest.TestCase):
    """Test for Classified Polygon Land Cover Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(TsunamiRasterLandcoverFunction)

    def test_run(self):
        function = TsunamiRasterLandcoverFunction.instance()

        hazard_path = test_data_path('hazard', 'tsunami_wgs84.tif')
        exposure_path = test_data_path('exposure', 'landcover.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsRasterLayer(hazard_path, 'Tsunami')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Land Cover', 'ogr')
        self.assertEqual(hazard_layer.isValid(), True)
        self.assertEqual(exposure_layer.isValid(), True)

        rect_extent = [106.5, -6.5, 107, -6]
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.requested_extent = rect_extent
        function.run()
        impact = function.impact

        impact = safe_to_qgis_layer(impact)

        self.assertEqual(impact.dataProvider().featureCount(), 72)
        features = {}
        exposure_field = function.exposure.keyword('field')
        for f in impact.getFeatures():
            type_tuple = f[exposure_field], f[function.target_field]
            features[type_tuple] = round(f.geometry().area(), 1)

        expected_features = {
            (u'Population', u'Dry Zone'): 7977390.3,
            (u'Population', u'Low Hazard Zone'): 403.8,
            (u'Population', u'Medium Hazard Zone'): 156692.3,
            (u'Population', u'High Hazard Zone'): 298791.1,
            (u'Population', u'Very High Hazard Zone'): 8884.6,
            (u'Water', u'Dry Zone'): 403.8,
            (u'Water', u'Low Hazard Zone'): 65836.7,
            (u'Water', u'Medium Hazard Zone'): 34746.7,
            (u'Water', u'High Hazard Zone'): 9310.4,
            (u'Water', u'Very High Hazard Zone'): 807.7,
            (u'Meadow', u'Dry Zone'): 2512444.0,
            (u'Forest', u'Dry Zone'): 1000000.0
        }
        self.assertEqual(len(expected_features.keys()), len(features.keys()))
        for key, value in expected_features.iteritems():
            result = features[key]
            msg = '%s is different than %s, I got %s' % (key, value, result)
            self.assertEqual(value, result, msg)

    def test_keywords(self):

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'exposure': 'land_cover',
            'field': 'FCODE',
        }

        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'tsunami',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'metres'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
