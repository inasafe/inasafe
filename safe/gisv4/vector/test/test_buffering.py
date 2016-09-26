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
from collections import OrderedDict

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QGis
from safe.gisv4.vector.buffering import buffering


class TestBuffering(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_buffer_points(self):
        """Test we can buffer points."""
        radii = OrderedDict()
        radii[500] = 'high'
        radii[1000] = 'medium'
        radii[2000] = 'low'

        # Let's add a vector layer.
        layer = load_test_vector_layer('hazard', 'volcano_point.shp')
        keywords = layer.keywords
        self.assertEqual(layer.keywords['layer_geometry'], 'point')

        expected_keywords = keywords.copy()
        expected_keywords['layer_geometry'] = 'polygon'
        result = buffering(
            layer=layer,
            radii=radii)

        self.assertDictEqual(result.keywords, expected_keywords)
        self.assertEqual(result.geometryType(), QGis.Polygon)
        expected_feature_count = layer.featureCount() * len(radii)
        self.assertEqual(result.featureCount(), expected_feature_count)
