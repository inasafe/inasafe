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
__version__ = '0.5.0'
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
                                      assertHashesForFile,
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
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            'd0c3071c4babe7db4f9762b311d61184',  # ub12.04xiner
                            'b94cfd8a10d709ff28466ada425f24c8',  # ub11.04-64
                            '00dc58aa50867de9b617ccfab0d13f21',  # ub12.04
                            'e65853e217a4c9b0c2f303dd2aadb373',  # ub12.04 xvfb
                            'e4273364b33a943e1108f519dbe8e06c',  # ub12.04-64
                            '91177a81bee4400be4e85789e3be1e91',  # binary read
                            '57da6f81b4a55507e1bed0b73423244b',  # wVistaSP2-32
                            '']
        assertHashesForFile(myExpectedHashes, myPath)
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
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        # Results currently identical to getLegend as image is same
        myExpectedHashes = ['',  # win
                            'd0c3071c4babe7db4f9762b311d61184',  # ub12.04 xinr
                            'b94cfd8a10d709ff28466ada425f24c8',  # ub11.04-64
                            '00dc58aa50867de9b617ccfab0d13f21',  # ub12.04
                            'e65853e217a4c9b0c2f303dd2aadb373',  # ub12.04 xvfb
                            'e4273364b33a943e1108f519dbe8e06c',  # ub12.04-64
                            # ub11.04-64 laptop
                            '91177a81bee4400be4e85789e3be1e91',  # Binary Read
                            '57da6f81b4a55507e1bed0b73423244b',  # wVistaSP2-32
                            '']
        assertHashesForFile(myExpectedHashes, myPath)

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
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            '9ead6ce0ac789adc65a6f00bd2d1f709',  # ub12.04xiner
                            '84bc3d518e3a0504f8dc36dfd620394e',  # ub11.04-64
                            'b68ccc328de852f0c66b8abe43eab3da',  # ub12.04
                            'cd5fb96f6c5926085d251400dd3b4928',  # ub12.04 xvfb
                            'a654d0dcb6b6d14b0a7a62cd979c16b9',  # ub12.04-64
                            # ub11.04-64 laptop
                            '9692ba8dbf909b8fe3ed27a8f4924b78',  # binary read
                            '5f4ef033bb1d6f36af4c08db55ca63be',  # wVistaSP2-32
                            '',
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

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
        myExpectedHashes = ['850ed7ad9e8f992e96c5449701ba5434',  # ub 12.04-64
                            '3d4d9f196fb2fe1e18d54a8d6ab4a349',
                            'e8ef2222f90fc2f95dc86f416de2579e',  # ub 11.04-64
                            '']
        assertHashesForFile(myExpectedHashes, myPath)

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
        # OS platforms cause different output, so hashes are a list
        # of 'known good' renders.
        myExpectedHashes = ['',  # win
                            '67c0f45792318298664dd02cc0ac94c3',  # ub12.04xiner
                            '53e0ba1144e071ad41756595d29bf444',  # ub12.04
                            '0681c3587305074bc9272f456fb4dd09',  # ub12.04 xvfb
                            'a37443d70604bdc8c279576b424a158c',  # ub12.04-64
                            # ub11.04-64 laptop
                            '944cee3eb9d916816b60ef41e8069683',  # binary read
                            'de3ceb6547ffc6c557d031c0b7ee9e75',  # wVistaSP2-32
                            '91177a81bee4400be4e85789e3be1e91',  # ub12.04-64
                            'e65853e217a4c9b0c2f303dd2aadb373',  # ub12.04 xvfb
                            'b94cfd8a10d709ff28466ada425f24c8',  # ub11.04-64
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

if __name__ == '__main__':
    suite = unittest.makeSuite(MapLegendTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
