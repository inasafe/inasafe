# coding=utf-8
"""Tests for utilities."""
import unittest
import sys
import os
from unittest import expectedFailure

# noinspection PyUnresolvedReferences
import qgis

from safe.common.testing import TESTDATA, HAZDATA, EXPDATA, get_qgis_app
from safe.utilities.utilities import (
    get_error_message,
    humanise_seconds,
    impact_attribution,
    read_file_keywords)
from safe.utilities.gis import qgis_version
from safe.test.utilities import test_data_path
from safe.common.exceptions import KeywordNotFoundError
from safe.storage.utilities import bbox_intersection

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)


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

    def test_impact_layer_attribution(self):
        """Test we get an attribution html snippet nicely for impact layers."""
        keywords = {
            'hazard_title': 'Sample Hazard Title',
            'hazard_source': 'Sample Hazard Source',
            'exposure_title': 'Sample Exposure Title',
            'exposure_source': 'Sample Exposure Source'}
        attribution = impact_attribution(keywords)
        print attribution
        # noinspection PyArgumentList
        self.assertEqual(len(attribution.to_text()), 170)

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

        vector_path = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        raster_shake_path = os.path.join(
            HAZDATA, 'Shakemap_Padang_2009.asc')
        raster_tsunami_path = os.path.join(
            TESTDATA, 'tsunami_max_inundation_depth_utm56s.tif')
        raster_exposure_path = os.path.join(
            TESTDATA, 'tsunami_building_exposure.shp')
        raster_population_path = os.path.join(EXPDATA, 'glp10ag.asc')

        keyword = read_file_keywords(raster_shake_path, 'category')
        expected_keyword = 'hazard'
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
            keyword, expected_keyword, raster_shake_path)
        self.assertEqual(keyword, 'hazard', message)

        # Test we get an exception if keyword is not found
        try:
            _ = read_file_keywords(raster_shake_path, 'boguskeyword')
        except KeywordNotFoundError:
            pass  # this is good
        except Exception, e:
            message = ('Request for bogus keyword raised incorrect '
                       'exception type: \n %s') % str(e)
            assert (), message

        keywords = read_file_keywords(raster_shake_path)

        expected_keywords = {
            'category': 'hazard',
            'subcategory': 'earthquake',
            'source': 'USGS',
            'unit': 'MMI',
            'title': 'An earthquake in Padang like in 2009'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(raster_population_path)
        expected_keywords = {
            'category': 'exposure',
            'source': ('Center for International Earth Science Information '
                       'Network (CIESIN)'),
            'subcategory': 'population',
            'datatype': 'density',
            'title': 'People'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(vector_path)
        expected_keywords = {
            'category': 'exposure',
            'datatype': 'itb',
            'subcategory': 'structure',
            'title': 'Padang WGS84'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        # tsunami example (one layer is UTM)
        keywords = read_file_keywords(raster_tsunami_path)
        expected_keywords = {
            'title': 'Tsunami Max Inundation',
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'm'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(raster_exposure_path)
        expected_keywords = {
            'category': 'exposure',
            'subcategory': 'structure',
            'title': 'Tsunami Building Exposure'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
