"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Map  Legend test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__date__ = '12/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import logging

# Add PARENT directory to path to make test aware of other modules
#pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(pardir)

from PyQt4 import QtGui
from qgis.core import (QgsSymbol,
                       QgsMapLayerRegistry)
from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities_test import (getQgisTestApp,
                                      checkImages,
                                      loadLayer)
from safe_qgis.map import MapLegend

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class MapLegendTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        myRegistry = QgsMapLayerRegistry.instance()
        for myLayer in myRegistry.mapLayers():
            myRegistry.removeMapLayer(myLayer)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        LOGGER.debug('test_getLegend called')
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myMapLegend = MapLegend(myLayer)
        assert myMapLegend.layer is not None
        myLegend = myMapLegend.getLegend()
        myPath = unique_filename(prefix='getLegend',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myLegend.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        myControlImages = ['getLegend.png',
                           'getLegend-variantWindosVistaSP2-32.png',
                           'getClassToLegend-variantUB12.04-64.png',
                           'getLegend-variantJenkins.png']
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = checkImages(myControlImages,
                                        myPath,
                                        myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
            'copy the test image generated to create a new control image.')
        assert myFlag, myMessage
        LOGGER.debug('test_getLegend done')

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works."""
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myMapLegend = MapLegend(myLayer)
        myImage = myMapLegend.getVectorLegend()
        myPath = unique_filename(prefix='getVectorLegend',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myImage.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        myControlImages = ['getVectorLegend.png',
                           'getVectorLegend-variantWindosVistaSP2-32.png',
                           'getVectorLegend-variantUB12.04-64.png',
                           'getVectorLegend-variantJenkins.png']
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = checkImages(myControlImages,
                                    myPath,
                                    myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                'copy the test image generated to create a new control image.')
        assert myFlag, myMessage

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, _ = loadLayer('test_floodimpact.tif')
        myMapLegend = MapLegend(myLayer)
        myImage = myMapLegend.getRasterLegend()
        myPath = unique_filename(prefix='getRasterLegend',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myImage.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        myControlImages = ['getRasterLegend.png',
                           'getRasterLegend-variantWindosVistaSP2-32.png',
                           'getRasterLegend-variantUB12.04-64.png',
                           'getRasterLegend-variantJenkins.png']
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = checkImages(myControlImages,
                                        myPath,
                                        myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                'copy the test image generated to create a new control image.')
        assert myFlag, myMessage

    def test_addSymbolToLegend(self):
        """Test we can add a symbol to the legend."""
        myLayer, _ = loadLayer('test_floodimpact.tif')
        myMapLegend = MapLegend(myLayer)
        mySymbol = QgsSymbol()
        mySymbol.setColor(QtGui.QColor(12, 34, 56))
        myMapLegend.addSymbolToLegend(mySymbol,
                                theMin=0,
                                theMax=2,
                                theCategory=None,
                                theLabel='Foo')
        myPath = unique_filename(prefix='addSymblToLegend',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myMapLegend.getLegend().save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        myControlImages = ['addSymbolToLegend.png',
                           'addSymbolToLegend-variantWindosVistaSP2-32.png',
                           'addSymbolToLegend-variantUB12.04-64.png',
                           'addSymbolToLegend-variantJenkins.png']
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = checkImages(myControlImages,
                                        myPath,
                                        myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                'copy the test image generated to create a new control image.')
        assert myFlag, myMessage

    def test_addClassToLegend(self):
        """Test we can add a class to the map legend."""
        myLayer, _ = loadLayer('test_shakeimpact.shp')
        myMapLegend = MapLegend(myLayer)
        myColour = QtGui.QColor(12, 34, 126)
        myMapLegend.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory=None,
                               theLabel='bar')
        myMapLegend.addClassToLegend(myColour,
                               theMin=None,
                               theMax=None,
                               theCategory=None,
                               theLabel='foo')
        myPath = unique_filename(prefix='addClassToLegend',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myMapLegend.getLegend().save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        myControlImages = ['getClassToLegend.png',
                           'getClassToLegend-variantWindosVistaSP2-32.png',
                           'getClassToLegend-variantUB12.04-64.png',
                           'getClassToLegend-variantJenkins.png']
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = checkImages(myControlImages,
                                        myPath,
                                        myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                'copy the test image generated to create a new control image.')
        assert myFlag, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(MapLegendTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
