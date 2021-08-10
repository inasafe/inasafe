# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import standard_data_path
from safe.gis.tools import load_layer, full_layer_uri

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


class GisToolsTest(unittest.TestCase):

    def test_load_layer_from_uri(self):
        """Test we can load a layer with different parameters."""
        # Without provider
        path = standard_data_path(
            'gisv4', 'aggregation', 'small_grid.geojson')
        layer, purpose = load_layer(path)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'small_grid')
        self.assertEqual(purpose, 'aggregation')

        layer, purpose = load_layer(path, 'foo')
        self.assertEqual(layer.name(), 'foo')

        # With internal URI
        internal_uri = full_layer_uri(layer)
        self.assertTrue(
            internal_uri.endswith('small_grid.geojson|qgis_provider=ogr'),
            internal_uri
        )
        layer, purpose = load_layer(full_layer_uri(layer))
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'small_grid')
        self.assertEqual(purpose, 'aggregation')

        # path plus extra layer parameter
        path = standard_data_path(
            'gisv4', 'aggregation', 'small_grid.geojson')
        path += '|layerid=0'
        layer, purpose = load_layer(path)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'small_grid')
        self.assertEqual(purpose, 'aggregation')

        # CSV
        path = standard_data_path(
            'gisv4', 'impacts', 'exposure_summary_table.csv')
        layer, purpose = load_layer(path)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'exposure_summary_table')
        self.assertEqual(purpose, 'undefined')
        self.assertEqual(len(layer.fields()), 4)

        # QLR
        # This QLR contains a file based reference layer to
        # small_grid.geojson, and it should work the same way
        # as if we load small_grid.geojson
        # In practice we could put the non file-based layer (PostGIS/WFS)
        # and load it from QLR
        path = standard_data_path(
            'gisv4', 'aggregation', 'small_grid.qlr')
        layer, purpose = load_layer(path)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'small_grid')
        self.assertEqual(purpose, 'aggregation')

    @unittest.skipIf(True, 'You need a PostGIS database and edit the URI.')
    def test_load_layer_from_uri_with_postgis(self):
        """Test we can load a layer with different parameters in POSTGIS."""
        uri = (
            'dbname=\'stdm\' '
            'host=localhost '
            'port=5433 '
            'user=\'etienne\' '
            'sslmode=disable '
            'key=\'id\' '
            'srid=4326 '
            'type=MultiPolygon '
            'table="public"."buildings" (geom) sql='
        )
        layer, purpose = load_layer(uri)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), 'buildings')
        self.assertEqual(purpose, 'undefined')

        expected = '"public"."buildings" (geom) sql=|qgis_provider=postgres'
        internal_uri = full_layer_uri(layer)
        self.assertTrue(
            internal_uri.endswith(expected), internal_uri)
