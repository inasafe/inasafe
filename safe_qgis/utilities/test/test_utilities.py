import unittest
import sys
import os

from unittest import expectedFailure

# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

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
    breakdown_defaults)
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app, TEST_FILES_DIR)
from safe_qgis.tools.test.test_keywords_dialog import (
    makePolygonLayer,
    makePadangLayer,
    makePointLayer)
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

    def test_stacktrace_html(self):
        """Stack traces can be caught and rendered as html
        """

        # This is about general exception handling, so ok to use catch-all
        # pylint: disable=W0703
        try:
            bbox_intersection('aoeu', 'oaeu', [])
        except Exception, e:
            # Display message and traceback

            myMessage = get_error_message(e)
            #print myMessage
            myMessage = myMessage.to_text()
            self.assertIn(str(e), myMessage)
            self.assertIn('line', myMessage)
            self.assertIn('file', myMessage)

            myMessage = get_error_message(e)
            myMessage = myMessage.to_html()
            assert str(e) in myMessage

            myMessage = myMessage.decode('string_escape')
            myExpectedResult = open(
                TEST_FILES_DIR +
                '/test-stacktrace-html.txt', 'r').read().replace('\n', '')
            self.assertIn(myExpectedResult, myMessage)

        # pylint: enable=W0703

    def test_getQgisVersion(self):
        """Test we can get the version of QGIS"""
        myVersion = qgis_version()
        myMessage = 'Got version %s of QGIS, but at least 107000 is needed'
        assert myVersion > 10700, myMessage

    def test_getLayerAttributeNames(self):
        """Test we can get the correct attributes back"""
        myLayer = makePolygonLayer()

        #with good attribute name
        myAttrs, myPos = layer_attribute_names(myLayer, [
            QVariant.Int, QVariant.String],
            'TEST_STRIN')  # Not a typo...
        myExpectedAttrs = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        myExpectedPos = 2
        myMessage = 'myExpectedAttrs, got %s, expected %s' % (
            myAttrs, myExpectedAttrs)
        assert (myAttrs == myExpectedAttrs), myMessage
        myMessage = 'myExpectedPos, got %s, expected %s' % (
            myPos, myExpectedPos)
        assert (myPos == myExpectedPos), myMessage

        #with inexistent attribute name
        myAttrs, myPos = layer_attribute_names(
            myLayer,
            [QVariant.Int, QVariant.String],
            'MISSING_ATTR')
        myExpectedAttrs = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        myExpectedPos = None
        myMessage = 'myExpectedAttrs, got %s, expected %s' % (
            myAttrs, myExpectedAttrs)
        assert (myAttrs == myExpectedAttrs), myMessage
        myMessage = 'myExpectedPos, got %s, expected %s' % (
            myPos, myExpectedPos)
        assert (myPos == myExpectedPos), myMessage

        #with raster layer
        myLayer = makePadangLayer()
        myAttrs, myPos = layer_attribute_names(myLayer, [], '')
        myMessage = 'Should return None, None for raster layer, got %s, %s' % (
            myAttrs, myPos)
        assert (myAttrs is None and myPos is None), myMessage

    def test_isLayerPolygonal(self):
        """Test we can get the correct attributes back"""
        myLayer = makePolygonLayer()
        myMessage = 'isPolygonLayer, %s layer should be polygonal' % myLayer
        assert is_polygon_layer(myLayer), myMessage

        myLayer = makePointLayer()
        myMessage = '%s layer should be polygonal' % myLayer
        assert not is_polygon_layer(myLayer), myMessage

        myLayer = makePadangLayer()
        myMessage = ('%s raster layer should not be polygonal' % myLayer)
        assert not is_polygon_layer(myLayer), myMessage

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
        myMessage = 'Defaults: got %s, expected %s' % (
            myDefaults, myExpectedDefaults)
        assert (myDefaults == myExpectedDefaults), myMessage

    def test_mmPointConversion(self):
        """Test that conversions between pixel and page dimensions work."""

        myDpi = 300
        myPixels = 300
        myMM = 25.4  # 1 inch
        myResult = points_to_mm(myPixels, myDpi)
        myMessage = "Expected: %s\nGot: %s" % (myMM, myResult)
        assert myResult == myMM, myMessage
        myResult = mm_to_points(myMM, myDpi)
        myMessage = "Expected: %s\nGot: %s" % (myPixels, myResult)
        assert myResult == myPixels, myMessage

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
        myKeywords = {'hazard_title': 'Sample Hazard Title',
                      'hazard_source': 'Sample Hazard Source',
                      'exposure_title': 'Sample Exposure Title',
                      'exposure_source': 'Sample Exposure Source'}
        myAttribution = impact_attribution(myKeywords)
        print myAttribution
        self.assertEqual(len(myAttribution.to_text()), 170)

    @expectedFailure
    def test_localisedAttribution(self):
        """Test we can localise attribution."""
        os.environ['LANG'] = 'id'
        myKeywords = {'hazard_title': 'Jakarta 2007 flood',
                      'hazard_source': 'Sample Hazard Source',
                      'exposure_title': 'People in Jakarta',
                      'exposure_source': 'Sample Exposure Source'}
        myHtml = impact_attribution(myKeywords, True)
        print myHtml
        assert myHtml == '11'

    def testDpiToMeters(self):
        """Test conversion from dpi to dpm."""
        myDpi = 300
        myDpm = dpi_to_meters(myDpi)
        myExpectedDpm = 11811.023622
        myMessage = ('Conversion from dpi to dpm failed\n'
                     ' Got: %s Expected: %s\n' %
                     (myDpm, myExpectedDpm))
        self.assertAlmostEqual(myDpm, myExpectedDpm, msg=myMessage)

    def testWhich(self):
        """Test that the which command works as expected."""
        myBinary = 'gdalwarp'
        myPath = which(myBinary)
        # Check we found at least one match
        assert len(myPath) > 0

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
