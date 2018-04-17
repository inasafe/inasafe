# coding=utf-8

import unittest

from qgis.core import QgsRectangle

from safe.test.utilities import get_qgis_app, load_test_raster_layer
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

from safe.gis.raster.clip_bounding_box import clip_by_extent

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestClipRaster(unittest.TestCase):

    """Tests for clipping a raster layer with an extent."""

    def test_clip_raster(self):
        """Test we can clip a raster layer."""
        layer = load_test_raster_layer('gisv4', 'hazard', 'earthquake.asc')
        expected = QgsRectangle(106.75, -6.2, 106.80, -6.1)
        new_layer = clip_by_extent(layer, expected)

        extent = new_layer.extent()
        self.assertAlmostEqual(expected.xMinimum(), extent.xMinimum(), 0)
        self.assertAlmostEqual(expected.xMaximum(), extent.xMaximum(), 0)
        self.assertAlmostEqual(expected.yMinimum(), extent.yMinimum(), 0)
        self.assertAlmostEqual(expected.yMaximum(), extent.yMaximum(), 0)
