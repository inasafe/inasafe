# coding=utf-8
"""**Tests for map creation in QGIS plugin.**

"""

__author__ = 'Tim Sutton <tim@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import os
import logging

# Add PARENT directory to path to make test aware of other modules
#pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(pardir)

from qgis.core import (
    QgsMapLayerRegistry,
    QgsRectangle)
from qgis.gui import QgsMapCanvasLayer

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe_qgis.utilities.utilities_for_testing import load_layer
from safe_qgis.report.map import Map

LOGGER = logging.getLogger('InaSAFE')


class MapTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""

    def setUp(self):
        """Setup fixture run before each tests"""
        # noinspection PyArgumentList
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()

    def test_get_map_title(self):
        """Getting the map title from the keywords"""
        layer, _ = load_layer('test_floodimpact.tif')
        report = Map(IFACE)
        report.set_impact_layer(layer)
        title = report.map_title()
        expected_title = 'Penduduk yang Mungkin dievakuasi'
        message = 'Expected: %s\nGot:\n %s' % (expected_title, title)
        assert title == expected_title, message

    def test_handle_missing_map_title(self):
        """Missing map title from the keywords fails gracefully"""
        # TODO running OSM Buildngs with Pendudk Jakarta
        # wasthrowing an error when requesting map title
        # that this test wasnt replicating well
        layer, _ = load_layer('population_padang_1.asc')
        report = Map(IFACE)
        report.set_impact_layer(layer)
        title = report.map_title()
        expected_title = None
        message = 'Expected: %s\nGot:\n %s' % (expected_title, title)
        assert title == expected_title, message

    def test_default_template(self):
        """Test that loading default template works"""
        LOGGER.info('Testing default_template')
        layer, _ = load_layer('test_shakeimpact.shp')
        canvas_layer = QgsMapCanvasLayer(layer)
        CANVAS.setLayerSet([canvas_layer])
        rect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(rect)
        CANVAS.refresh()
        report = Map(IFACE)
        report.set_impact_layer(layer)
        out_path = unique_filename(
            prefix='mapDefaultTemplateTest',
            suffix='.pdf',
            dir=temp_dir('test'))
        report.make_pdf(out_path)
        LOGGER.debug(out_path)
        message = 'Rendered output does not exist: %s' % out_path
        self.assertTrue(os.path.exists(out_path), message)
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        out_size = os.stat(out_path).st_size

        # Note: You should replace, not append the numbers for a given
        # platform. Also note that this test will break every time the
        # version number of InaSAFE changes so we should ultimately come up
        # with a lower maintenance test strategy.
        expected_sizes = [
            405359,  # Ubuntu 13.04_64
            427172,  # Ubuntu 13.10_64
            139236,  # Ubuntu 14.04_64 AG
            152980,  # Ubuntu 14.04_64 TS - pycharm
            152862,  # Ubuntu 14.04_64 TS - make - TODO why is this?
            414589,  # Slackware64 14.0
            144542,  # Linux Mint 14_64
            148267,  # Windows 7 32
            150412,  # Windows 7 64
            143652,  # UB 12.04 Jenkins
        ]
        message = '%s\nExpected rendered map pdf to be in %s, got %s' % (
            out_path, expected_sizes, out_size)
        self.assertIn(out_size, expected_sizes, message)

    def test_custom_logo(self):
        """Test that setting user-defined logo works."""
        LOGGER.info('Testing custom_logo')
        layer, _ = load_layer('test_shakeimpact.shp')
        canvas_layer = QgsMapCanvasLayer(layer)
        CANVAS.setLayerSet([canvas_layer])
        rect = QgsRectangle(106.7894, -6.2308, 106.8004, -6.2264)
        CANVAS.setExtent(rect)
        CANVAS.refresh()
        report = Map(IFACE)
        report.set_impact_layer(layer)
        report.set_organisation_logo(":/plugins/inasafe/logo-flower.png")
        out_path = unique_filename(
            prefix='mapCustomLogoTest', suffix='.pdf', dir=temp_dir('test'))
        report.make_pdf(out_path)
        LOGGER.debug(out_path)
        message = 'Rendered output does not exist: %s' % out_path
        self.assertTrue(os.path.exists(out_path), message)
        # pdf rendering is non deterministic so we can't do a hash check
        # test_renderComposition renders just the image instead of pdf
        # so we hash check there and here we just do a basic minimum file
        # size check.
        out_size = os.stat(out_path).st_size

        # Note: You should replace, not append the numbers for a given
        # platform. Also note that this test will break every time the
        # version number of InaSAFE changes so we should ultimately come up
        # with a lower maintenance test strategy.

        expected_sizes = [
            402083,  # Ubuntu 13.04_64
            400563,  # Ubuntu 13.10_64
            76960,  # Ubuntu 14.04_64 AG
            90704,  # Ubuntu 14.04_64 TS pycharm
            90582,  # Ubuntu 14.04_64 TS make - TODO why is this?
            367934,  # Slackware64 14.0
            82263,  # Linux Mint 14_64
            85418,  # Windows 7 32bit
            88779,  # Windows 7 64bit
            81373,   # Jenkins ub 12.04
        ]
        message = '%s\nExpected rendered map pdf to be in %s, got %s' % (
            out_path, expected_sizes, out_size)
        self.assertIn(out_size, expected_sizes, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(MapTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
