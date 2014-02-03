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
    from PyQt4.QtCore import QVariant
    from qgis.core import (
        QgsVectorLayer,
        QgsPoint,
        QgsField,
        QgsFeature,
        QgsGeometry,
        QgsFeatureRequest,
        QgsApplication
        )


from qgis_vector_tools import (
    points_to_rectangles,
    union_geometry,
    split_by_polygon
    )


class Test_qgis_raster_tools(unittest.TestCase):

    def setUp(self):
        self.POLYGON_BASE = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'polygonization_result'))
        self.LINE_BEFORE = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'line_before_splitting'))
        self.LINE_AFTER = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'line_after_splitting1'))

    def test_points_to_rectangles(self):
        """Test points_to_rectangles work
        """
        points = self._create_points()
        x_index = points.dataProvider().fieldNameIndex('X')
        y_index = points.dataProvider().fieldNameIndex('Y')
        dx, dy = 1, 2
        polygons = points_to_rectangles(points, dx, dy)
        for feature in polygons.getFeatures():
            geom = feature.geometry()
            attr = feature.attributes()

            self.assertTrue(geom.isGeosValid())
            self.assertAlmostEquals(geom.area(), dx * dy)

            p = geom.centroid().asPoint()
            x, y = [attr[index].toDouble()[0] for index in [x_index, y_index]]
            self.assertLess(abs(p.x() - x), dx)
            self.assertLess(abs(p.y() - y), dy)
    test_points_to_rectangles.slow = False

    def test_union_geometry(self):
        """Test union_geometry work"""

        # Create big polygons from the point layer,
        # then the union is one BIG polygon
        dx = dy = 10
        points = self._create_points()
        polygons = points_to_rectangles(points, dx, dy)
        geom = union_geometry(polygons)

        # The union is the rectangle
        expected_area = QgsGeometry.fromPolygon([
            [QgsPoint(10, 30),
             QgsPoint(40, 30),
             QgsPoint(40, 0),
             QgsPoint(10, 0)]
        ])

        self.assertTrue(geom.isGeosValid())
        self.assertFalse(geom.isMultipart())
        self.assertAlmostEquals(geom.area(), 3*dx * 3*dy)
        self.assertTrue((geom.isGeosEqual(expected_area)))

        polygons = points_to_rectangles(points, 0.5 * dx, 0.5 * dy)
        geom = union_geometry(polygons)
        # The union is 9 squares
        self.assertAlmostEquals(geom.area(), 1.5*dx * 1.5*dy)
        self.assertTrue(geom.isMultipart())
    test_union_geometry.slow = False

    def test_split_by_polygon(self):
        """Test split_by_polygon work"""
        line_before = QgsVectorLayer(
            self.LINE_BEFORE + '.shp', 'test', 'ogr')
        expected_lines = QgsVectorLayer(
            self.LINE_AFTER + '.shp', 'test', 'ogr')
        polygon_layer = QgsVectorLayer(
            self.POLYGON_BASE + '.shp', 'test', 'ogr')

        # Only one polygon is stored in the layer
        for feature in polygon_layer.getFeatures():
            polygon = feature.geometry()

        splitted_lines = split_by_polygon(line_before,
                                          polygon,
                                          mark_value=(1, 'INSIDE'))

        # Test the lines is not multipart
        for feature in splitted_lines.getFeatures():
            self.assertFalse(feature.geometry().isMultipart())

        self.assertEqual(expected_lines.featureCount(),
                         splitted_lines.featureCount())
        # Assert fo every line from splitted_lines
        # we can find the same line
        for feature in splitted_lines.getFeatures():
            found = False
            for expected in expected_lines.getFeatures():
                if (feature.attributes() == expected.attributes()) and \
                    (feature.geometry().isGeosEqual(expected.geometry())):
                    found = True
                    break
            self.assertTrue(found)
    test_split_by_polygon.slow = True

    def _create_points(self):
        """Create points for testing"""

        point_layer = QgsVectorLayer(
        'Point?crs=EPSG:4326', 'points', 'memory')

        point_provider = point_layer.dataProvider()
        point_provider.addAttributes([QgsField('X', QVariant.Double)])
        point_provider.addAttributes([QgsField('Y', QVariant.Double)])
        x_index = point_provider.fieldNameIndex('X')
        y_index = point_provider.fieldNameIndex('Y')

        point_layer.startEditing()
        for x in [10, 20, 30]:
            for y in [10, 20, 30]:
                feature = QgsFeature()
                feature.initAttributes(2)
                feature.setAttribute(x_index, x)
                feature.setAttribute(y_index, y)
                geom = QgsGeometry.fromPoint(QgsPoint(x, y))
                feature.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feature])
        point_layer.commitChanges()

        return point_layer


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_qgis_raster_tools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
