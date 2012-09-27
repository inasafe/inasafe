import unittest
import sys
import os

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe.api import bbox_intersection
from safe_qgis.utilities import (getExceptionWithStacktrace,
                              setVectorStyle,
                              setRasterStyle,
                              qgisVersion)
from safe_qgis.utilities_test import unitTestDataPath
from safe_qgis.utilities_test import (loadLayer, getQgisTestApp)
from safe_qgis.exceptions import StyleError
from safe.common.exceptions import BoundingBoxError

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class UtilitiesTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        pass

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
        myLayer, myType = loadLayer('issue126.tif')
        del myType
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
        myValue1 = myLayer.rasterTransparency().alphaValue(1.1)
        myValue2 = myLayer.rasterTransparency().alphaValue(1.4)
        myMessage = ('Transparency should be ignored when style class'
                     ' quantities are floats')
        assert myValue1 == myValue2 == 255, myMessage

        # Now run the same test again
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

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
