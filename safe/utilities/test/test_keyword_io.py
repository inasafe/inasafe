# coding=utf-8
"""Tests for keyword io class."""
import unittest

from qgis.core import QgsDataSourceURI, QgsVectorLayer

from safe.definitionsv4.definitions_v3 import inasafe_keyword_version
from safe.common.exceptions import NoKeywordsFoundError
from safe.common.utilities import unique_filename
from safe.test.utilities import (
    load_layer,
    get_qgis_app,
    standard_data_path,
    clone_raster_layer)
from safe.utilities.keyword_io import KeywordIO, definition
from safe.utilities.metadata import read_iso19115_metadata
from safe.utilities.unicode import get_unicode

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class KeywordIOTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

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
        self.raster_layer, _ = load_layer(hazard_path)
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
        self.vector_layer, _ = load_layer(vector_path)
        self.expected_vector_keywords = {
            'keyword_version': '3.5',
            'structure_class_field': 'FLOODED',
            'value_mapping': {},
            'title': 'buildings_osm_4326',
            'layer_geometry': 'polygon',
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'exposure': 'structure',
        }
        # Keyword less layer
        keywordless_path = standard_data_path('other', 'keywordless_layer.shp')
        self.keywordless_layer, _ = load_layer(keywordless_path)
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

    def test_update_keywords(self):
        """Test append file keywords with update_keywords method."""
        self.maxDiff = None
        layer = clone_raster_layer(
            name='tsunami_wgs84',
            extension='.tif',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        new_keywords = {
            'hazard_category': 'multiple_event'
        }
        self.keyword_io.update_keywords(layer, new_keywords)
        keywords = self.keyword_io.read_keywords(layer)
        expected_keywords = {
            'hazard_category': 'multiple_event',
            'title': 'Tsunami',
            'hazard': 'tsunami',
            'continuous_hazard_unit': 'metres',
            'layer_geometry': 'raster',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'keyword_version': inasafe_keyword_version
        }
        expected_keywords = {
            k: get_unicode(v) for k, v in expected_keywords.iteritems()
        }
        self.assertDictEqual(keywords, expected_keywords)

    def test_copy_keywords(self):
        """Test we can copy the keywords."""
        self.maxDiff = None
        out_path = unique_filename(
            prefix='test_copy_keywords', suffix='.shp')
        layer = clone_raster_layer(
            name='generic_continuous_flood',
            extension='.asc',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        self.keyword_io.copy_keywords(layer, out_path)
        # copied_keywords = read_file_keywords(out_path.split('.')[0] + 'xml')
        copied_keywords = read_iso19115_metadata(out_path)
        expected_keywords = self.expected_raster_keywords
        expected_keywords['keyword_version'] = inasafe_keyword_version

        self.assertDictEqual(copied_keywords, expected_keywords)

    def test_definition(self):
        """Test we can get definitions for keywords.

        .. versionadded:: 3.2

        """
        keyword = 'hazards'
        keyword_definition = definition(keyword)
        self.assertTrue('description' in keyword_definition)

    def test_to_message(self):
        """Test we can convert keywords to a message object.

        .. versionadded:: 3.2

        """
        keywords = self.keyword_io.read_keywords(self.vector_layer)
        message = self.keyword_io.to_message(keywords).to_text()
        self.assertIn('*Exposure*, structure------', message)

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
            u'\n---\n*high*, Kawasan Rawan Bencana III------',
            table.to_text())
        # should also work passing a dict
        keyword_value = {
            'high': ['Kawasan Rawan Bencana III'],
            'medium': ['Kawasan Rawan Bencana II'],
            'low': ['Kawasan Rawan Bencana I']}
        table = self.keyword_io._dict_to_row(keyword_value)
        self.assertIn(
            u'\n---\n*high*, Kawasan Rawan Bencana III------',
            table.to_text())

    def test_keyword_io(self):
        """Test read keywords directly from keywords file

        .. versionadded:: 3.2
        """
        self.maxDiff = None
        keywords = self.keyword_io.read_keywords_file(self.keyword_path)
        expected_keywords = self.expected_vector_keywords
        self.assertDictEqual(keywords, expected_keywords)

if __name__ == '__main__':
    suite = unittest.makeSuite(KeywordIOTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
