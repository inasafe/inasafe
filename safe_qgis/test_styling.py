import unittest
import sys
import os

from unittest import expectedFailure
from PyQt4.QtCore import QVariant

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe_qgis.styling import (
    setVectorGraduatedStyle,
    setRasterStyle,
    _addMinMaxToStyle)
from safe_qgis.utilities import getErrorMessage
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


class StylingTest(unittest.TestCase):
    """Tests for qgis styling related functions.
    """

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_issue126(self):
        """Test that non integer transparency ranges fail gracefully.
        .. seealso:: https://github.com/AIFDR/inasafe/issues/126
        """
        # This dataset has all cells with value 1.3
        myLayer, _ = loadLayer('issue126.tif')

        # Note the float quantity values below
        myStyleInfo = {'style_classes': [
            dict(colour='#38A800', quantity=1.1, transparency=100),
            dict(colour='#38A800', quantity=1.4, transparency=0),
            dict(colour='#79C900', quantity=10.1, transparency=0)]}

        try:
            setRasterStyle(myLayer, myStyleInfo)
        except Exception, e:
            myMessage = (
                'Setting style info with float based ranges should fail '
                'gracefully.')
            e.args = (e.args[0] + myMessage,)
            raise
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

        try:
            setRasterStyle(myLayer, myStyleInfo)
        except Exception, e:
            myMessage = (
                'Broken: Setting style info with generate valid transparent '
                'floating point pixel entries such as 2.0, 3.0')
            e.args = (e.args[0] + myMessage,)
            raise

    def test_transparency_of_minimum_value(self):
        """Test that transparency of minimum value works when set to 100%
        """
        # This dataset has all cells with value 1.3
        myLayer, _ = loadLayer('issue126.tif')

        # Note the float quantity values below
        myStyleInfo = {'style_classes': [
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
             'transparency': 0, 'label': u'Tinggi [0 orang/sel]'}]}

        try:
            setRasterStyle(myLayer, myStyleInfo)
        except Exception, e:
            myMessage = '\nCould not create raster style'
            e.args = (e.args[0] + myMessage,)
            raise

        #myMessage = ('Should get a single transparency class for first style '
        #             'class')
        myTransparencyList = (
            myLayer.rasterTransparency().
            transparentSingleValuePixelList())

        self.assertEqual(len(myTransparencyList), 2)

    def test_issue121(self):
        """Test that point symbol size can be set from style (issue 121).
        .. seealso:: https://github.com/AIFDR/inasafe/issues/121
        """
        myLayer, myType = loadLayer('kecamatan_jakarta_osm_centroids.shp')
        del myType
        # Note the float quantity values below
        myStyleInfo = {'target_field': 'KEPADATAN', 'style_classes': [
            {'opacity': 1, 'max': 200, 'colour': '#fecc5c',
             'min': 45, 'label': 'Low', 'size': 1},
            {'opacity': 1, 'max': 350, 'colour': '#fd8d3c',
             'min': 201, 'label': 'Medium', 'size': 2},
            {'opacity': 1, 'max': 539, 'colour': '#f31a1c',
             'min': 351, 'label': 'High', 'size': 3}]}
        myMessage = 'Setting style with point sizes should work.'
        try:
            setVectorGraduatedStyle(myLayer, myStyleInfo)
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
            myMessage = getErrorMessage(e)
            myString = 'BoundingBoxError'
            assert myString in myMessage.to_text(), myMessage
            myString = 'Western boundary'
            assert myString in myMessage.to_text(), myMessage

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
            setVectorGraduatedStyle(myVectorLayer, myStyle)
        except StyleError:
            # Exactly what should have happened
            return
        except Exception, e:
            print str(e)
        assert False, 'Incorrect handling of broken styles'

    def testAddMinMaxToStyle(self):
        """Test our add min max to style function."""
        myClasses = [dict(colour='#38A800', quantity=2, transparency=0),
                     dict(colour='#38A800', quantity=5, transparency=50),
                     dict(colour='#79C900', quantity=10, transparency=50),
                     dict(colour='#CEED00', quantity=20, transparency=50),
                     dict(colour='#FFCC00', quantity=50, transparency=34),
                     dict(colour='#FF6600', quantity=100, transparency=77),
                     dict(colour='#FF0000', quantity=200, transparency=24),
                     dict(colour='#7A0000', quantity=300, transparency=22)]
        myExpectedClasses = [
            {'max': 2.0, 'colour': '#38A800', 'min': 0.0, 'transparency': 0,
             'quantity': 2},
            {'max': 5.0, 'colour': '#38A800', 'min': 2.0000000000000004,
             'transparency': 50, 'quantity': 5},
            {'max': 10.0, 'colour': '#79C900', 'min': 5.0000000000000009,
             'transparency': 50, 'quantity': 10},
            {'max': 20.0, 'colour': '#CEED00', 'min': 10.000000000000002,
             'transparency': 50, 'quantity': 20},
            {'max': 50.0, 'colour': '#FFCC00', 'min': 20.000000000000004,
             'transparency': 34, 'quantity': 50},
            {'max': 100.0, 'colour': '#FF6600', 'min': 50.000000000000007,
             'transparency': 77, 'quantity': 100},
            {'max': 200.0, 'colour': '#FF0000', 'min': 100.00000000000001,
             'transparency': 24, 'quantity': 200},
            {'max': 300.0, 'colour': '#7A0000', 'min': 200.00000000000003,
             'transparency': 22, 'quantity': 300}]

        myActualClasses = _addMinMaxToStyle(myClasses)
        print myActualClasses
        self.maxDiff = None
        self.assertListEqual(myExpectedClasses, myActualClasses)



if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
