# coding=utf-8

import unittest

from safe.test.utilities import standard_data_path
from safe.test.qgis_app import qgis_app
from safe.gis.tools import load_layer, full_layer_uri

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

qgis_app()


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
