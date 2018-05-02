# coding=utf-8
"""Test converting geojson to shapefile."""

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer,
)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gis.vector.convert_geojson_to_shapefile import (
    convert_geojson_to_shapefile
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestConvertGeoJSONtoShapefile(unittest.TestCase):

    def test_convert_geojson_to_shapefile(self):
        """Test convert_geojson_to_shapefile"""
        layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson', clone=True)

        flag = convert_geojson_to_shapefile(layer.source())
        self.assertTrue(flag)
