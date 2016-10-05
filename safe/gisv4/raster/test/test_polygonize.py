# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsFeatureRequest

from safe.gisv4.raster.polygonize import polygonize
from safe.definitionsv4.layer_geometry import (
    layer_geometry, layer_geometry_polygon)
from safe.definitionsv4.fields import hazard_class_field


class TestReclassifyRaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reclassify_raster(self):
        """Test we can reclassify a raster layer."""
        layer = load_test_raster_layer('hazard', 'classified_flood_20_20.asc')

        expected_keywords = layer.keywords.copy()
        expected_keywords[
            layer_geometry['key']] = layer_geometry_polygon['key']
        expected_keywords['inasafe_fields'] = {
            hazard_class_field['key']: hazard_class_field['field_name']}

        polygonized = polygonize(layer)

        self.assertEqual(polygonized.name(), 'polygonized')
        self.assertDictEqual(polygonized.keywords, expected_keywords)

        self.assertEqual(polygonized.featureCount(), 400)

        expected_count = {
            '1': 133,
            '2': 134,
            '3': 133,
        }

        inasafe_fields = polygonized.keywords.get('inasafe_fields')
        field_name = inasafe_fields.get(hazard_class_field['key'])

        for value, count in expected_count.iteritems():
            expression = '"%s" = \'%s\'' % (field_name, value)
            request = QgsFeatureRequest().setFilterExpression(expression)
            self.assertEqual(
                sum(1 for _ in polygonized.getFeatures(request)), count)
