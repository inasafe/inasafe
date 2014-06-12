# coding=utf-8
"""Tests for utilities."""
import unittest
import sys
import os

from unittest import expectedFailure

# noinspection PyPackageRequirements
from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.utilities.defaults import breakdown_defaults
from safe_qgis.utilities.utilities import (
    get_error_message,
    qgis_version,
    mm_to_points,
    points_to_mm,
    humanise_seconds,
    is_polygon_layer,
    layer_attribute_names,
    impact_attribution,
    dpi_to_meters,
    qt_at_least)
from safe_qgis.utilities.utilities_for_testing import (
    TEST_FILES_DIR)
from safe_qgis.tools.test.test_keywords_dialog import (
    make_polygon_layer,
    make_padang_layer,
    make_point_layer)
from safe_qgis.safe_interface import bbox_intersection


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
            #print message
            message = message.to_text()
            self.assertIn(str(e), message)
            self.assertIn('line', message)
            self.assertIn('file', message)

            message = get_error_message(e)
            message = message.to_html()
            assert str(e) in message

            message = message.decode('string_escape')
            expected_results = open(
                TEST_FILES_DIR +
                '/test-stacktrace-html.txt', 'r').read().replace('\n', '')
            self.assertIn(expected_results, message)

        # pylint: enable=W0703

    def test_get_qgis_version(self):
        """Test we can get the version of QGIS"""
        version = qgis_version()
        message = 'Got version %s of QGIS, but at least 107000 is needed'
        assert version > 10700, message

    def test_get_layer_attribute_names(self):
        """Test we can get the correct attributes back"""
        layer = make_polygon_layer()

        #with good attribute name
        attributes, position = layer_attribute_names(layer, [
            QVariant.Int, QVariant.String],
            'TEST_STRIN')  # Not a typo...
        expected_attributes = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        expected_position = 2
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        assert (attributes == expected_attributes), message
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        assert (position == expected_position), message

        #with non existing attribute name
        attributes, position = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String],
            'MISSING_ATTR')
        expected_attributes = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        expected_position = None
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        assert (attributes == expected_attributes), message
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        assert (position == expected_position), message

        #with raster layer
        layer = make_padang_layer()
        attributes, position = layer_attribute_names(layer, [], '')
        message = 'Should return None, None for raster layer, got %s, %s' % (
            attributes, position)
        assert (attributes is None and position is None), message

    def test_is_polygonal_layer(self):
        """Test we can get the correct attributes back"""
        layer = make_polygon_layer()
        message = 'isPolygonLayer, %s layer should be polygonal' % layer
        assert is_polygon_layer(layer), message

        layer = make_point_layer()
        message = '%s layer should be polygonal' % layer
        assert not is_polygon_layer(layer), message

        layer = make_padang_layer()
        message = ('%s raster layer should not be polygonal' % layer)
        assert not is_polygon_layer(layer), message

    def test_get_defaults(self):
        """Test defaults for post processing can be obtained properly."""
        # Warning this code is duplicated from test_defaults...TS
        expected = {
            'ADULT_RATIO_KEY': 'adult ratio default',
            'ADULT_RATIO_ATTR_KEY': 'adult ratio attribute',
            'ADULT_RATIO': 0.659,

            'FEMALE_RATIO_KEY': 'female ratio default',
            'FEMALE_RATIO_ATTR_KEY': 'female ratio attribute',
            'FEMALE_RATIO': 0.5,

            'ELDERLY_RATIO_ATTR_KEY': 'elderly ratio attribute',
            'ELDERLY_RATIO_KEY': 'elderly ratio default',
            'ELDERLY_RATIO': 0.078,

            'YOUTH_RATIO': 0.263,
            'YOUTH_RATIO_ATTR_KEY': 'youth ratio attribute',
            'YOUTH_RATIO_KEY': 'youth ratio default',

            'NO_DATA': u'No data',

            'AGGR_ATTR_KEY': 'aggregation attribute'}
        defaults = breakdown_defaults()
        self.assertDictEqual(defaults, expected)

    def test_mm_to_points(self):
        """Test that conversions between pixel and page dimensions work."""

        dpi = 300
        pixels = 300
        mm = 25.4  # 1 inch
        result = points_to_mm(pixels, dpi)
        message = "Expected: %s\nGot: %s" % (mm, result)
        assert result == mm, message
        result = mm_to_points(mm, dpi)
        message = "Expected: %s\nGot: %s" % (pixels, result)
        assert result == pixels, message

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

    def test_dpi_to_meters(self):
        """Test conversion from dpi to dpm."""
        dpi = 300
        dpm = dpi_to_meters(dpi)
        expected_dpm = 11811.023622
        message = (
            'Conversion from dpi to dpm failed\n'
            ' Got: %s Expected: %s\n' %
            (dpm, expected_dpm))
        self.assertAlmostEqual(dpm, expected_dpm, msg=message)

    def test_qt_at_least(self):
        """Test that we can compare the installed qt version"""
        # simulate 4.7.2 installed
        test_version = 0x040702

        assert qt_at_least('4.6.4', test_version)
        assert qt_at_least('4.7.2', test_version)
        assert not qt_at_least('4.8.4', test_version)

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
