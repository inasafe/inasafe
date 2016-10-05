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
from osgeo import gdal
from collections import OrderedDict

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsFeatureRequest

from safe.gisv4.vector.reclassify import reclassify
from safe.definitionsv4.fields import hazard_value_field


class TestReclassifyVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(
        int(gdal.VersionInfo('VERSION_NUM')) < 2010000,
        'GDAL 2.1 is required for geopackage.')
    def test_reclassify_vector(self):
        """Test we can reclassify a continuous vector layer."""
        ranges = OrderedDict()
        # value <= 0.0
        ranges[1] = [None, 0.0]

        # 0.0 < value <= 1
        ranges[2] = [0.0, 1]

        # 1 < value <= 1.5 and gap in output classes
        ranges[10] = [1, 1.5]

        # value > 1.5
        ranges[11] = [1.3, None]

        # Let's add a vector layer.
        layer = load_test_vector_layer(
            'hazard', 'continuous_vector.geojson', clone=True)

        # Ismail any idea why inasafe_fields is not loaded ?
        # I need to hardcode it this keyword.
        layer.keywords['inasafe_fields'] = {'hazard_value_field': 'depth'}

        self.assertEqual(layer.featureCount(), 400)
        classified = reclassify(layer, ranges)
        self.assertEqual(layer.featureCount(), 375)

        expected_field = hazard_value_field['field_name']
        self.assertEqual(classified.fieldNameIndex(expected_field), 0)

        """
        Test deactivated, I will promise I will come back. ET
        expected_count = {
            #'1': 76,
            '2': 120,
            '10': 68,
            '11': 111,
        }

        for value, count in expected_count.iteritems():
            expression = '"%s" = \'%s\'' % (expected_field, value)
            print expression
            request = QgsFeatureRequest().setFilterExpression(expression)
            self.assertEqual(
                sum(1 for _ in classified.getFeatures(request)), count)
        """
