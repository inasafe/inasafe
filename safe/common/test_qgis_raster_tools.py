# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'kolesov.dm@gmail.com'
__date__ = '20/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.common.testing import UNITDATA, get_qgis_app
from safe.storage.raster import qgis_imported

if qgis_imported:   # Import QgsRasterLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import (
        QgsRasterLayer,
        QgsRaster,
        QgsPoint,
        QgsVectorLayer,
        QgsRectangle)


# noinspection PyUnresolvedReferences
RASTER_BASE = os.path.abspath(
    os.path.join(UNITDATA, 'hazard', 'jakarta_flood_design'))
# noinspection PyUnresolvedReferences
VECTOR_BASE = os.path.abspath(
    os.path.join(UNITDATA, 'other', 'polygonization_result'))

from safe.common.qgis_raster_tools import (
    pixels_to_points,
    polygonize,
    clip_raster)


class TestQGISRasterTools(unittest.TestCase):

    def setUp(self):
        self.raster = QgsRasterLayer(RASTER_BASE + '.tif', 'test')
        self.provider = self.raster.dataProvider()
        self.extent = self.raster.extent()
        self.x_res = self.raster.rasterUnitsPerPixelX()
        self.y_res = self.raster.rasterUnitsPerPixelY()

    def test_pixels_to_points(self):
        points = pixels_to_points(
            self.raster, threshold_min=1.0, threshold_max=1.5)

        # There are four such pixels only
        self.assertEquals(points.featureCount(), 4)
        for point in points.dataProvider().getFeatures():
            point = point.geometry().asPoint()

            # Move point in center of the pixels and get the value
            value = self.provider.identify(
                QgsPoint(
                    point.x() + 0.5 * self.x_res,
                    point.y() - 0.5 * self.y_res),
                QgsRaster.IdentifyFormatValue,
                self.extent)
            value = value.results()[1]
            self.assertGreater(value, 1.0)
            self.assertLess(value, 1.5)

        # Infinite threshold test
        points = pixels_to_points(self.raster, threshold_min=1.1)
        self.assertEquals(points.featureCount(), 8)
        for point in points.dataProvider().getFeatures():
            point = point.geometry().asPoint()

            # Move point in center of the pixels and get the value
            value = self.provider.identify(
                QgsPoint(
                    point.x() + 0.5 * self.x_res,
                    point.y() - 0.5 * self.y_res),
                QgsRaster.IdentifyFormatValue,
                self.extent)
            value = value.results()[1]
            self.assertGreater(value, 1.1)
    test_pixels_to_points.slow = True

    def test_polygonize(self):
        """Test if polygonize works"""
        geometry = polygonize(
            self.raster, threshold_min=1.0, threshold_max=1.5)
        # Result is one square
        self.assertTrue(geometry.isGeosValid())
        self.assertFalse(geometry.isMultipart())

        # noinspection PyArgumentEqualDefault
        geometry = polygonize(self.raster, threshold_min=0.0)
        # Result is several polygons
        self.assertTrue(geometry.isGeosValid())
        self.assertTrue(geometry.isMultipart())

        expected = QgsVectorLayer(VECTOR_BASE + '.shp', 'test', 'ogr')
        for feature in expected.getFeatures():
            # the layer has one feature only
            expected_geom = feature.geometry()
            self.assertTrue((geometry.isGeosEqual(expected_geom)))
    test_polygonize.slow = True

    def test_clip_raster(self):
        """Test clip_raster work"""
        new_raster = clip_raster(
            self.raster,
            self.raster.width(),
            self.raster.height(),
            self.extent
        )

        self.assertEqual(self.raster.rasterUnitsPerPixelY(),
                         new_raster.rasterUnitsPerPixelY())
        self.assertEqual(self.raster.rasterUnitsPerPixelX(),
                         new_raster.rasterUnitsPerPixelX())
        self.assertEqual(self.raster.extent(),
                         new_raster.extent())
        self.assertEqual(self.raster.width(),
                         new_raster.width())
        self.assertEqual(self.raster.height(),
                         new_raster.height())

        # Set extent as 1/2 of self.extent
        center = self.extent.center()
        x_max, y_max = center.x(), center.y()
        new_extent = QgsRectangle(
            self.extent.xMinimum(),
            self.extent.yMinimum(),
            x_max,
            y_max
        )
        new_raster = clip_raster(
            self.raster,
            self.raster.width(),
            self.raster.height(),
            new_extent
        )
        self.assertAlmostEquals(
            self.raster.rasterUnitsPerPixelY(),
            2 * new_raster.rasterUnitsPerPixelY())
        self.assertAlmostEquals(
            self.raster.rasterUnitsPerPixelX(),
            2 * new_raster.rasterUnitsPerPixelX())
        self.assertEqual(new_extent, new_raster.extent())
        self.assertEqual(self.raster.width(), new_raster.width())
        self.assertEqual(self.raster.height(), new_raster.height())
    test_clip_raster.slow = True

if __name__ == '__main__':
    suite = unittest.makeSuite(TestQGISRasterTools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
