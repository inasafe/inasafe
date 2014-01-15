
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
        QgsApplication
        )


from qgis_vector_tools import (
    points_to_rectangles,
    union_geometry
    )


class Test_qgis_raster_tools(unittest.TestCase):

    def test_points_to_rectangles(self):
        """Test points_to_rectangles works
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
            self.assertAlmostEquals(geom.area(), dx*dy)

            p = geom.centroid().asPoint()
            x, y = [attr[index].toDouble()[0] for index in [x_index, y_index]]
            self.assertLess(abs(p.x()-x), dx)
            self.assertLess(abs(p.y()-y), dy)
    test_points_to_rectangles.slow = False

    def test_union_geometry(self):
        """Test union_geometry works"""

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
    test_union_geometry.slow = False

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
