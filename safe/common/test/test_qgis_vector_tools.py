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
from safe.common.gdal_ogr_tools import (
    polygonize_thresholds)
if qgis_imported:  # Import QgsRasterLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from PyQt4.QtCore import QVariant
    from qgis.core import (
        QgsVectorLayer,
        QgsPoint,
        QgsField,
        QgsFeature,
        QgsGeometry,
        QgsRectangle)


from safe.common.qgis_vector_tools import (
    points_to_rectangles,
    union_geometry,
    create_layer,
    clip_by_polygon,
    split_by_polygon,
    split_by_polygon_in_out)


class TestQGISVectorTools(unittest.TestCase):

    def setUp(self):
        self.polygon_base = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'polygonization_result'))
        self.line_before = os.path.abspath(
            os.path.join(UNITDATA, 'other', 'line_before_splitting'))
        self.line_after = os.path.abspath(
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
            x, y = [attr[index] for index in [x_index, y_index]]
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
        # noinspection PyCallByClass,PyTypeChecker
        expected_area = QgsGeometry.fromPolygon([[
            QgsPoint(10, 30),
            QgsPoint(40, 30),
            QgsPoint(40, 0),
            QgsPoint(10, 0)]])

        self.assertTrue(geom.isGeosValid())
        self.assertFalse(geom.isMultipart())
        self.assertAlmostEquals(geom.area(), 3 * dx * 3 * dy)
        self.assertTrue((geom.isGeosEqual(expected_area)))

        polygons = points_to_rectangles(points, 0.5 * dx, 0.5 * dy)
        geom = union_geometry(polygons)
        # The union is 9 squares
        self.assertAlmostEquals(geom.area(), 1.5 * dx * 1.5 * dy)
        self.assertTrue(geom.isMultipart())
    test_union_geometry.slow = False

    def test_create_layer(self):
        """Test create layer work"""

        # Lines
        line_layer = QgsVectorLayer(
            self.line_before + '.shp', 'test', 'ogr')
        new_layer = create_layer(line_layer)
        self.assertEquals(new_layer.geometryType(), line_layer.geometryType())
        self.assertEquals(new_layer.crs(), line_layer.crs())
        fields = line_layer.dataProvider().fields()
        new_fields = new_layer.dataProvider().fields()
        self.assertEquals(new_fields.toList(), fields.toList())

        # Polygon
        polygon_layer = QgsVectorLayer(
            self.polygon_base + '.shp', 'test', 'ogr')
        new_layer = create_layer(polygon_layer)
        self.assertEquals(
            new_layer.geometryType(),
            polygon_layer.geometryType()
        )
        self.assertEquals(new_layer.crs(), polygon_layer.crs())
        fields = polygon_layer.dataProvider().fields()
        new_fields = new_layer.dataProvider().fields()
        self.assertEquals(new_fields.toList(), fields.toList())

    def test_clip_by_polygon(self):
        """Test clip_by_polygon work"""
        line_before = QgsVectorLayer(
            self.line_before + '.shp', 'test', 'ogr')
        lines = QgsVectorLayer(
            self.line_after + '.shp', 'test', 'ogr')
        polygon_layer = QgsVectorLayer(
            self.polygon_base + '.shp', 'test', 'ogr')

        # Only one polygon is stored in the layer
        for feature in polygon_layer.getFeatures():
            polygon = feature.geometry()

        clipped_lines = clip_by_polygon(
            line_before,
            polygon)

        # Test the lines is not multipart
        for feature in clipped_lines.getFeatures():
            self.assertFalse(feature.geometry().isMultipart())

        # Lines with flooded=1 lie within the polygon
        for feature in clipped_lines.getFeatures():
            found = False
            for expected in lines.getFeatures():
                if (expected.attributes()[2] == 1) and \
                   (feature.geometry().isGeosEqual(expected.geometry())):
                    found = True
                    break
            self.assertTrue(found)
    test_clip_by_polygon.slow = True

    def test_split_by_polygon(self):
        """Test split_by_polygon work"""
        line_before = QgsVectorLayer(
            self.line_before + '.shp', 'test', 'ogr')
        expected_lines = QgsVectorLayer(
            self.line_after + '.shp', 'test', 'ogr')
        polygon_layer = QgsVectorLayer(
            self.polygon_base + '.shp', 'test', 'ogr')

        # Only one polygon is stored in the layer
        for feature in polygon_layer.getFeatures():
            polygon = feature.geometry()

        split_lines = split_by_polygon(
            line_before,
            polygon,
            mark_value=('flooded', 1))

        # Test the lines is not multipart
        for feature in split_lines.getFeatures():
            self.assertFalse(feature.geometry().isMultipart())

        self.assertEqual(expected_lines.featureCount(),
                         split_lines.featureCount())
        # Assert for every line from split_lines
        # we can find the same line
        for feature in split_lines.getFeatures():
            found = False
            for expected in expected_lines.getFeatures():
                if (feature.attributes() == expected.attributes()) and \
                   (feature.geometry().isGeosEqual(expected.geometry())):
                    found = True
                    break
            self.assertTrue(found)

        # Split by the extent (The result is the copy of the layer)
        line_before.updateExtents()
        # Expand extent to cover the lines (add epsilon to bounds)
        epsilon = 0.0001    # A small number
        extent = line_before.extent()
        new_extent = QgsRectangle(
            extent.xMinimum() - epsilon,
            extent.yMinimum() - epsilon,
            extent.xMaximum() + epsilon,
            extent.yMaximum() + epsilon
        )
        new_extent = QgsGeometry().fromRect(new_extent)
        split_lines = split_by_polygon(
            line_before,
            new_extent)
        for feature in split_lines.getFeatures():
            found = False
            for expected in line_before.getFeatures():
                if (feature.attributes() == expected.attributes()) and \
                   (feature.geometry().isGeosEqual(expected.geometry())):
                    found = True
                    break
            self.assertTrue(found)
    test_split_by_polygon.slow = True

    def _create_points(self):
        """Create points for testing"""

        point_layer = QgsVectorLayer('Point?crs=EPSG:4326', 'points', 'memory')

        point_provider = point_layer.dataProvider()
        point_provider.addAttributes([QgsField('X', QVariant.Double)])
        point_provider.addAttributes([QgsField('Y', QVariant.Double)])
        x_index = point_provider.fieldNameIndex('X')
        y_index = point_provider.fieldNameIndex('Y')

        point_layer.startEditing()
        for x in [10.0, 20.0, 30.0]:
            for y in [10.0, 20.0, 30.0]:
                feature = QgsFeature()
                feature.initAttributes(2)
                feature.setAttribute(x_index, x)
                feature.setAttribute(y_index, y)
                # noinspection PyCallByClass
                geom = QgsGeometry.fromPoint(QgsPoint(x, y))
                feature.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feature])
        point_layer.commitChanges()

        return point_layer

    def test_split_by_polygon_in_out(self):
        """Test split_by_polygon in-out work"""

        raster_name = os.path.join(
            UNITDATA,
            'hazard',
            'jakarta_flood_design.tif')

        exposure_name = os.path.join(
            UNITDATA,
            'exposure',
            'roads_osm_4326.shp')
        qgis_exposure = QgsVectorLayer(
            exposure_name,
            'EXPOSURE',
            'ogr')

        inside_file_name, inside_layer_name, outside_file_name, \
            outside_layer_name = polygonize_thresholds(raster_name, 0.1)

        polygon_in = \
            QgsVectorLayer(inside_file_name, inside_layer_name, 'ogr')
        polygon_out = \
            QgsVectorLayer(outside_file_name, outside_layer_name, 'ogr')

        layer = split_by_polygon_in_out(
            qgis_exposure, polygon_in, polygon_out, 'flooded', 1)

        feature_count = layer.featureCount()
        self.assertEqual(feature_count, 184)

        flooded = 0
        iterator = layer.getFeatures()
        for feature in iterator:
            attributes = feature.attributes()
            if attributes[3] == 1:
                flooded += 1
        self.assertEqual(flooded, 25)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestQGISVectorTools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
