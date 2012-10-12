"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import logging

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities_test import (getQgisTestApp,
                                      assertHashForFile,
                                      loadLayer)
from safe_qgis.map import HtmlRenderer

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')

class HtmlRendererTest(unittest.TestCase):
    """Test the InaSAFE Html Renderer"""
    def setUp(self):
        pass

    def test_htmlToPrinter(self):
        """Test that we can render some html to a printer."""
        myHtml = ('<table>'
                  '<thead>'
                  '<tr>'
                  '<th rowspan="2">Wilayah</th>'
                  '<th colspan="2">Jumlah Penduduk</th>'
                  '<th rospan="2" colspan="2">Jumlah Penduduk yang Mungkin</th>'
                  '</tr>')
        i = 100
        while i < 100:
            i += 1
            myHtml+=('<tr>'
                     '<td></td><td></td><td></td><td></td><td></td><td></td>'
                     '</tr>')
        myHtml += '</table>'
        myPageDpi = 300
        myRenderer = HtmlRenderer(myPageDpi)
        myPath = unique_filename(prefix='impactTable',
                                 suffix='.pdf',
                                 dir=temp_dir('test'))
        LOGGER.debug(myPath)
        myRenderer.htmlToPrinter(myHtml, myPath)

    def Xtest_renderTable(self):
        """Test that html renders nicely. Commented out for now until we work
    out how to get webkit to do offscreen rendering nicely."""
        myFilename = 'test_floodimpact.tif'
        myLayer, myType = loadLayer(myFilename)
        CANVAS.refresh()
        del myType
        myMessage = 'Layer is not valid: %s' % myFilename
        assert myLayer.isValid(), myMessage
        myMap = Map(IFACE)
        myMap.setImpactLayer(myLayer)
        myPixmap = myMap.renderImpactTable()
        assert myPixmap is not None
        myExpectedWidth = 500
        myExpectedHeight = 300
        myMessage = 'Invalid width - got %s expected %s' % (
            myPixmap.width(),
            myExpectedWidth)
        assert myPixmap.width() == myExpectedWidth, myMessage
        myMessage = 'Invalid height - got %s expected %s' % (
            myPixmap.height(),
            myExpectedHeight)
        assert myPixmap.height() == myExpectedHeight
        myPath = unique_filename(prefix='impactTable',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        myPixmap.save(myPath, 'PNG')
        LOGGER.debug(myPath)
        myExpectedHash = 'c9164d5c2bb85c6081905456ab827f3e'
        assertHashForFile(myExpectedHash, myPath)

if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
