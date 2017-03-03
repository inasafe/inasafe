# coding=utf-8
import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer,
    load_test_vector_layer
)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QGis
from safe.gis.raster.zonal_statistics import zonal_stats

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestReclassifyRaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_zonal_statistics_raster(self):
        """Test we can do zonal statistics."""
        raster = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')
        raster.keywords['inasafe_default_values'] = {}
        vector = load_test_vector_layer(
            'aggregation', 'grid_jakarta_4326.geojson')

        vector.keywords['hazard_keywords'] = {}
        vector.keywords['aggregation_keywords'] = {}

        number_fields = vector.fields().count()
        vector = zonal_stats(raster, vector)

        self.assertEqual(vector.fields().count(), number_fields + 1)
        self.assertEqual(vector.geometryType(), QGis.Polygon)
