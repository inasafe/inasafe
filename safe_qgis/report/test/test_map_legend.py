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
from qgis.core import QgsMapLayerRegistry, QgsFillSymbolV2
from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    check_images,
    load_layer)
from safe_qgis.report.map import MapLegend

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class MapLegendTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        # noinspection PyArgumentList
        myRegistry = QgsMapLayerRegistry.instance()
        for myLayer in myRegistry.mapLayers():
            myRegistry.removeMapLayer(myLayer)

    def test_getLegend(self):
        """Getting a legend for a generic layer works."""
        LOGGER.debug('test_getLegend called')
        myLayer, _ = load_layer('test_shakeimpact.shp')
        myMapLegend = MapLegend(myLayer)
        assert myMapLegend.layer is not None
        myLegend = myMapLegend.get_legend()
        myPath = unique_filename(
            prefix='getLegend',
            suffix='.png',
            dir=temp_dir('test'))
        myLegend.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        myTolerance = 0  # to allow for version number changes in disclaimer

        myFlag, myMessage = check_images('getLegend', myPath, myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                      'copy the test image generated to create a new control '
                      'image.')
        assert myFlag, myMessage
        LOGGER.debug('test_getLegend done')

    def test_getVectorLegend(self):
        """Getting a legend for a vector layer works.
        @note This test is not related do thousand separator since we insert
        our own legend notes and our own layer.
        """
        myLayer, _ = load_layer('test_shakeimpact.shp')
        myMapLegend = MapLegend(
            myLayer,
            legend_notes='Thousand separator represented by \',\'',
            legend_units='(people per cell)')
        myImage = myMapLegend.vector_legend()
        myPath = unique_filename(
            prefix='getVectorLegend',
            suffix='.png',
            dir=temp_dir('test'))
        myImage.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = check_images(
            'getVectorLegend', myPath, myTolerance)
        myMessage += ('\nWe want these images to match, if they do already '
                      'copy the test image generated to create a new control '
                      'image.')
        assert myFlag, myMessage

    def test_getRasterLegend(self):
        """Getting a legend for a raster layer works."""
        myLayer, _ = load_layer('test_floodimpact.tif')
        myMapLegend = MapLegend(myLayer)
        myImage = myMapLegend.raster_legend()
        myPath = unique_filename(
            prefix='getRasterLegend',
            suffix='.png',
            dir=temp_dir('test'))
        myImage.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = check_images(
            'getRasterLegend', myPath, myTolerance)
        myMessage += (
            '\nWe want these images to match, if they do already copy the test'
            ' image generated to create a new control image.')
        assert myFlag, myMessage

    def test_addSymbolToLegend(self):
        """Test we can add a symbol to the legend."""
        myLayer, _ = load_layer('test_floodimpact.tif')
        myMapLegend = MapLegend(myLayer)
        mySymbol = QgsFillSymbolV2()
        mySymbol.setColor(QtGui.QColor(12, 34, 56))
        myMapLegend.add_symbol(
            mySymbol,
            minimum=0,
            # expect 2.0303 in legend
            maximum=2.02030,
            label='Foo')
        myPath = unique_filename(
            prefix='addSymbolToLegend',
            suffix='.png',
            dir=temp_dir('test'))
        myMapLegend.get_legend().save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = check_images(
            'addSymbolToLegend', myPath, myTolerance)
        myMessage += (
            '\nWe want these images to match, if they do already, copy the '
            'test image generated to create a new control image.')
        assert myFlag, myMessage

    def test_addClassToLegend(self):
        """Test we can add a class to the map legend."""
        myLayer, _ = load_layer('test_shakeimpact.shp')
        myMapLegend = MapLegend(myLayer)
        myColour = QtGui.QColor(12, 34, 126)
        myMapLegend.add_class(
            myColour,
            label='bar')
        myMapLegend.add_class(
            myColour,
            label='foo')
        myPath = unique_filename(
            prefix='addClassToLegend',
            suffix='.png',
            dir=temp_dir('test'))
        myMapLegend.get_legend().save(myPath, 'PNG')
        LOGGER.debug(myPath)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so place any other possible
        # variants in the safe_qgis/test_data/test_images/ dir e.g.
        # addClassToLegend-variantUbuntu13.04.png
        myTolerance = 0  # to allow for version number changes in disclaimer
        myFlag, myMessage = check_images(
            'addClassToLegend', myPath, myTolerance)
        myMessage += (
            '\nWe want these images to match, if they do already copy the test'
            ' image generated to create a new control image.')
        assert myFlag, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(MapLegendTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
