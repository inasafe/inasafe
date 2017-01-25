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
    humanise_seconds,
    impact_attribution,
    replace_accentuated_characters,
    is_keyword_version_supported
)
from safe.utilities.gis import qgis_version


class UtilitiesTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

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

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
