# coding=utf-8
"""Tests for keyword io class."""
import unittest

from qgis.core import QgsDataSourceURI, QgsVectorLayer

from safe.common.exceptions import NoKeywordsFoundError
from safe.test.utilities import (
    get_qgis_app,
    standard_data_path,
    clone_raster_layer, load_layer)
from safe.utilities.keyword_io import KeywordIO

__copyright__ = "Copyright 2011, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data."""

    def setUp(self):
        self.keyword_io = KeywordIO()

        # SQLite Layer
        uri = QgsDataSourceURI()
        sqlite_building_path = standard_data_path(
            'exposure', 'exposure.sqlite')
        uri.setDatabase(sqlite_building_path)
        uri.setDataSource('', 'buildings_osm_4326', 'Geometry')
        self.sqlite_layer = QgsVectorLayer(
            uri.uri(), 'OSM Buildings', 'spatialite')
        self.expected_sqlite_keywords = {
            'datatype': 'OSM'
        }

        # Raster Layer keywords
        hazard_path = standard_data_path('hazard', 'tsunami_wgs84.tif')
        self.raster_layer, _ = load_layer(hazard_path, provider='gdal')
        self.expected_raster_keywords = {
            'hazard_category': 'single_event',
            'title': 'Generic Continuous Flood',
            'hazard': 'flood',
            'continuous_hazard_unit': 'generic',
            'layer_geometry': 'raster',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'keyword_version': '3.5'
        }

        # Vector Layer keywords
        vector_path = standard_data_path('exposure', 'buildings_osm_4326.shp')
        self.vector_layer, _ = load_layer(vector_path, provider='ogr')
        self.expected_vector_keywords = {
            'keyword_version': '3.5',
            'value_map': {},
            'title': 'buildings_osm_4326',
            'layer_geometry': 'polygon',
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'exposure': 'structure',
        }
        # Keyword less layer
        keywordless_path = standard_data_path('other', 'keywordless_layer.shp')
        self.keywordless_layer, _ = load_layer(
            keywordless_path, provider='ogr')
        # Keyword file
        self.keyword_path = standard_data_path(
            'exposure', 'buildings_osm_4326.xml')

    def test_read_raster_file_keywords(self):
        """Can we read raster file keywords using generic readKeywords method
        """
        layer = clone_raster_layer(
            name='generic_continuous_flood',
            extension='.asc',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        keywords = self.keyword_io.read_keywords(layer)
        expected_keywords = self.expected_raster_keywords

        self.assertDictEqual(keywords, expected_keywords)

    def test_read_vector_file_keywords(self):
        """Test read vector file keywords with the generic readKeywords method.
         """
        self.maxDiff = None
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        expected_keywords = self.expected_vector_keywords

        self.assertDictEqual(keywords, expected_keywords)

    def test_read_keywordless_layer(self):
        """Test read 'keyword' file from keywordless layer.
        """
        self.assertRaises(
            NoKeywordsFoundError,
            self.keyword_io.read_keywords,
            self.keywordless_layer,
            )

    def test_to_message(self):
        """Test we can convert keywords to a message object.

        .. versionadded:: 3.2

        """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        message = self.keyword_io.to_message(keywords).to_text()
        self.assertIn('*Exposure*, Structures------', message)

    def test_layer_to_message(self):
        """Test to show augmented keywords if KeywordsIO ctor passed a layer.

        .. versionadded:: 3.3
        """
        keywords = KeywordIO(self.vector_layer)
        message = keywords.to_message().to_text()
        self.assertIn('*Reference system*, ', message)

    def test_dict_to_row(self):
        """Test the dict to row helper works.

        .. versionadded:: 3.2
        """
        keyword_value = (
            "{'high': ['Kawasan Rawan Bencana III'], "
            "'medium': ['Kawasan Rawan Bencana II'], "
            "'low': ['Kawasan Rawan Bencana I']}")
        table = self.keyword_io._dict_to_row(keyword_value)
        self.assertIn(
            '\n---\n*High*, Kawasan Rawan Bencana III------',
            table.to_text())
        # should also work passing a dict
        keyword_value = {
            'high': ['Kawasan Rawan Bencana III'],
            'medium': ['Kawasan Rawan Bencana II'],
            'low': ['Kawasan Rawan Bencana I']}
        table = self.keyword_io._dict_to_row(keyword_value)
        self.assertIn(
            '\n---\n*High*, Kawasan Rawan Bencana III------',
            table.to_text())


if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
