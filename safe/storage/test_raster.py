# coding=utf-8
"""**Tests for safe raster layer class**
    contains tests for QGIS specific methods.
    See test_io.py also
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '28/12/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging
import unittest

from safe.common.testing import UNITDATA, get_qgis_app
from safe.storage.utilities import read_keywords
from safe.storage.raster import Raster, qgis_imported

if qgis_imported:   # Import QgsRasterLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import QgsRasterLayer

LOGGER = logging.getLogger('InaSAFE')
KEYWORD_PATH = os.path.abspath(
    os.path.join(UNITDATA, 'hazard', 'jakarta_flood_design.keywords'))
RASTER_BASE = os.path.abspath(
    os.path.join(UNITDATA, 'hazard', 'jakarta_flood_design'))


class RasterTest(unittest.TestCase):

    def setUp(self):
        msg = 'Keyword file does not exist at %s' % KEYWORD_PATH
        assert os.path.exists(KEYWORD_PATH), msg

    def test_qgis_raster_layer_loading(self):
        """Test that reading from QgsRasterLayer works."""
        if qgis_imported:
            # This line is the cause of the problem:
            qgis_layer = QgsRasterLayer(RASTER_BASE + '.tif', 'test')
            layer = Raster(data=qgis_layer)
            qgis_extent = qgis_layer.dataProvider().extent()
            qgis_extent = [qgis_extent.xMinimum(), qgis_extent.yMinimum(),
                           qgis_extent.xMaximum(), qgis_extent.yMaximum()]
            layer_exent = layer.get_bounding_box()
            self.assertListEqual(
                layer_exent, qgis_extent,
                'Expected %s extent, got %s' % (qgis_extent, layer_exent))

    def test_convert_to_qgis_rastet_layer(self):
        """Test that converting to QgsVectorLayer works."""
        if qgis_imported:
            # Create vector layer
            keywords = read_keywords(RASTER_BASE + '.keywords')
            layer = Raster(data=RASTER_BASE + '.tif', keywords=keywords)

            # Convert to QgsRasterLayer
            qgis_layer = layer.as_qgis_native()
            qgis_extent = qgis_layer.dataProvider().extent()
            qgis_extent = [qgis_extent.xMinimum(), qgis_extent.yMinimum(),
                           qgis_extent.xMaximum(), qgis_extent.yMaximum()]
            layer_exent = layer.get_bounding_box()
            self.assertListEqual(
                layer_exent, qgis_extent,
                'Expected %s extent, got %s' % (qgis_extent, layer_exent))


if __name__ == '__main__':
    suite = unittest.makeSuite(RasterTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
