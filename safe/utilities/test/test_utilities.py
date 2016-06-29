# coding=utf-8
"""Tests for utilities."""

import unittest
import os
import codecs
from unittest import expectedFailure

from safe.test.utilities import (
    standard_data_path,
    get_qgis_app,
)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.utilities.utilities import (
    get_error_message,
    humanise_seconds,
    impact_attribution,
    replace_accentuated_characters,
    reorder_dictionary,
    main_type,
    is_keyword_version_supported
)
from safe.utilities.gis import qgis_version

from safe.storage.utilities import bbox_intersection


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
            control_file_path = standard_data_path(
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
        control_file_path = standard_data_path(
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
        assert html == '11'

        # Set back to en
        os.environ['LANG'] = 'en'

    def test_is_keyword_version_supported(self):
        """Test for is_keyword_version_supported."""
        self.assertTrue(is_keyword_version_supported('3.2', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2', '3.3'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1-alpha', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.3'))
        self.assertFalse(is_keyword_version_supported('3.02.1', '3.2'))

    def test_order_dictionary(self):
        """Test if we can reorder a dictionary correctly."""
        unordered = {
            1: 'a',
            2: 'b',
            3: 'c',
            4: 'd',
            5: 'e'
        }
        expected = [5, 4, 3, 2, 1]

        new_dict = reorder_dictionary(unordered, expected)
        self.assertItemsEqual(expected, new_dict.keys())

        # These keys don't exist, we expect an empty dictionary.
        expected = ['Z', 'X', 'Y']
        new_dict = reorder_dictionary(unordered, expected)
        self.assertEqual(len(new_dict), 0)

    def test_main_type(self):
        """Test the good feature type according to the value mapping."""
        mapping = {
            'residential': ['house', 'apartments', 'residential'],
            'industrial': ['commercial', 'retail']
        }
        self.assertEqual(main_type('residential', mapping), 'residential')
        self.assertEqual(main_type('house', mapping), 'residential')
        self.assertEqual(main_type('apartments', mapping), 'residential')
        self.assertEqual(main_type('warehouse', mapping), 'other')
        self.assertEqual(main_type(None, mapping), 'other')
        self.assertEqual(main_type('null', mapping), 'other')

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
