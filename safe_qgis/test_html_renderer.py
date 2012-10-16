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
__version__ = '0.5.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
import logging

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities_test import (getQgisTestApp,
                                      assertHashesForFile,
                                      loadLayer)
from safe_qgis.html_renderer import HtmlRenderer

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class HtmlRendererTest(unittest.TestCase):
    """Test the InaSAFE Html Renderer"""
    def setUp(self):
        pass

    def sampleHtml(self):
        """Helper function to generate some sample html."""
        myHtml = ('<table>'
                  '<thead>'
                  '<tr>'
                  '<th>Wilayah</th>'
                  '<th>Jumlah Penduduk</th>'
                  '<th>Jumlah Penduduk yang Mungkin</th>'
                  '<th>Wilayah</th>'
                  '<th>Jumlah Penduduk</th>'
                  '<th>Jumlah Penduduk yang Mungkin</th>'
                  '</tr>')
        i = 0
        while i < 100:
            i += 1
            myHtml += ('<tr>'
                       '<td>%(i)s</td><td>%(i)s</td><td>%(i)s</td>'
                       '<td>%(i)s</td><td>%(i)s</td><td>%(i)s</td>'
                       '</tr>') % {'i': i}
        myHtml += '</table>'
        return myHtml

    def test_printToPdf(self):
        """Test that we can render some html to a pdf (most common use case).
        """
        LOGGER.debug('InaSAFE HtmlRenderer testing printToPdf')
        myHtml = self.sampleHtml()
        myPageDpi = 300
        myRenderer = HtmlRenderer(myPageDpi)
        myPath = unique_filename(prefix='testHtmlTable',
                                 suffix='.pdf',
                                 dir=temp_dir('test'))
        LOGGER.debug(myPath)
        # If it fails myNewPath will come back as None
        myNewPath = myRenderer.printToPdf(myHtml, myPath)
        myMessage = 'Rendered output does not exist: %s' % myNewPath
        assert os.path.exists(myNewPath), myMessage
        # Also it should use our desired output file name
        myMessage = 'Incorrect path - got: %s\nExpected: %s\n' % (
            myNewPath, myPath)
        assert myNewPath == myPath, myMessage
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        mySize = os.stat(myNewPath).st_size
        myExpectedSize = 18449  # as rendered on linux ub 11.04-64
        myMessage = ('Expected rendered map pdf to be at least %s, got %s. '
                     'Please update myExpectedSize if the rendered output '
                     'is acceptible on your system.'
                     % (myExpectedSize, mySize))
        assert mySize >= myExpectedSize, myMessage

    def test_printImpactTable(self):
        """Test that we can render html from impact table keywords."""
        LOGGER.debug('InaSAFE HtmlRenderer testing printImpactTable')
        myFilename = 'test_floodimpact.tif'
        myLayer, _ = loadLayer(myFilename)
        myMessage = 'Layer is not valid: %s' % myFilename
        assert myLayer.isValid(), myMessage
        myPageDpi = 300
        myHtmlRenderer = HtmlRenderer(myPageDpi)
        myPath = unique_filename(prefix='impactTable',
                                 suffix='.pdf',
                                 dir=temp_dir('test'))
        myPath = myHtmlRenderer.printImpactTable(myLayer,
                                                 theFilename=myPath)
        myMessage = 'Rendered output does not exist: %s' % myPath
        assert os.path.exists(myPath), myMessage
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        mySize = os.stat(myPath).st_size
        myExpectedSize = 20936  # as rendered on linux ub 12.04 64
        myMessage = ('Expected rendered map pdf to be at least %s, got %s'
                     % (myExpectedSize, mySize))
        assert mySize >= myExpectedSize, myMessage

    def test_renderHtmlToPixmap(self):
        """Test that we can render html to a pixmap."""
        LOGGER.debug('InaSAFE HtmlRenderer testing renderHtmlToPixmap')
        myHtml = self.sampleHtml()
        LOGGER.debug(myHtml)
        myPageDpi = 300
        myRenderer = HtmlRenderer(myPageDpi)
        myPath = unique_filename(prefix='testHtmlToPixmap',
                                 suffix='.png',
                                 dir=temp_dir('test'))
        LOGGER.debug(myPath)
        myWidth = 250
        myPixmap = myRenderer.renderHtmlToPixmap(myHtml, myWidth)
        LOGGER.debug(myPixmap.__class__)
        myPixmap.save(myPath)
        myMessage = 'Rendered output does not exist: %s' % myPath
        assert os.path.exists(myPath), myMessage
        myExpectedHashes = ['1b4ef78f93581086af944340a7d1dacc',  # ub12.04-64
                            'aa110b049db7d6305b212543c2167383',  # ub12.04 xvfb
                            '8e626bda4310f174d40a076af65c6023',  # ub11.04-64
                            '869bb116ebebc1497ee9881eece0efc3',  # ub11.10-64
                            '',
                            ]
        assertHashesForFile(myExpectedHashes, myPath)

if __name__ == '__main__':
    suite = unittest.makeSuite(HtmlRendererTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
