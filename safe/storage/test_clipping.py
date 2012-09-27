import unittest
import numpy
from os.path import join

from safe.common.testing import TESTDATA
from safe.common.polygon import is_inside_polygon, inside_polygon
from safe.storage.vector import Vector
from safe.storage.core import read_layer
from safe.storage.clipping import clip_raster_by_polygons


# FIXME (Ole): Move this along with contents of clipping.py to
# common and consolidate
class Test_Clipping(unittest.TestCase):
    """Tests for clipping module
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clip_points_by_polygons(self):
        """Points can be clipped by polygons (real data)
        """

        # Name input files
        point_name = join(TESTDATA, 'population_5x5_jakarta_points.shp')
        point_layer = read_layer(point_name)
        points = numpy.array(point_layer.get_geometry())
        attrs = point_layer.get_data()

        # Loop through polygons
        for filename in ['polygon_0.shp', 'polygon_1.shp', 'polygon_2.shp',
                         'polygon_3.shp', 'polygon_4.shp',
                         'polygon_5.shp', 'polygon_6.shp']:

            polygon_layer = read_layer(join(TESTDATA, filename))
            polygon = polygon_layer.get_geometry()[0]

            # Clip
            indices = inside_polygon(points, polygon)

            # Sanity
            for point in points[indices, :]:
                assert is_inside_polygon(point, polygon)

            # Explicit tests
            if filename == 'polygon_0.shp':
                assert len(indices) == 6
            elif filename == 'polygon_1.shp':
                assert len(indices) == 2
                assert numpy.allclose(points[indices[0], :],
                                      [106.8125, -6.1875])
                assert numpy.allclose(points[indices[1], :],
                                      [106.8541667, -6.1875])
                assert numpy.allclose(attrs[indices[0]]['value'],
                                      331941.6875)
                assert numpy.allclose(attrs[indices[1]]['value'],
                                      496445.8125)
            elif filename == 'polygon_2.shp':
                assert len(indices) == 7
            elif filename == 'polygon_3.shp':
                assert len(indices) == 0  # Degenerate
            elif filename == 'polygon_4.shp':
                assert len(indices) == 0  # Degenerate
            elif filename == 'polygon_5.shp':
                assert len(indices) == 8
            elif filename == 'polygon_6.shp':
                assert len(indices) == 6

    test_clip_points_by_polygons.slow = True

    def test_clip_raster_by_polygons(self):
        """Raster grids can be clipped by polygon layers

        # See qgis project in test data: raster_point_and_clipping_test.qgs
        """

        # Name input files
        poly = join(TESTDATA, 'kabupaten_jakarta_singlepart.shp')
        grid = join(TESTDATA, 'population_5x5_jakarta.asc')

        # Get layers using API
        P = read_layer(poly)
        R = read_layer(grid)

        M = len(P)
        N = len(R)
        assert N == 56

        # Clip
        C = clip_raster_by_polygons(R, P)
        assert len(C) == M

        # Check points inside polygon
        tot = 0
        for c in C:
            tot += len(c)
        assert tot == 14

        # Check that points are inside the right polygon
        for i, polygon in enumerate(P.get_geometry()):

            points = C[i][0]
            values = C[i][1]

            # Sanity first
            for point in points:
                assert is_inside_polygon(point, polygon)

            # Specific tests against raster pixel values inside polygons
            # The values are read from qgis
            if i == 0:
                assert len(points) == 6
                assert numpy.allclose(values[0], 200951)
                assert numpy.allclose(values[1], 283237)
                assert numpy.allclose(values[2], 278385)
                assert numpy.allclose(values[3], 516061)
                assert numpy.allclose(values[4], 207414)
                assert numpy.allclose(values[5], 344466)

            elif i == 1:
                assert len(points) == 2
                msg = ('Got wrong coordinates %s, expected %s'
                       % (str(points[0, :]), str([106.8125, -6.1875])))
                assert numpy.allclose(points[0, :], [106.8125, -6.1875]), msg
                assert numpy.allclose(points[1, :], [106.8541667, -6.1875])
                assert numpy.allclose(values[0], 331942)
                assert numpy.allclose(values[1], 496446)
            elif i == 2:
                assert len(points) == 7
                assert numpy.allclose(values[0], 268579)
                assert numpy.allclose(values[1], 155795)
                assert numpy.allclose(values[2], 403674)
                assert numpy.allclose(values[3], 259280)
                assert numpy.allclose(values[4], 284526)
                assert numpy.allclose(values[5], 334370)
                assert numpy.allclose(values[6], 143325)
            elif i == 3:
                assert len(points) == 0  # Degenerate
            elif i == 4:
                assert len(points) == 0  # Degenerate
            elif i == 5:
                assert len(points) == 8
                assert numpy.allclose(values[0], 279103)
                assert numpy.allclose(values[1], 205762)
                assert numpy.allclose(values[2], 428705)
                assert numpy.allclose(values[3], 331093)
                assert numpy.allclose(values[4], 227514)
                assert numpy.allclose(values[5], 249308)
                assert numpy.allclose(values[6], 215739)
                assert numpy.allclose(values[7], 147447)
            elif i == 6:
                assert len(points) == 6
                assert numpy.allclose(values[0], 61836.4)
                assert numpy.allclose(values[1], 165723)
                assert numpy.allclose(values[2], 151307)
                assert numpy.allclose(values[3], 343787)
                assert numpy.allclose(values[4], 303627)
                assert numpy.allclose(values[5], 225232)

            # Generate layer objects
            values = [{'value': x} for x in C[i][1]]
            point_layer = Vector(data=values, geometry=points,
                                 projection=P.get_projection())
            assert point_layer.is_point_data

            polygon_layer = Vector(geometry=[polygon],
                                   projection=P.get_projection())
            assert polygon_layer.is_polygon_data

            # Generate spatial data for visualisation with e.g. QGIS
            if False:
                point_layer.write_to_file('points_%i.shp' % i)
                polygon_layer.write_to_file('polygon_%i.shp' % i)

    test_clip_raster_by_polygons.slow = True

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Clipping, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
