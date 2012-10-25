import unittest
import sys
import os

from unittest import expectedFailure
from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe.api import bbox_intersection
from safe_qgis.utilities import (getExceptionWithStacktrace,
                              setVectorStyle,
                              setRasterStyle,
                              qgisVersion,
                              mmToPoints,
                              pointsToMM,
                              humaniseSeconds,
                              isLayerPolygonal,
                              getLayerAttributeNames,
                              impactLayerAttribution,
                              dpiToMeters)
from safe_qgis.utilities_test import (unitTestDataPath,
                                     loadLayer,
                                     getQgisTestApp)
from safe_qgis.exceptions import StyleError
from safe.common.exceptions import BoundingBoxError
from safe_qgis.test_keywords_dialog import (makePolygonLayer,
                                            makePadangLayer,
                                            makePointLayer)
from safe_qgis.utilities import getDefaults

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

            myMessage = getExceptionWithStacktrace(e, html=False)
            #print myMessage
            assert str(e) in myMessage
            assert 'line' in myMessage
            assert 'File' in myMessage

            myMessage = getExceptionWithStacktrace(e, html=True)
            assert str(e) in myMessage
            assert '<pre id="traceback"' in myMessage
            assert 'line' in myMessage
            assert 'File' in myMessage
        # pylint: enable=W0703

    def test_issue126(self):
        """Test that non integer transparency ranges fail gracefully.
        .. seealso:: https://github.com/AIFDR/inasafe/issues/126
        """
        # This dataset has all cells with value 1.3
        myLayer, _ = loadLayer('issue126.tif')

        # Note the float quantity values below
        myStyleInfo = {}
        myStyleInfo['style_classes'] = [
                        dict(colour='#38A800', quantity=1.1, transparency=100),
                        dict(colour='#38A800', quantity=1.4, transparency=0),
                        dict(colour='#79C900', quantity=10.1, transparency=0)]
        myMessage = ('Setting style info with float based ranges should fail '
                    'gracefully.')
        try:
            setRasterStyle(myLayer, myStyleInfo)
        except:
            raise Exception(myMessage)
        # Now validate the transparency values were set to 255 because
        # they are floats and we cant specify pixel ranges to floats
        # Note we don't test on the exact interval because 464c6171dd55
        myValue1 = myLayer.rasterTransparency().alphaValue(1.2)
        myValue2 = myLayer.rasterTransparency().alphaValue(1.5)
        myMessage = ('Transparency should be ignored when style class'
                     ' quantities are floats')
        assert myValue1 == myValue2 == 255, myMessage

        # Now run the same test again for int intervals
        myStyleInfo['style_classes'] = [
                        dict(colour='#38A800', quantity=2, transparency=100),
                        dict(colour='#38A800', quantity=4, transparency=0),
                        dict(colour='#79C900', quantity=10, transparency=0)]
        myMessage = ('Setting style info with generate valid transparent '
                     'pixel entries.')
        try:
            setRasterStyle(myLayer, myStyleInfo)
        except:
            raise Exception(myMessage)
        # Now validate the transparency values were set to 255 because
        # they are floats and we cant specify pixel ranges to floats
        myValue1 = myLayer.rasterTransparency().alphaValue(1)
        myValue2 = myLayer.rasterTransparency().alphaValue(3)
        myMessage1 = myMessage + 'Expected 0 got %i' % myValue1
        myMessage2 = myMessage + 'Expected 255 got %i' % myValue2
        assert myValue1 == 0, myMessage1
        assert myValue2 == 255, myMessage2

        # Verify that setRasterStyle doesn't break when floats coincide with
        # integers
        # See https://github.com/AIFDR/inasafe/issues/126#issuecomment-5978416
        myStyleInfo['style_classes'] = [
                        dict(colour='#38A800', quantity=2.0, transparency=100),
                        dict(colour='#38A800', quantity=4.0, transparency=0),
                        dict(colour='#79C900', quantity=10.0, transparency=0)]
        myMessage = ('Broken: Setting style info with generate valid '
                     'transparent '
                     'floating point pixel entries such as 2.0, 3.0')
        try:
            setRasterStyle(myLayer, myStyleInfo)
        except Exception, e:
            raise Exception(myMessage + ': ' + str(e))

    def test_transparency_of_minimum_value(self):
        """Test that transparency of minimum value works when set to 100%
        """
        # This dataset has all cells with value 1.3
        myLayer, _ = loadLayer('issue126.tif')

        # Note the float quantity values below
        myStyleInfo = {}
        myStyleInfo['style_classes'] = [
            {'colour': '#FFFFFF', 'transparency': 100, 'quantity': 0.0},
            {'colour': '#38A800', 'quantity': 0.038362596547925065,
             'transparency': 0, 'label': u'Rendah [0 orang/sel]'},
            {'colour': '#79C900', 'transparency': 0,
             'quantity': 0.07672519309585013},
            {'colour': '#CEED00', 'transparency': 0,
             'quantity': 0.1150877896437752},
            {'colour': '#FFCC00', 'quantity': 0.15345038619170026,
             'transparency': 0, 'label': u'Sedang [0 orang/sel]'},
            {'colour': '#FF6600', 'transparency': 0,
             'quantity': 0.19181298273962533},
            {'colour': '#FF0000', 'transparency': 0,
             'quantity': 0.23017557928755039},
            {'colour': '#7A0000', 'quantity': 0.26853817583547546,
             'transparency': 0, 'label': u'Tinggi [0 orang/sel]'}]

        myMessage = 'Could not create raster style'
        try:
            setRasterStyle(myLayer, myStyleInfo)
        except:
            raise Exception(myMessage)

        myMessage = ('Should get a single transparency class for first style '
                     'class')
        myTransparencyList = (myLayer.rasterTransparency().
                transparentSingleValuePixelList())

        self.assertEqual(len(myTransparencyList), 1)

    def test_issue121(self):
        """Test that point symbol size can be set from style (issue 121).
        .. seealso:: https://github.com/AIFDR/inasafe/issues/121
        """
        myLayer, myType = loadLayer('kecamatan_jakarta_osm_centroids.shp')
        del myType
        # Note the float quantity values below
        myStyleInfo = {'target_field': 'KEPADATAN',
                       'style_classes':
                           [{'opacity': 1, 'max': 200, 'colour': '#fecc5c',
                             'min': 45, 'label': 'Low', 'size': 1},
                            {'opacity': 1, 'max': 350, 'colour': '#fd8d3c',
                             'min': 201, 'label': 'Medium', 'size': 2},
                            {'opacity': 1, 'max': 539, 'colour': '#f31a1c',
                             'min': 351, 'label': 'High', 'size': 3}]}
        myMessage = ('Setting style with point sizes should work.')
        try:
            setVectorStyle(myLayer, myStyleInfo)
        except:
            raise Exception(myMessage)
        # Now validate the size values were set as expected

        if myLayer.isUsingRendererV2():
            # new symbology - subclass of QgsFeatureRendererV2 class
            myRenderer = myLayer.rendererV2()
            myType = myRenderer.type()
            assert myType == 'graduatedSymbol'
            mySize = 1
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol()
                mySymbolLayer = mySymbol.symbolLayer(0)
                myActualSize = mySymbolLayer.size()
                myMessage = (('Expected symbol layer 0 for range %s to have'
                             ' a size of %s, got %s') %
                             (mySize, mySize, myActualSize))
                assert mySize == myActualSize, myMessage
                mySize += 1

    def test_issue157(self):
        """Verify that we get the error class name back - issue #157
           .. seealso:: https://github.com/AIFDR/inasafe/issues/121
        """
        try:
            bbox_intersection('aoeu', 'oaeu', [])
        except BoundingBoxError, e:
            myMessage = getExceptionWithStacktrace(e, html=False)
            assert 'BoundingBoxError : Western' in myMessage, myMessage

    def test_issue230(self):
        """Verify that we give informative errors when style is not correct
           .. seealso:: https://github.com/AIFDR/inasafe/issues/230
        """
        myPath = unitTestDataPath('impact')
        myVectorLayer, myType = loadLayer('polygons_for_styling.shp', myPath)
        del myType
        myStyle = {'legend_title': u'Population Count',
                   'target_field': 'population',
                   'style_classes':
                   [{'transparency': 0,
                     'min': [0],  # <-- intentionally broken list not number!
                     'max': 139904.08186340332,
                     'colour': '#FFFFFF',
                     'size': 1,
                     'label': u'Nil'},
                    {'transparency': 0,
                     'min': 139904.08186340332,
                     'max': 279808.16372680664,
                     'colour': '#38A800',
                     'size': 1,
                     'label': u'Low'},
                    {'transparency': 0,
                     'min': 279808.16372680664,
                     'max': 419712.24559020996,
                     'colour': '#79C900',
                     'size': 1,
                     'label': u'Low'},
                    {'transparency': 0,
                     'min': 419712.24559020996,
                     'max': 559616.32745361328,
                     'colour': '#CEED00',
                     'size': 1,
                     'label': u'Low'},
                    {'transparency': 0,
                     'min': 559616.32745361328,
                     'max': 699520.4093170166,
                     'colour': '#FFCC00',
                     'size': 1,
                     'label': u'Medium'},
                    {'transparency': 0,
                     'min': 699520.4093170166,
                     'max': 839424.49118041992,
                     'colour': '#FF6600',
                     'size': 1,
                     'label': u'Medium'},
                    {'transparency': 0,
                     'min': 839424.49118041992,
                     'max': 979328.57304382324,
                     'colour': '#FF0000',
                     'size': 1,
                     'label': u'Medium'},
                    {'transparency': 0,
                     'min': 979328.57304382324,
                     'max': 1119232.6549072266,
                     'colour': '#7A0000',
                     'size': 1,
                     'label': u'High'}]}
        try:
            setVectorStyle(myVectorLayer, myStyle)
        except StyleError:
            # Exactly what should have happened
            return
        except Exception, e:
            print str(e)
        assert False, 'Incorrect handling of broken styles'

    def test_getQgisVersion(self):
        """Test we can get the version of QGIS"""
        myVersion = qgisVersion()
        myMessage = 'Got version %s of QGIS, but at least 107000 is needed'
        assert myVersion > 10700, myMessage

    def test_getLayerAttributeNames(self):
        """Test we can get the correct attributes back"""
        myLayer = makePolygonLayer()

        #with good attribute name
        myAttrs, myPos = getLayerAttributeNames(myLayer,
            [QVariant.Int, QVariant.String],
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
        myAttrs, myPos = getLayerAttributeNames(myLayer,
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
        myMessage = 'isLayerPolygonal, %s layer should be polygonal' % myLayer
        assert isLayerPolygonal(myLayer), myMessage

        myLayer = makePointLayer()
        myMessage = '%s layer should be polygonal' % myLayer
        assert not isLayerPolygonal(myLayer), myMessage

        myLayer = makePadangLayer()
        myMessage = ('%s raster layer should not be polygonal'
                    % myLayer)
        assert not isLayerPolygonal(myLayer), myMessage

    def test_getDefaults(self):
        myExpectedDefaults = {
            'FEM_RATIO_KEY': 'female ratio default',
            'YOUTH_RATIO': 0.263,
            'ELDER_RATIO': 0.078,
            'NO_DATA': 'No data',
            'FEM_RATIO': 0.5,
            'AGGR_ATTR_KEY': 'aggregation attribute',
            'FEM_RATIO_ATTR_KEY': 'female ratio attribute',
            'ADULT_RATIO': 0.659
        }
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
        myHtml = impactLayerAttribution(myKeywords)
        print myHtml
        self.assertEqual(len(myHtml), 288)

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

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
