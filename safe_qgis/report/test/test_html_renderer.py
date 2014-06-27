# coding=utf-8
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
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import os
import unittest
import logging

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities.utilities_for_testing import (
    load_layer, check_images)
from safe_qgis.report.html_renderer import HtmlRenderer
from safe_qgis.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger('InaSAFE')


class HtmlRendererTest(unittest.TestCase):
    """Test the InaSAFE Html Renderer"""
    def setUp(self):
        """Runs before each test."""
        pass

    def sample_html(self, line_count=100):
        """Helper function to generate some sample html.

        :param line_count: How many lines of fake html you want.
            Default is 100.
        :type line_count: int

        :returns: Html snippet containing a table with line_count rows.
        :type: str
        """
        html = (
            '<table class="table table-striped condensed'
            ' bordered-table">'
            '<thead>'
            '<tr>'
            '<th>Wilayah</th>'
            '<th>Jumlah Penduduk</th>'
            '<th>Jumlah Penduduk yang Mungkin</th>'
            '<th>Wilayah</th>'
            '<th>Jumlah Penduduk</th>'
            '<th>Jumlah Penduduk yang Mungkin</th>'
            '</tr>'
            '</thead>')
        i = 0
        while i < line_count:
            i += 1
            html += (
                '<tr>'
                '<td>%(i)s</td><td>%(i)s</td><td>%(i)s</td>'
                '<td>%(i)s</td><td>%(i)s</td><td>%(i)s</td>'
                '</tr>') % {'i': i}
        html += '</table>'
        return html

    def test_print_to_pdf(self):
        """Test that we can render some html to a pdf (most common use case).
        """
        LOGGER.debug('InaSAFE HtmlRenderer testing printToPdf')
        html = self.sample_html()
        page_dpi = 300
        renderer = HtmlRenderer(page_dpi)
        path = unique_filename(
            prefix='testHtmlTable',
            suffix='.pdf',
            dir=temp_dir('test'))
        LOGGER.debug(path)
        # If it fails new_path will come back as None
        new_path = renderer.to_pdf(html, path)
        message = 'Rendered output does not exist: %s' % new_path
        self.assertTrue(os.path.exists(new_path), message)
        # Also it should use our desired output file name
        message = 'Incorrect path - got: %s\nExpected: %s\n' % (
            new_path, path)
        self.assertEqual(path, new_path, message)
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        size = os.stat(new_path).st_size
        expected_size = 16600  # as rendered on linux ub 13.04-64 (MB)
        message = (
            'Expected rendered map pdf to be at least %s, got %s. '
            'Please update expected_size if the rendered output '
            'is acceptible on your system.'
            % (expected_size, size))
        self.assertTrue(size >= expected_size, message)

    def test_print_impact_table(self):
        """Test that we can render html from impact table keywords."""
        LOGGER.debug('InaSAFE HtmlRenderer testing printImpactTable')
        file_name = 'test_floodimpact.tif'
        layer, _ = load_layer(file_name)
        message = 'Layer is not valid: %s' % file_name
        self.assertTrue(layer.isValid(), message)
        page_dpi = 300
        html_renderer = HtmlRenderer(page_dpi)
        path = unique_filename(
            prefix='impact_table',
            suffix='.pdf',
            dir=temp_dir('test'))
        keyword_io = KeywordIO()
        keywords = keyword_io.read_keywords(layer)
        path = html_renderer.print_impact_table(keywords, filename=path)
        message = 'Rendered output does not exist: %s' % path
        self.assertTrue(os.path.exists(path), message)
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        size = os.stat(path).st_size
        expected_sizes = [
            20936,  # as rendered on linux ub 12.04 64
            21523,  # as rendered on linux ub 12.10 64
            20605,  # as rendered on linux ub 13.04 64
            13965,  # as rendered on linux ub 13.10 64
            14220,  # as rendered on linux ub 13.04 64 MB
            11074,  # as rendered on linux ub 14.04 64 AG
            17295,  # as rendered on linux ub 14.04_64 TS
            18665,  # as rendered on Jenkins per 19 June 2014
            377191,  # as rendered on OSX
            17556,  # as rendered on Windows 7_32
            16163L,  # as rendered on Windows 7 64 bit Ultimate i3
            251782L,  # as rendered on Windows 8 64 bit amd
            21491,  # as rendered on Slackware64 14.0
            18667,  # as rendered on Linux Mint 14_64
        ]
        print 'Output pdf to %s' % path
        self.assertIn(size, expected_sizes)

    def test_render_html_to_image(self):
        """Test that we can render html to a pixmap."""
        LOGGER.debug('InaSAFE HtmlRenderer testing renderHtmlToImage')
        html = self.sample_html(20)
        LOGGER.debug(html)
        page_dpi = 100
        renderer = HtmlRenderer(page_dpi)
        path = unique_filename(
            prefix='testHtmlToImage',
            suffix='.png',
            dir=temp_dir('test'))
        LOGGER.debug(path)
        width = 150
        pixmap = renderer.html_to_image(html, width)
        self.assertFalse(pixmap.isNull())
        LOGGER.debug(pixmap.__class__)
        pixmap.save(path)
        message = 'Rendered output does not exist: %s' % path
        self.assertTrue(os.path.exists(path), message)

        tolerance = 1000  # to allow for version number changes in disclaimer
        flag, message = check_images(
            'renderHtmlToImage', path, tolerance)
        self.assertTrue(flag, message + '\n' + path)

if __name__ == '__main__':
    suite = unittest.makeSuite(HtmlRendererTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
