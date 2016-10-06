# coding=utf-8

import unittest
from osgeo import gdal
from collections import OrderedDict

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsFeatureRequest

from safe.gisv4.vector.reclassify import reclassify
from safe.definitionsv4.fields import hazard_class_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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

        self.assertEqual(layer.featureCount(), 400)
        classified = reclassify(layer, ranges)
        self.assertEqual(layer.featureCount(), 375)

        expected_field = hazard_class_field['field_name']
        self.assertEqual(classified.fieldNameIndex(expected_field), 1)

        self.assertEqual(
            layer.keywords['inasafe_fields'][hazard_class_field['key']],
            hazard_class_field['field_name'])

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
