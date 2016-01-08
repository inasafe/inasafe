# coding=utf-8
"""Tests for utilities."""

import unittest
import os
import codecs
import shutil
from unittest import expectedFailure

from safe.definitions import inasafe_keyword_version
from safe.utilities.utilities import (
    get_error_message,
    humanise_seconds,
    impact_attribution,
    replace_accentuated_characters,
    read_file_keywords,
    is_keyword_version_supported
)
from safe.utilities.gis import qgis_version
from safe.test.utilities import (
    test_data_path,
    get_qgis_app,
    clone_raster_layer
)
from safe.common.exceptions import KeywordNotFoundError
from safe.storage.utilities import bbox_intersection

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class UtilitiesTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_stacktrace_html(self):
        """Stack traces can be caught and rendered as html
        """

        # This is about general exception handling, so ok to use catch-all
        # pylint: disable=W0703
        try:
            bbox_intersection('aoeu', 'oaeu', [])
        except Exception, e:
            # Display message and traceback

            message = get_error_message(e)
            # print message
            message = message.to_text()
            self.assertIn(str(e), message)
            self.assertIn('line', message)
            self.assertIn('file', message)

            message = get_error_message(e)
            message = message.to_html()
            assert str(e) in message

            message = message.decode('string_escape')
            control_file_path = test_data_path(
                'control',
                'files',
                'test-stacktrace-html.txt')
            expected_results = open(control_file_path).read().replace('\n', '')
            self.assertIn(expected_results, message)

            # pylint: enable=W0703

    def test_get_qgis_version(self):
        """Test we can get the version of QGIS"""
        version = qgis_version()
        message = 'Got version %s of QGIS, but at least 107000 is needed'
        assert version > 10700, message

    def test_humanize_seconds(self):
        """Test that humanise seconds works."""
        self.assertEqual(humanise_seconds(5), '5 seconds')
        self.assertEqual(humanise_seconds(65), 'a minute')
        self.assertEqual(humanise_seconds(3605), 'over an hour')
        self.assertEqual(humanise_seconds(9000), '2 hours and 30 minutes')
        self.assertEqual(humanise_seconds(432232),
                         '5 days, 0 hours and 3 minutes')

    def test_accentuated_characters(self):
        """Test that accentuated characters has been replaced."""
        self.assertEqual(
            replace_accentuated_characters(u'áéíóúýÁÉÍÓÚÝ'), 'aeiouyAEIOUY')

    def test_impact_layer_attribution(self):
        """Test we get an attribution html snippet nicely for impact layers."""
        keywords = {
            'hazard_title': 'Sample Hazard Title',
            'hazard_source': 'Sample Hazard Source',
            'exposure_title': 'Sample Exposure Title',
            'exposure_source': 'Sample Exposure Source'}
        attribution = impact_attribution(keywords)
        control_file_path = test_data_path(
            'control',
            'files',
            'impact-layer-attribution.txt')
        expected_result = codecs.open(
            control_file_path,
            mode='r',
            encoding='utf-8').readlines()

        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, attribution.to_text())

    @expectedFailure
    def test_localised_attribution(self):
        """Test we can localise attribution."""
        os.environ['LANG'] = 'id'
        keywords = {
            'hazard_title': 'Jakarta 2007 flood',
            'hazard_source': 'Sample Hazard Source',
            'exposure_title': 'People in Jakarta',
            'exposure_source': 'Sample Exposure Source'}
        html = impact_attribution(keywords, True)
        print html
        assert html == '11'

        # Set back to en
        os.environ['LANG'] = 'en'

    def test_get_keyword_from_file(self):
        """Get keyword from a filesystem file's .keyword file."""
        raster_layer = clone_raster_layer(
            'jakarta_flood_design', '.tif', False, test_data_path('hazard'))

        raster_layer_path = raster_layer.source()

        keyword_file = test_data_path('other', 'jakarta_flood_design.keywords')

        raster_keyword_path = (
            os.path.splitext(raster_layer_path)[0] + '.keywords')

        shutil.copy2(keyword_file, raster_keyword_path)

        keyword = read_file_keywords(raster_layer_path, 'layer_purpose')
        expected_keyword = 'hazard'
        self.assertEqual(keyword, expected_keyword)

        # Test we get an exception if keyword is not found
        self.assertRaises(
            KeywordNotFoundError,
            read_file_keywords, raster_layer_path, 'boguskeyword')

        # Test if all the keywords are all ready correctly
        keywords = read_file_keywords(raster_layer_path)
        expected_keywords = {
            'hazard_category': 'single_event',
            'hazard': 'flood',
            'continuous_hazard_unit': 'metres',
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'title': 'Jakarta flood like 2007 with structural improvements',
            'keyword_version': '3.2'
        }
        self.assertDictEqual(keywords, expected_keywords)

    def test_is_keyword_version_supported(self):
        """Test for is_keyword_version_supported."""
        self.assertTrue(is_keyword_version_supported('3.2', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2', '3.3'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1-alpha', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.3'))
        self.assertFalse(is_keyword_version_supported('3.02.1', '3.2'))


if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
