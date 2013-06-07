import unittest
import sys
import os

from unittest import expectedFailure
from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe_qgis.utilities import (
    getErrorMessage,
    qgisVersion,
    mmToPoints,
    pointsToMM,
    humaniseSeconds,
    isPolygonLayer,
    getLayerAttributeNames,
    impactLayerAttribution,
    dpiToMeters,
    which)
from safe_qgis.utilities_test import (
    unitTestDataPath,
    loadLayer,
    getQgisTestApp)
from safe_qgis.exceptions import StyleError
from safe_qgis.test_keywords_dialog import (makePolygonLayer,
                                            makePadangLayer,
                                            makePointLayer)
from safe_qgis.utilities import getDefaults
from safe_qgis.safe_interface import BoundingBoxError, bbox_intersection

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class UtilitiesTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
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

            myMessage = getErrorMessage(e)
            #print myMessage
            myMessage = myMessage.to_text()
            self.assertIn(str(e), myMessage)
            self.assertIn('line', myMessage)
            self.assertIn('file', myMessage)

            myMessage = getErrorMessage(e)
            myMessage = myMessage.to_html()
            assert str(e) in myMessage
            self.assertIn('</i> Traceback</h5>', myMessage)
            self.assertIn('line', myMessage)
            self.assertIn('file', myMessage)
        # pylint: enable=W0703

    def test_getQgisVersion(self):
        """Test we can get the version of QGIS"""
        myVersion = qgisVersion()
        myMessage = 'Got version %s of QGIS, but at least 107000 is needed'
        assert myVersion > 10700, myMessage

    def test_getLayerAttributeNames(self):
        """Test we can get the correct attributes back"""
        myLayer = makePolygonLayer()

        #with good attribute name
        myAttrs, myPos = getLayerAttributeNames(myLayer, [
            QVariant.Int, QVariant.String],
            'TEST_STRIN')
        myExpectedAttrs = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        myExpectedPos = 2
        myMessage = 'myExpectedAttrs, got %s, expected %s' % (
            myAttrs, myExpectedAttrs)
        assert (myAttrs == myExpectedAttrs), myMessage
        myMessage = 'myExpectedPos, got %s, expected %s' % (
            myPos, myExpectedPos)
        assert (myPos == myExpectedPos), myMessage

        #with inexistent attribute name
        myAttrs, myPos = getLayerAttributeNames(
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
        myAttrs, myPos = getLayerAttributeNames(myLayer, [], '')
        myMessage = 'Should return None, None for raster layer, got %s, %s' % (
            myAttrs, myPos)
        assert (myAttrs is None and myPos is None), myMessage

    def test_isLayerPolygonal(self):
        """Test we can get the correct attributes back"""
        myLayer = makePolygonLayer()
        myMessage = 'isPolygonLayer, %s layer should be polygonal' % myLayer
        assert isPolygonLayer(myLayer), myMessage

        myLayer = makePointLayer()
        myMessage = '%s layer should be polygonal' % myLayer
        assert not isPolygonLayer(myLayer), myMessage

        myLayer = makePadangLayer()
        myMessage = ('%s raster layer should not be polygonal' % myLayer)
        assert not isPolygonLayer(myLayer), myMessage

    def test_getDefaults(self):
        myExpectedDefaults = {
            'FEM_RATIO_KEY': 'female ratio default',
            'YOUTH_RATIO': 0.263,
            'ELDER_RATIO': 0.078,
            'NO_DATA': 'No data',
            'FEM_RATIO': 0.5,
            'AGGR_ATTR_KEY': 'aggregation attribute',
            'FEM_RATIO_ATTR_KEY': 'female ratio attribute',
            'ADULT_RATIO': 0.659}
        myDefaults = getDefaults()
        myMessage = 'Defaults: got %s, expected %s' % (
            myDefaults, myExpectedDefaults)
        assert (myDefaults == myExpectedDefaults), myMessage

    def test_mmPointConversion(self):
        """Test that conversions between pixel and page dimensions work."""

        myDpi = 300
        myPixels = 300
        myMM = 25.4  # 1 inch
        myResult = pointsToMM(myPixels, myDpi)
        myMessage = "Expected: %s\nGot: %s" % (myMM, myResult)
        assert myResult == myMM, myMessage
        myResult = mmToPoints(myMM, myDpi)
        myMessage = "Expected: %s\nGot: %s" % (myPixels, myResult)
        assert myResult == myPixels, myMessage

    def test_humaniseSeconds(self):
        """Test that humanise seconds works."""
        self.assertEqual(humaniseSeconds(5), '5 seconds')
        self.assertEqual(humaniseSeconds(65), 'a minute')
        self.assertEqual(humaniseSeconds(3605), 'over an hour')
        self.assertEqual(humaniseSeconds(9000), '2 hours and 30 minutes')
        self.assertEqual(humaniseSeconds(432232),
                         '5 days, 0 hours and 3 minutes')

    def test_impactLayerAttribution(self):
        """Test we get an attribution html snippet nicely for impact layers."""
        myKeywords = {'hazard_title': 'Sample Hazard Title',
                      'hazard_source': 'Sample Hazard Source',
                      'exposure_title': 'Sample Exposure Title',
                      'exposure_source': 'Sample Exposure Source'}
        myAttribution = impactLayerAttribution(myKeywords)
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
        myHtml = impactLayerAttribution(myKeywords, True)
        print myHtml
        assert myHtml == '11'

    def testDpiToMeters(self):
        """Test conversion from dpi to dpm."""
        myDpi = 300
        myDpm = dpiToMeters(myDpi)
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
