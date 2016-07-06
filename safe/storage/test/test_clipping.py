# coding=utf-8
import unittest
import numpy
import os
from os.path import join

from safe.test.utilities import TESTDATA
from safe.gis.polygon import (
    is_inside_polygon,
    inside_polygon,
    populate_polygon,
    generate_random_points_in_bbox)
from safe.storage.vector import Vector
from safe.storage.core import read_layer
from safe.storage.geometry import Polygon
from safe.common.utilities import unique_filename


# FIXME (Ole): Move this along with contents of clipping.py to
# common and consolidate
class Test_Clipping(unittest.TestCase):
    """Tests for clipping module
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False), 'Slow test, skipped on travis')
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

    def test_clip_points_by_polygons_with_holes0(self):
        """Points can be clipped by polygons with holes
        """

        # Define an outer ring
        outer_ring = numpy.array([[106.79, -6.233],
                                  [106.80, -6.24],
                                  [106.78, -6.23],
                                  [106.77, -6.21],
                                  [106.79, -6.233]])

        # Define inner rings
        inner_rings = [numpy.array([[106.77827, -6.2252],
                                    [106.77775, -6.22378],
                                    [106.78, -6.22311],
                                    [106.78017, -6.22530],
                                    [106.77827, -6.2252]])[::-1],
                       numpy.array([[106.78652, -6.23215],
                                    [106.78642, -6.23075],
                                    [106.78746, -6.23143],
                                    [106.78831, -6.23307],
                                    [106.78652, -6.23215]])[::-1]]

        v = Vector(geometry=[Polygon(outer_ring=outer_ring,
                                     inner_rings=inner_rings)])
        assert v.is_polygon_data

        # Write it to file
        tmp_filename = unique_filename(suffix='.shp')
        v.write_to_file(tmp_filename)

        # Read polygon it back
        L = read_layer(tmp_filename)
        P = L.get_geometry(as_geometry_objects=True)[0]

        outer_ring = P.outer_ring
        inner_ring0 = P.inner_rings[0]
        inner_ring1 = P.inner_rings[1]

        # Make some test points
        points = generate_random_points_in_bbox(outer_ring, 1000, seed=13)

        # Clip to outer ring, excluding holes
        indices = inside_polygon(points, P.outer_ring, holes=P.inner_rings)

        # Sanity
        for point in points[indices, :]:
            # Must be inside outer ring
            assert is_inside_polygon(point, outer_ring)

            # But not in any of the inner rings
            assert not is_inside_polygon(point, inner_ring0)
            assert not is_inside_polygon(point, inner_ring1)

        if False:
            # Store for visual check
            pol = Vector(geometry=[P])
            tmp_filename = unique_filename(suffix='.shp')
            pol.write_to_file(tmp_filename)
            # print 'Polygon with holes written to %s' % tmp_filename

            pts = Vector(geometry=points[indices, :])
            tmp_filename = unique_filename(suffix='.shp')
            pts.write_to_file(tmp_filename)
            # print 'Clipped points written to %s' % tmp_filename

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False), 'Slow test, skipped on travis')
    def test_clip_points_by_polygons_with_holes_real(self):
        """Points can be clipped by polygons with holes (real data)
        """

        # Read real polygon with holes
        filename = '%s/%s' % (TESTDATA, 'donut.shp')
        L = read_layer(filename)

        # --------------------------------------------
        # Pick one polygon that has 2 inner rings
        P = L.get_geometry(as_geometry_objects=True)[1]

        outer_ring = P.outer_ring
        inner_ring0 = P.inner_rings[0]
        inner_ring1 = P.inner_rings[1]

        # Make some test points
        points_in_bbox = generate_random_points_in_bbox(outer_ring, 1000)
        points_in_inner_ring0 = populate_polygon(inner_ring0, 2, seed=13)
        points_in_inner_ring1 = populate_polygon(inner_ring1, 2, seed=17)
        points = numpy.concatenate((points_in_bbox,
                                    points_in_inner_ring0,
                                    points_in_inner_ring1))

        # Clip
        indices = inside_polygon(points, P.outer_ring, holes=P.inner_rings)

        # Sanity
        for point in points[indices, :]:
            # Must be inside outer ring
            assert is_inside_polygon(point, outer_ring)

            # But not in any of the inner rings
            assert not is_inside_polygon(point, inner_ring0)
            assert not is_inside_polygon(point, inner_ring1)

        # ---------------------------------------------------------
        # Pick a polygon that has 1 inner ring (nice visualisation)
        P = L.get_geometry(as_geometry_objects=True)[9]

        outer_ring = P.outer_ring
        inner_ring = P.inner_rings[0]

        # Make some test points
        points = generate_random_points_in_bbox(outer_ring, 500)

        # Clip
        indices = inside_polygon(points, P.outer_ring, holes=P.inner_rings)

        # Sanity
        for point in points[indices, :]:
            # Must be inside outer ring
            assert is_inside_polygon(point, outer_ring)

            # But not in the inner ring
            assert not is_inside_polygon(point, inner_ring)

        # Store for visual check (nice one!)
        # Uncomment os.remove if you want see the layers
        pol = Vector(geometry=[P])
        tmp_filename = unique_filename(suffix='.shp')
        pol.write_to_file(tmp_filename)
        # print 'Polygon with holes written to %s' % tmp_filename
        os.remove(tmp_filename)

        pts = Vector(geometry=points[indices, :])
        tmp_filename = unique_filename(suffix='.shp')
        pts.write_to_file(tmp_filename)
        # print 'Clipped points written to %s' % tmp_filename
        os.remove(tmp_filename)

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Clipping, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
