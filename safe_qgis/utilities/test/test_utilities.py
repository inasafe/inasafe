import unittest
import sys
import os

from unittest import expectedFailure

from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
from safe.common.testing import get_qgis_app

pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

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
    which,
    get_utm_zone,
    get_utm_epsg)
from safe_qgis.utilities.utilities_for_testing import (
    TEST_FILES_DIR)
from safe_qgis.tools.test.test_keywords_dialog import (
    make_polygon_layer,
    make_padang_layer,
    make_point_layer)
from safe_qgis.safe_interface import bbox_intersection

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

    def test_get_utm_epsg(self):
        """Test we can get correct epsg code"""
        # North semisphere
        self.assertEqual(get_utm_epsg(-178, 10), 32601)
        self.assertEqual(get_utm_epsg(178, 20), 32660)
        self.assertEqual(get_utm_epsg(-3, 30), 32630)
        # South semisphere:
        self.assertEqual(get_utm_epsg(-178, -10), 32701)
        self.assertEqual(get_utm_epsg(178, -20), 32760)
        self.assertEqual(get_utm_epsg(-3, -30), 32730)

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
            myExpectedResult = open(
                TEST_FILES_DIR +
                '/test-stacktrace-html.txt', 'r').read().replace('\n', '')
            self.assertIn(myExpectedResult, message)

        # pylint: enable=W0703

    def test_getQgisVersion(self):
        """Test we can get the version of QGIS"""
        myVersion = qgis_version()
        message = 'Got version %s of QGIS, but at least 107000 is needed'
        assert myVersion > 10700, message

    def test_getLayerAttributeNames(self):
        """Test we can get the correct attributes back"""
        layer = make_polygon_layer()

        #with good attribute name
        myAttrs, myPos = layer_attribute_names(layer, [
            QVariant.Int, QVariant.String],
            'TEST_STRIN')  # Not a typo...
        myExpectedAttrs = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        myExpectedPos = 2
        message = 'myExpectedAttrs, got %s, expected %s' % (
            myAttrs, myExpectedAttrs)
        assert (myAttrs == myExpectedAttrs), message
        message = 'myExpectedPos, got %s, expected %s' % (
            myPos, myExpectedPos)
        assert (myPos == myExpectedPos), message

        #with inexistent attribute name
        myAttrs, myPos = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String],
            'MISSING_ATTR')
        myExpectedAttrs = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        myExpectedPos = None
        message = 'myExpectedAttrs, got %s, expected %s' % (
            myAttrs, myExpectedAttrs)
        assert (myAttrs == myExpectedAttrs), message
        message = 'myExpectedPos, got %s, expected %s' % (
            myPos, myExpectedPos)
        assert (myPos == myExpectedPos), message

        #with raster layer
        layer = make_padang_layer()
        myAttrs, myPos = layer_attribute_names(layer, [], '')
        message = 'Should return None, None for raster layer, got %s, %s' % (
            myAttrs, myPos)
        assert (myAttrs is None and myPos is None), message

    def test_isLayerPolygonal(self):
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

    def test_getDefaults(self):
        """Test defaults for post processing can be obtained properly."""
        myExpectedDefaults = {
            'FEM_RATIO_KEY': 'female ratio default',
            'YOUTH_RATIO': 0.263,
            'ELDER_RATIO': 0.078,
            'NO_DATA': 'No data',
            'FEM_RATIO': 0.5,
            'AGGR_ATTR_KEY': 'aggregation attribute',
            'FEM_RATIO_ATTR_KEY': 'female ratio attribute',
            'ADULT_RATIO': 0.659}
        myDefaults = breakdown_defaults()
        message = 'Defaults: got %s, expected %s' % (
            myDefaults, myExpectedDefaults)
        assert (myDefaults == myExpectedDefaults), message

    def test_mmPointConversion(self):
        """Test that conversions between pixel and page dimensions work."""

        myDpi = 300
        myPixels = 300
        myMM = 25.4  # 1 inch
        myResult = points_to_mm(myPixels, myDpi)
        message = "Expected: %s\nGot: %s" % (myMM, myResult)
        assert myResult == myMM, message
        myResult = mm_to_points(myMM, myDpi)
        message = "Expected: %s\nGot: %s" % (myPixels, myResult)
        assert myResult == myPixels, message

    def test_humaniseSeconds(self):
        """Test that humanise seconds works."""
        self.assertEqual(humanise_seconds(5), '5 seconds')
        self.assertEqual(humanise_seconds(65), 'a minute')
        self.assertEqual(humanise_seconds(3605), 'over an hour')
        self.assertEqual(humanise_seconds(9000), '2 hours and 30 minutes')
        self.assertEqual(humanise_seconds(432232),
                         '5 days, 0 hours and 3 minutes')

    def test_impactLayerAttribution(self):
        """Test we get an attribution html snippet nicely for impact layers."""
        keywords = {'hazard_title': 'Sample Hazard Title',
                      'hazard_source': 'Sample Hazard Source',
                      'exposure_title': 'Sample Exposure Title',
                      'exposure_source': 'Sample Exposure Source'}
        myAttribution = impact_attribution(keywords)
        print myAttribution
        self.assertEqual(len(myAttribution.to_text()), 170)

    @expectedFailure
    def test_localisedAttribution(self):
        """Test we can localise attribution."""
        os.environ['LANG'] = 'id'
        keywords = {'hazard_title': 'Jakarta 2007 flood',
                      'hazard_source': 'Sample Hazard Source',
                      'exposure_title': 'People in Jakarta',
                      'exposure_source': 'Sample Exposure Source'}
        myHtml = impact_attribution(keywords, True)
        print myHtml
        assert myHtml == '11'

    def testDpiToMeters(self):
        """Test conversion from dpi to dpm."""
        myDpi = 300
        myDpm = dpi_to_meters(myDpi)
        myExpectedDpm = 11811.023622
        message = ('Conversion from dpi to dpm failed\n'
                     ' Got: %s Expected: %s\n' %
                     (myDpm, myExpectedDpm))
        self.assertAlmostEqual(myDpm, myExpectedDpm, msg=message)

    def testWhich(self):
        """Test that the which command works as expected."""
        myBinary = 'gdalwarp'
        path = which(myBinary)
        # Check we found at least one match
        assert len(path) > 0

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
