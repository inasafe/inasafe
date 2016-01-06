# coding=utf-8
"""io related tests."""
import unittest
import numpy
import os
from osgeo import gdal

from safe.storage.raster import Raster
from safe.storage.vector import Vector, convert_polygons_to_centroids
from safe.storage.projection import Projection, DEFAULT_PROJECTION
from safe.storage.utilities import (
    write_keywords,
    read_keywords,
    bbox_intersection,
    minimal_bounding_box,
    buffered_bounding_box,
    array_to_wkt,
    calculate_polygon_area,
    calculate_polygon_centroid,
    points_along_line,
    geotransform_to_bbox,
    geotransform_to_resolution,
    raster_geometry_to_geotransform)
from safe.storage.core import (
    read_layer,
    write_raster_data,
    get_bounding_box,
    bboxlist2string,
    bboxstring2list,
    check_bbox_string)
from safe.storage.test.utilities import same_API
from safe.storage.geometry import Polygon
from safe.gis.numerics import nan_allclose
from safe.test.utilities import (
    TESTDATA,
    HAZDATA,
    DATADIR)
from safe.common.utilities import unique_filename
from safe.gis.polygon import is_inside_polygon
from safe.common.exceptions import (
    BoundingBoxError,
    ReadLayerError,
    VerificationError,
    InaSAFEError)

# Known feature counts in test data
FEATURE_COUNTS = {
    'test_buildings.shp': 144,
    'tsunami_building_exposure.shp': 19,
    'kecamatan_geo.shp': 42,
    'Padang_WGS84.shp': 3896,
    'OSM_building_polygons_20110905.shp': 34960,
    'indonesia_highway_sample.shp': 2,
    'OSM_subset.shp': 79,
    'kecamatan_jakarta_osm.shp': 47}

GEOTRANSFORMS = [(105.3000035, 0.008333, 0.0, -5.5667785, 0.0, -0.008333),
                 (105.29857, 0.0112, 0.0, -5.565233000000001, 0.0, -0.0112),
                 (96.956, 0.03074106, 0.0, 2.2894972560001, 0.0, -0.03074106)]


# Auxiliary function for raster test
def linear_function(x, y):
    """Auxiliary function for use with raster test
    :param x:
    :param y:
    """

    return x + y / 2.


class TestIO(unittest.TestCase):
    """Tests for reading and writing of raster and vector data.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instantiation_of_empty_layers(self):
        """Vector and Raster objects can be instantiated with None
        """

        v = Vector(None)
        assert v.get_name() is None
        assert v.is_inasafe_spatial_object
        assert str(v).startswith('Vector data')

        r = Raster(None)
        assert r.get_name() is None
        assert r.is_inasafe_spatial_object
        assert str(r).startswith('Raster data')

    def test_vector_feature_count(self):
        """Number of features read from vector data is as expected
        """

        # Read and verify test data
        for vectorname in ['test_buildings.shp',
                           'tsunami_building_exposure.shp',
                           'Padang_WGS84.shp',
                           'OSM_building_polygons_20110905.shp',
                           'OSM_subset.shp']:

            filename = '%s/%s' % (TESTDATA, vectorname)
            layer = read_layer(filename)
            coords = layer.get_geometry()
            attributes = layer.get_data()

            # Check basic data integrity
            n = len(layer)
            assert len(coords) == n
            assert len(attributes) == n
            assert FEATURE_COUNTS[vectorname] == n

    test_vector_feature_count.slow = True

    def test_reading_and_writing_of_vector_point_data(self):
        """Vector point data can be read and written correctly
        """

        # First test that some error conditions are caught
        filename = unique_filename(suffix='nshoe66u')
        try:
            read_layer(filename)
        except ReadLayerError:
            pass
        else:
            msg = 'Exception for unknown extension should have been raised'
            raise Exception(msg)

        filename = unique_filename(suffix='.gml')
        try:
            read_layer(filename)
        except ReadLayerError:
            pass
        else:
            msg = 'Exception for non-existing file should have been raised'
            raise Exception(msg)

        # Read and verify test data
        for vectorname in [
                'test_buildings.shp',
                'tsunami_building_exposure.shp',
                'Padang_WGS84.shp']:

            filename = '%s/%s' % (TESTDATA, vectorname)
            layer = read_layer(filename)
            coords = numpy.array(layer.get_geometry())
            attributes = layer.get_data()

            # Check basic data integrity
            N = len(layer)
            assert coords.shape[0] == N
            assert coords.shape[1] == 2

            assert FEATURE_COUNTS[vectorname] == N

            assert isinstance(layer.get_name(), basestring)

            # Check projection
            wkt = layer.get_projection(proj4=False)
            assert wkt.startswith('GEOGCS')

            assert layer.projection == Projection(DEFAULT_PROJECTION)

            # Check integrity of each feature
            field_names = None
            for i in range(N):
                # Consistency between of geometry and fields

                x1 = coords[i, 0]
                x2 = attributes[i]['LONGITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                x1 = coords[i, 1]
                x2 = attributes[i]['LATITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                # Verify that each feature has the same fields
                if field_names is None:
                    field_names = attributes[i].keys()
                else:
                    assert len(field_names) == len(attributes[i].keys())
                    assert field_names == attributes[i].keys()

            # Write data back to file
            # FIXME (Ole): I would like to use gml here, but OGR does not
            #              store the spatial reference! Ticket #18
            out_filename = unique_filename(suffix='.shp')
            Vector(geometry=coords, data=attributes, projection=wkt,
                   geometry_type='point').write_to_file(out_filename)

            # Read again and check
            layer = read_layer(out_filename)
            assert layer.is_point_data
            coords = numpy.array(layer.get_geometry())
            attributes = layer.get_data()

            # Check basic data integrity
            N = len(layer)
            assert coords.shape[0] == N
            assert coords.shape[1] == 2

            # Check projection
            assert layer.projection == Projection(DEFAULT_PROJECTION)

            # Check integrity of each feature
            field_names = None
            for i in range(N):

                # Consistency between of geometry and fields
                x1 = coords[i, 0]
                x2 = attributes[i]['LONGITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                x1 = coords[i, 1]
                x2 = attributes[i]['LATITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                # Verify that each feature has the same fields
                if field_names is None:
                    field_names = attributes[i].keys()
                else:
                    assert len(field_names) == len(attributes[i].keys())
                    assert field_names == attributes[i].keys()

            # Test individual extraction
            lon = layer.get_data(attribute='LONGITUDE')
            assert numpy.allclose(lon, coords[:, 0])

    test_reading_and_writing_of_vector_point_data.slow = True

    def Xtest_reading_and_writing_of_sqlite_vector_data(self):
        """SQLite vector data can be read and written correctly
        """

        # First test that some error conditions are caught
        filename = '%s/%s' % (TESTDATA, 'lembang_osm_20121003.sqlite')
        L = read_layer(filename)
        print L.get_attribute_names()

    def test_donut_polygons(self):
        """Donut polygon can be read, interpreted and written correctly
        """

        # Read real polygon with holes
        filename = '%s/%s' % (TESTDATA, 'donut.shp')
        L = read_layer(filename)

        # Write this new object, read it again and check
        tmp_filename = unique_filename(suffix='.shp')
        L.write_to_file(tmp_filename)

        # Read back
        R = read_layer(tmp_filename)
        msg = ('Geometry of polygon was not preserved after reading '
               'and re-writing')

        # Check
        assert R == L, msg

    test_donut_polygons.slow = True

    def test_3d_polygon(self):
        """3D polygons can be read correctly with z component dismissed

        3D polygons are a specialisation of '2d' polygons which assigns
        a 'z' to each vertex (wkbPolygon25D in ogr parlance).
        It's normally referred to as 2.5D since the format does not
        truly represent volumetric spaces

        This test verifies that such polygons can be read as 2d - i.e.
        with the third dimension removed.

        ogrinfo reports this for 25d polygons::

          INFO: Open of `../inasafe_data/test/25dpolygon.shp'
          using driver `ESRI Shapefile' successful.
          1: 25dpolygon (3D Polygon)

        """

        # Read real polygon with holes
        filename = '%s/%s' % (TESTDATA, '25dpolygon.shp')
        l = read_layer(filename)

        # Write this new object, read it again and check
        tmp_filename = unique_filename(suffix='.shp')
        l.write_to_file(tmp_filename)

        # Read back
        r = read_layer(tmp_filename)
        msg = ('Geometry of polygon was not preserved after reading '
               'and re-writing')

        # Check
        assert r == l, msg

    def test_analysis_of_vector_data_top_N(self):
        """Analysis of vector data - get top N of an attribute
        """

        for vectorname in ['test_buildings.shp',
                           'tsunami_building_exposure.shp']:

            filename = '%s/%s' % (TESTDATA, vectorname)
            layer = read_layer(filename)
            attributes = layer.get_data()

            # Check exceptions
            try:
                L = layer.get_topN(attribute='FLOOR_AREA', N=0)
            except VerificationError:
                pass
            else:
                msg = 'Exception should have been raised for N == 0'
                raise Exception(msg)

            # Check results
            for N in [5, 10, 11, 17]:
                if vectorname == 'test_buildings.shp':
                    L = layer.get_topN(attribute='FLOOR_AREA', N=N)
                    assert len(L) == N

                    msg = ('Got projection %s, expected %s' %
                           (L.projection, layer.projection))
                    assert L.projection == layer.projection, msg
                    # print [a['FLOOR_AREA'] for a in L.attributes]
                elif vectorname == 'tsunami_building_exposure.shp':
                    L = layer.get_topN(attribute='STR_VALUE', N=N)
                    assert len(L) == N
                    assert L.get_projection() == layer.get_projection()
                    val = [a['STR_VALUE'] for a in L.data]

                    ref = [a['STR_VALUE'] for a in attributes]
                    ref.sort()

                    assert numpy.allclose(val, ref[-N:],
                                          atol=1.0e-12, rtol=1.0e-12)
                else:
                    raise Exception

    def test_vector_class(self):
        """Consistency of vector class for point data
        """

        # Read data file
        layername = 'test_buildings.shp'
        filename = '%s/%s' % (TESTDATA, layername)
        V = read_layer(filename)

        # Add some additional keywords
        V.keywords['keyword_version'] = '3.2'
        V.keywords['title'] = 'test'

        # Check string representation of vector class
        assert str(V).startswith('Vector data')
        assert str(len(V)) in str(V)

        # Make a smaller dataset
        V_ref = V.get_topN('FLOOR_AREA', 5)

        geometry = V_ref.get_geometry()
        data = V_ref.get_data()
        projection = V_ref.get_projection()

        assert 'keyword_version' in V_ref.get_keywords()
        assert 'title' in V_ref.get_keywords()

        # Create new object from test data
        v_new = Vector(data=data, projection=projection, geometry=geometry,
                       keywords=V_ref.get_keywords())

        # Check equality operations
        assert v_new == V_ref
        assert not v_new != V_ref

        v3 = v_new.copy()
        assert v_new == v3  # Copy is OK

        v3.data[0]['FLOOR_AREA'] += 1.0e-5
        assert v_new == v3  # Copy is OK within tolerance

        v3.data[0]['FLOOR_AREA'] += 1.0e-2
        assert v_new != v3  # Copy is outside tolerance

        v3 = v_new.copy()
        v4 = v_new.copy()
        v3.data[0]['BUILDING_C'] = True
        assert v4 == v3  # Booleans work

        v3.data[0]['BUILDING_C'] = False
        assert v4 != v3  # Booleans work

        v3.data[0]['BUILDING_C'] = None
        assert v4 != v3  # None works

        v3.data[0]['BUILDING_C'] = None
        v4.data[0]['BUILDING_C'] = False
        assert v4 == v3  # False matches None

        v3.data[0]['BUILDING_C'] = 0
        v4.data[0]['BUILDING_C'] = False
        assert v4 == v3  # False matches 0

        v3.data[0]['BUILDING_C'] = 1
        v4.data[0]['BUILDING_C'] = True
        assert v4 == v3  # True matches 1

        # Write this new object, read it again and check
        tmp_filename = unique_filename(suffix='.shp')
        v_new.write_to_file(tmp_filename)

        v_tmp = read_layer(tmp_filename)
        # Need to set this since we always use the latest version.
        v_tmp.keywords['keyword_version'] = V_ref.keywords['keyword_version']
        assert v_tmp == V_ref

        # Check that equality raises exception when type is wrong
        try:
            v_tmp == Raster()
        except TypeError:
            pass
        else:
            msg = 'Should have raised TypeError'
            raise Exception(msg)

        # Check that differences in keywords affect comparison
        # Need to set this since we always use the latest version.
        v_new.keywords['keyword_version'] = V_ref.keywords['keyword_version']
        assert v_new == V_ref
        v_tmp.keywords['kw2'] = 'blah'
        assert not v_tmp == V_ref
        assert v_tmp != V_ref

    def test_ordering_polygon_vertices(self):
        """Ordering of polygon vertices is preserved when writing and reading
        """

        # So far the admissible classes are Point, Line and Polygon
        tmp_filename = unique_filename(suffix='.shp')

        # Simple polygon (in clock wise order)
        p = numpy.array([[106.79, -6.23],
                         [106.80, -6.24],
                         [106.78, -6.23],
                         [106.77, -6.21]])

        v_ref = Vector(geometry=[p], geometry_type='polygon')
        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        for i in range(len(v_ref)):
            x = v_ref.get_geometry()[i]
            y = v_file.get_geometry()[i]
            msg = 'Read geometry %s, but expected %s' % (y, x)
            assert numpy.allclose(x, y), msg

        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_polygon_data
        assert v_file.geometry_type == 3

        # Reversed order (OGR will swap back to clockwise)
        p = numpy.array([[106.77, -6.21],
                         [106.78, -6.23],
                         [106.80, -6.24],
                         [106.79, -6.23]])

        v_ref = Vector(geometry=[p], geometry_type='polygon')
        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        for i in range(len(v_ref)):
            x = v_ref.get_geometry()[i]
            x = x[::-1, :]  # Flip Up-Down to get order clockwise
            y = v_file.get_geometry()[i]
            msg = 'Read geometry %s, but expected %s' % (y, x)
            assert numpy.allclose(x, y), msg
        assert v_file == v_ref
        assert v_ref == v_file
        assert v_ref.is_polygon_data
        assert v_ref.geometry_type == 3

        # Self intersecting polygon (in this case order will be flipped)
        p = numpy.array([[106.79, -6.23],
                         [106.80, -6.24],
                         [106.78, -6.23],
                         [106.79, -6.22],
                         [106.77, -6.21]])
        v_ref = Vector(geometry=[p], geometry_type='polygon')
        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        for i in range(len(v_ref)):
            x = v_ref.get_geometry()[i]
            x = x[::-1, :]  # Flip Up-Down to get order clockwise
            y = v_file.get_geometry()[i]
            msg = 'Read geometry %s, but expected %s' % (y, x)
            assert numpy.allclose(x, y), msg

        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_polygon_data
        assert v_file.geometry_type == 3

    def test_vector_class_geometry_types(self):
        """Admissible geometry types work in vector class

        Also check that reported bounding boxes are correct
        """

        # So far the admissible classes are Point, Line and Polygon
        tmp_filename = unique_filename(suffix='.shp')

        # Check that one single polygon works
        P = numpy.array([[106.79, -6.23],
                         [106.80, -6.24],
                         [106.78, -6.23],
                         [106.77, -6.21]])
        v = Vector(geometry=[P])
        assert v.is_polygon_data
        assert len(v) == 1

        v_ref = Vector(geometry=[P], geometry_type='polygon')
        assert v_ref.is_polygon_data
        assert len(v_ref) == 1

        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        for i in range(len(v_ref)):
            x = v_ref.get_geometry()[i]
            y = v_file.get_geometry()[i]
            msg = 'Read geometry %s, but expected %s' % (y, x)
            assert numpy.allclose(x, y), msg

        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_polygon_data
        assert v_file.geometry_type == 3

        # Then a more complex dataset
        test_data = [numpy.array([[122.226889, -8.625599],
                                  [122.227299, -8.624500],
                                  [122.227409, -8.624221],
                                  [122.227536, -8.624059]]),
                     numpy.array([[122.237129, -8.628637],
                                  [122.233170, -8.627332],
                                  [122.231621, -8.626837],
                                  [122.231021, -8.626557]]),
                     numpy.array([[122.247938, -8.632926],
                                  [122.247940, -8.633560],
                                  [122.247390, -8.636220]]),
                     numpy.array([[122.22, -8.6256],
                                  [122.23, -8.6245],
                                  [122.24, -8.6242],
                                  [122.22, -8.6240]]),
                     numpy.array([[122.24, -8.63],
                                  [122.23, -8.63],
                                  [122.23, -8.62],
                                  [122.23, -8.61]]),
                     numpy.array([[122.25, -8.63],
                                  [122.24, -8.633],
                                  [122.23, -8.64]])]

        # Point data
        v_ref = Vector(geometry=test_data[0])
        assert v_ref.is_point_data
        assert v_ref.geometry_type == 1
        data_bbox = v_ref.get_bounding_box()

        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_point_data
        assert v_file.geometry_type == 1
        assert numpy.allclose(v_file.get_bounding_box(), data_bbox,
                              rtol=1.0e-12, atol=1.0e-12)

        v = Vector(geometry=test_data[0], geometry_type='point')
        assert v.is_point_data
        # The layer is never been writen, so the keyword_version is missing
        v.keywords = v_ref.keywords
        assert v_ref == v

        v = Vector(geometry=test_data[0], geometry_type=1)
        assert v.is_point_data
        # The layer is never been writen, so the keyword_version is missing
        v.keywords = v_ref.keywords
        assert v_ref == v

        # Line data
        v_ref = Vector(geometry=test_data, geometry_type='line')
        assert v_ref.is_line_data
        assert v_ref.geometry_type == 2
        data_bbox = v_ref.get_bounding_box()

        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_line_data
        assert v_file.geometry_type == 2
        assert numpy.allclose(v_file.get_bounding_box(), data_bbox,
                              rtol=1.0e-12, atol=1.0e-12)

        v = Vector(geometry=test_data, geometry_type=2)
        # The layer is never been writen, so the keyword_version is missing
        v.keywords = v_ref.keywords
        assert v == v_ref

        # Polygon data
        v_ref = Vector(geometry=test_data)
        assert v_ref.is_polygon_data
        assert v_ref.geometry_type == 3
        data_bbox = v_ref.get_bounding_box()

        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        assert v_file == v_ref
        assert v_ref == v_file
        assert v_file.is_polygon_data
        assert v_file.geometry_type == 3
        assert numpy.allclose(v_file.get_bounding_box(), data_bbox,
                              rtol=1.0e-12, atol=1.0e-12)

        v = Vector(geometry=test_data, geometry_type='polygon')
        # The layer is never been writen, so the keyword_version is missing
        v.keywords = v_ref.keywords
        assert v == v_ref

        v = Vector(geometry=test_data, geometry_type=3)
        # The layer is never been writen, so the keyword_version is missing
        v.keywords = v_ref.keywords
        assert v == v_ref

    def test_polygons_with_inner_rings(self):
        """Polygons with inner rings can be written and read
        """

        # Define two (closed) outer rings - clock wise direction
        outer_rings = [numpy.array([[106.79, -6.233],
                                    [106.80, -6.24],
                                    [106.78, -6.23],
                                    [106.77, -6.21],
                                    [106.79, -6.233]]),
                       numpy.array([[106.76, -6.23],
                                    [106.72, -6.23],
                                    [106.72, -6.22],
                                    [106.72, -6.21],
                                    [106.76, -6.23]])]

        tmp_filename = unique_filename(suffix='.shp')

        # Do outer rings first (use default geometry type polygon)
        v_ref = Vector(geometry=outer_rings)
        assert v_ref.is_polygon_data

        v_ref.write_to_file(tmp_filename)
        v_file = read_layer(tmp_filename)
        assert v_file == v_ref
        assert v_file.is_polygon_data

        # Do it again but with (closed) inner rings as well

        # Define inner rings (counter clock wise)
        inner_rings = [
            # 2 rings for feature 0
            [numpy.array([[106.77827, -6.2252],
                          [106.77775, -6.22378],
                          [106.78, -6.22311],
                          [106.78017, -6.22530],
                          [106.77827, -6.2252]])[::-1],
             numpy.array([[106.78652, -6.23215],
                          [106.78642, -6.23075],
                          [106.78746, -6.23143],
                          [106.78831, -6.23307],
                          [106.78652, -6.23215]])[::-1]],
            # 1 ring for feature 1
            [numpy.array([[106.73709, -6.22752],
                          [106.73911, -6.22585],
                          [106.74265, -6.22814],
                          [106.73971, -6.22926],
                          [106.73709, -6.22752]])[::-1]]]

        polygons = []
        for i, outer_ring in enumerate(outer_rings):
            p = Polygon(outer_ring=outer_ring, inner_rings=inner_rings[i])
            polygons.append(p)

        v_ref = Vector(geometry=polygons)
        assert v_ref.is_polygon_data
        data_bbox = v_ref.get_bounding_box()

        # Check data from Vector object
        geometry = v_ref.get_geometry(as_geometry_objects=True)
        for i, g in enumerate(geometry):
            assert numpy.allclose(g.outer_ring, outer_rings[i])
            if i == 0:
                assert len(g.inner_rings) == 2
            else:
                assert len(g.inner_rings) == 1

            for j, ring in enumerate(inner_rings[i]):
                assert numpy.allclose(ring, g.inner_rings[j])

        # Write to file and read again
        v_ref.write_to_file(tmp_filename)
        # print 'With inner rings, written to ', tmp_filename
        v_file = read_layer(tmp_filename)
        assert v_file == v_ref
        assert v_file.is_polygon_data
        assert numpy.allclose(v_file.get_bounding_box(), data_bbox,
                              rtol=1.0e-12, atol=1.0e-12)

        # Check data from file
        geometry = v_file.get_geometry(as_geometry_objects=True)
        for i, g in enumerate(geometry):
            assert numpy.allclose(g.outer_ring, outer_rings[i])
            if i == 0:
                assert len(g.inner_rings) == 2
            else:
                assert len(g.inner_rings) == 1

            for j, ring in enumerate(inner_rings[i]):
                assert numpy.allclose(ring, g.inner_rings[j])

    def test_attribute_types(self):
        """Different attribute types are handled correctly in vector data
        """

        # Read a data file
        layername = 'test_buildings.shp'
        filename = '%s/%s' % (TESTDATA, layername)
        V = read_layer(filename)

        # Make a smaller dataset
        V_ref = V.get_topN('FLOOR_AREA', 5)

        geometry = V_ref.get_geometry()
        # data = V_ref.get_data()
        projection = V_ref.get_projection()

        # Create new attributes with a range of types
        keys = ['None', 'String', 'Boolean', 'Integer', 'Real',
                'Array 1D', 'Array 2D']
        values = [None, 'Test', True, 3, 3.14,
                  numpy.array([2.56]), numpy.array([[6.21]])]

        data = []
        for i in range(len(geometry)):
            D = {}
            for j, key in enumerate(keys):
                if key == 'Boolean':
                    # Add a little variation
                    if i % 2 == 0:
                        D[key] = not values[j]
                    else:
                        D[key] = values[j]
                else:
                    D[key] = values[j]
            data.append(D)

        # Create new object from test data
        v_new = Vector(data=data, projection=projection, geometry=geometry)

        # Write this new object, read it again and check
        tmp_filename = unique_filename(suffix='.shp')
        v_new.write_to_file(tmp_filename)

        v_tmp = read_layer(tmp_filename)

        assert v_tmp.projection == v_new.projection
        assert numpy.allclose(v_tmp.geometry, v_new.geometry)
        assert v_tmp.data == v_new.data
        assert v_tmp.get_data() == v_new.get_data()
        assert v_tmp == v_new
        assert not v_tmp != v_new

    def test_reading_and_writing_of_vector_polygon_data(self):
        """Vector polygon data can be read and written correctly
        """

        # Read and verify test data
        vectorname = 'kecamatan_jakarta_osm.shp'

        filename = '%s/%s' % (TESTDATA, vectorname)
        layer = read_layer(filename)
        geometry = layer.get_geometry()
        attributes = layer.get_data()

        assert layer.is_polygon_data

        # Check basic data integrity
        N = len(layer)

        assert len(geometry) == N
        assert len(attributes) == N
        assert len(attributes[0]) == 2

        assert FEATURE_COUNTS[vectorname] == N
        assert isinstance(layer.get_name(), basestring)

        # Check projection
        wkt = layer.get_projection(proj4=False)
        assert wkt.startswith('GEOGCS')

        assert layer.projection == Projection(DEFAULT_PROJECTION)

        # Check each polygon
        for i in range(N):
            geom = geometry[i]
            n = geom.shape[0]
            assert n >= 2
            assert geom.shape[1] == 2

            # Check that polygon is closed
            assert numpy.allclose(geom[0], geom[-1], rtol=0)

            # But that not all points are the same
            max_dist = 0
            for j in range(n):
                d = numpy.sum((geom[j] - geom[0]) ** 2) / n
                if d > max_dist:
                    max_dist = d
            assert max_dist > 0

        # Check integrity of each feature
        expected_features = {13: {'KAB_NAME': 'JAKARTA PUSAT',
                                  'KEC_NAME': 'SAWAH BESAR'},
                             20: {'KAB_NAME': 'JAKARTA SELATAN',
                                  'KEC_NAME': 'MAMPANG PRAPATAN'}}

        for i in range(N):
            # Consistency with attributes read manually with qgis

            if i in expected_features:
                att = attributes[i]
                exp = expected_features[i]

                for key in exp:
                    msg = ('Expected attribute %s was not found in feature %i'
                           % (key, i))
                    assert key in att, msg

                    a = att[key]
                    e = exp[key]
                    msg = 'Got %s: "%s" but expected "%s"' % (key, a, e)
                    assert a == e, msg

        # Write data back to file
        # FIXME (Ole): I would like to use gml here, but OGR does not
        #              store the spatial reference! Ticket #18
        out_filename = unique_filename(suffix='.shp')
        Vector(geometry=geometry, data=attributes, projection=wkt,
               geometry_type='polygon').write_to_file(out_filename)

        # Read again and check
        layer = read_layer(out_filename)
        assert layer.is_polygon_data
        geometry_new = layer.get_geometry()
        attributes_new = layer.get_data()

        N = len(layer)
        assert len(geometry_new) == N
        assert len(attributes_new) == N

        for i in range(N):
            assert numpy.allclose(geometry[i],
                                  geometry_new[i],
                                  rtol=1.0e-6)  # OGR works in single precision

            assert len(attributes_new[i]) == 2
            for key in attributes_new[i]:
                assert attributes_new[i][key] == attributes[i][key]

    test_reading_and_writing_of_vector_polygon_data.slow = True

    def test_centroids_from_polygon_data(self):
        """Centroid point data can be derived from polygon data

        Test against centroid data generated by QGIS: shapefiles with
        a _centroids.shp suffix.
        """

        for vectorname in ['kecamatan_jakarta_osm.shp',
                           'OSM_subset.shp']:

            # Read and verify test data
            filename = '%s/%s' % (TESTDATA, vectorname)
            p_layer = read_layer(filename)
            p_geometry = p_layer.get_geometry()
            p_attributes = p_layer.get_data()
            N = len(p_layer)
            assert FEATURE_COUNTS[vectorname] == N

            # Read reference centroids generated by Qgis
            filename = '%s/%s' % (TESTDATA, vectorname[:-4] + '_centroids.shp')
            r_layer = read_layer(filename)
            r_geometry = r_layer.get_geometry()
            r_attributes = r_layer.get_data()
            assert len(r_layer) == N

            # Compute centroid data
            c_layer = convert_polygons_to_centroids(p_layer)
            assert len(c_layer) == N
            c_geometry = c_layer.get_geometry()
            c_attributes = c_layer.get_data()

            # Check that attributes are the same
            for i in range(N):
                p_att = p_attributes[i]
                c_att = c_attributes[i]
                r_att = r_attributes[i]
                for key in p_att:
                    assert key in c_att
                    assert c_att[key] == p_att[key]

                    assert key in r_att
                    assert c_att[key] == r_att[key]

            # Check that coordinates are the same up to machine precision
            for i in range(N):
                c_geom = c_geometry[i]
                r_geom = r_geometry[i]

                assert numpy.allclose(c_geom, r_geom,
                                      rtol=1.0e-8, atol=1.0e-12)

            # Check that each centroid fall within its polygon
            for i in range(N):
                point = c_geometry[i]
                polygon = p_geometry[i]
                assert is_inside_polygon(point, polygon, closed=False)

            # Write to file (for e.g. visual inspection)
            out_filename = unique_filename(prefix='centroid', suffix='.shp')
            # print 'writing to', out_filename
            c_layer.write_to_file(out_filename)

    test_centroids_from_polygon_data.slow = True

    def test_rasters_and_arrays(self):
        """Consistency of rasters and associated arrays.
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes
        dlon = 1
        dlat = -1

        # Define array where latitudes are rows and longitude columns
        A1 = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        lon = numpy.linspace(lon_ll + 0.5, lon_ll + numlon - 0.5, numlon)
        lat = numpy.linspace(lat_ll + 0.5, lat_ll + numlat - 0.5, numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A1[numlat - 1 - i, j] = linear_function(lon[j], lat[i])

        # Throw in a nodata element
        A1[2, 6] = numpy.nan

        # Upper left corner
        assert A1[0, 0] == 105.25
        assert A1[0, 0] == linear_function(lon[0], lat[4])

        # Lower left corner
        assert A1[4, 0] == 103.25
        assert A1[4, 0] == linear_function(lon[0], lat[0])

        # Upper right corner
        assert A1[0, 7] == 112.25
        assert A1[0, 7] == linear_function(lon[7], lat[4])

        # Lower right corner
        assert A1[4, 7] == 110.25
        assert A1[4, 7] == linear_function(lon[7], lat[0])

        # Generate raster object and write
        projection = ('GEOGCS["WGS 84",'
                      'DATUM["WGS_1984",'
                      'SPHEROID["WGS 84",6378137,298.2572235630016,'
                      'AUTHORITY["EPSG","7030"]],'
                      'AUTHORITY["EPSG","6326"]],'
                      'PRIMEM["Greenwich",0],'
                      'UNIT["degree",0.0174532925199433],'
                      'AUTHORITY["EPSG","4326"]]')
        geotransform = (lon_ul, dlon, 0, lat_ul, 0, dlat)
        R1 = Raster(A1, projection, geotransform,
                    keywords={'keyword_version': '3.2', 'title': 'test'})

        # Check string representation of raster class
        assert str(R1).startswith('Raster data')
        assert str(R1.rows) in str(R1)
        assert str(R1.columns) in str(R1)

        # Test conversion between geotransform and
        # geometry (longitudes and latitudes)
        longitudes, latitudes = R1.get_geometry()
        msg = 'Longitudes not as expected: %s' % str(longitudes)
        assert numpy.allclose(longitudes, [100.5, 101.5, 102.5, 103.5, 104.5,
                                           105.5, 106.5, 107.5]), msg

        msg = 'Latitudes not as expected: %s' % str(latitudes)
        assert numpy.allclose(latitudes, [5.5, 6.5, 7.5, 8.5, 9.5]), msg

        gt = raster_geometry_to_geotransform(longitudes, latitudes)
        msg = ('Conversion from coordinates to geotransform failed: %s'
               % str(gt))
        assert numpy.allclose(gt, geotransform,
                              rtol=1.0e-12, atol=1.0e-12), msg

        msg = ('Dimensions of raster array do not match those of '
               'raster object')
        assert numlat == R1.rows, msg
        assert numlon == R1.columns, msg

        # Write back to new (tif) file
        out_filename = unique_filename(suffix='.tif')
        R1.write_to_file(out_filename)
        assert R1.filename == out_filename

        # Check nodata in original layer
        assert numpy.isnan(R1.get_nodata_value())

        # Read again and check consistency
        R2 = read_layer(out_filename)
        assert R2.filename == out_filename

        # Check nodata in read layer
        assert numpy.isnan(R2.get_nodata_value())

        msg = ('Dimensions of written raster array do not match those '
               'of input raster file\n')
        msg += ('    Dimensions of input file '
                '%s:  (%s, %s)\n' % (R1.filename, numlat, numlon))
        msg += ('    Dimensions of output file %s: '
                '(%s, %s)' % (R2.filename, R2.rows, R2.columns))

        assert numlat == R2.rows, msg
        assert numlon == R2.columns, msg

        A2 = R2.get_data()

        assert numpy.allclose(numpy.nanmin(A1), numpy.nanmin(A2))
        assert numpy.allclose(numpy.nanmax(A1), numpy.nanmax(A2))

        msg = 'Array values of written raster array were not as expected'
        assert nan_allclose(A1, A2), msg

        msg = 'Geotransforms were different'
        assert R1.get_geotransform() == R2.get_geotransform(), msg

        p1 = R1.get_projection(proj4=True)
        p2 = R2.get_projection(proj4=True)
        msg = 'Projections were different: %s != %s' % (p1, p2)
        assert p1 == p1, msg

        # Exercise projection __eq__ method
        assert R1.projection == R2.projection

        # Check that equality raises exception when type is wrong
        try:
            R1.projection == 234
        except TypeError:
            print 'You can ignore the ERROR 1 message it is intentional - Tim'
        else:
            msg = 'Should have raised TypeError'
            raise Exception(msg)

        # Check keywords
        # Need to set this since we always use the latest version.
        R2.keywords['keyword_version'] = R1.keywords['keyword_version']
        self.assertEqual(R1.keywords, R2.keywords)

        # Check override of ==
        assert R1 == R2

    def test_rasters_created_with_projected_srs(self):
        """Rasters can be created from arrays in projected coordinates
        """

        # Create test data
        x_ul = 220534  # x value of upper left corner
        y_ul = 827790   # y_value of upper left corner
        numx = 8    # Number of xs
        numy = 5    # Number of ys
        dx = 200
        dy = -200

        # Define array where ys are rows and xs columns
        A1 = numpy.zeros((numy, numx))

        # Establish coordinates for lower left corner
        y_ll = y_ul - numy * dy
        x_ll = x_ul

        # Define pixel centers along each direction
        x = numpy.linspace(x_ll + 0.5, x_ll + numx - 0.5, numx)
        y = numpy.linspace(y_ll + 0.5, y_ll + numy - 0.5, numy)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numy):
            for j in range(numx):
                A1[numy - 1 - i, j] = linear_function(x[j], y[i])

        # Throw in a nodata element
        A1[2, 6] = numpy.nan

        # Upper left corner
        assert A1[0, 0] == linear_function(x[0], y[4])

        # Lower left corner
        assert A1[4, 0] == linear_function(x[0], y[0])

        # Upper right corner
        assert A1[0, 7] == linear_function(x[7], y[4])

        # Lower right corner
        assert A1[4, 7] == linear_function(x[7], y[0])

        # Generate raster object and write
        projection = """PROJCS["DGN95 / Indonesia TM-3 zone 48.2",
                        GEOGCS["DGN95",
                            DATUM["Datum_Geodesi_Nasional_1995",
                                SPHEROID["WGS 84",6378137,298.257223563,
                                    AUTHORITY["EPSG","7030"]],
                                TOWGS84[0,0,0,0,0,0,0],
                                AUTHORITY["EPSG","6755"]],
                            PRIMEM["Greenwich",0,
                                AUTHORITY["EPSG","8901"]],
                            UNIT["degree",0.01745329251994328,
                                AUTHORITY["EPSG","9122"]],
                            AUTHORITY["EPSG","4755"]],
                        UNIT["metre",1,
                            AUTHORITY["EPSG","9001"]],
                        PROJECTION["Transverse_Mercator"],
                        PARAMETER["latitude_of_origin",0],
                        PARAMETER["central_meridian",106.5],
                        PARAMETER["scale_factor",0.9999],
                        PARAMETER["false_easting",200000],
                        PARAMETER["false_northing",1500000],
                        AUTHORITY["EPSG","23834"],
                        AXIS["X",EAST],
                        AXIS["Y",NORTH]]"""

        geotransform = (x_ul, dx, 0, y_ul, 0, dy)
        r1 = Raster(A1, projection, geotransform,
                    keywords={'testkwd': 'testval', 'size': 'small'})

        # Check string representation of raster class
        assert str(r1).startswith('Raster data')
        assert str(r1.rows) in str(r1)
        assert str(r1.columns) in str(r1)

        assert nan_allclose(r1.get_data(), A1, rtol=1.0e-12)
        assert nan_allclose(r1.get_geotransform(), geotransform, rtol=1.0e-12)
        assert 'DGN95' in r1.get_projection()

    def test_reading_and_writing_of_real_rasters(self):
        """Rasters can be read and written correctly in different formats
        """
        raster_names = [
            'Earthquake_Ground_Shaking_clip.tif',
            'Population_2010_clip.tif',
            'shakemap_padang_20090930.asc',
            'population_padang_1.asc',
            'population_padang_2.asc'
        ]

        for raster in raster_names:
            filename = '%s/%s' % (TESTDATA, raster)
            r1 = read_layer(filename)
            assert r1.filename == filename

            # Check consistency of raster
            a1 = r1.get_data()
            m, n = a1.shape

            msg = ('Dimensions of raster array do not match those of '
                   'raster file %s' % r1.filename)
            assert m == r1.rows, msg
            assert n == r1.columns, msg

            # Test conversion between geotransform and
            # geometry (longitudes and latitudes)
            # pylint: disable=unbalanced-tuple-unpacking
            # pylint: disable=unpacking-non-sequence
            longitudes, latitudes = r1.get_geometry()
            # pylint: enable=unbalanced-tuple-unpacking
            # pylint: enable=unpacking-non-sequence
            gt = raster_geometry_to_geotransform(longitudes, latitudes)
            msg = ('Conversion from coordinates to geotransform failed: %s'
                   % str(gt))
            assert numpy.allclose(gt, r1.get_geotransform(),
                                  rtol=1.0e-12, atol=1.0e-12), msg

            # Write back to new file
            for ext in ['.tif']:  # Would like to also have , '.asc']:
                out_filename = unique_filename(suffix=ext)
                write_raster_data(
                    a1,
                    r1.get_projection(),
                    r1.get_geotransform(),
                    out_filename,
                    keywords=r1.keywords)

                # Read again and check consistency
                r2 = read_layer(out_filename)
                assert r2.filename == out_filename

                msg = ('Dimensions of written raster array do not match those '
                       'of input raster file\n')
                msg += ('    Dimensions of input file '
                        '%s:  (%s, %s)\n' % (r1.filename, m, n))
                msg += ('    Dimensions of output file %s: '
                        '(%s, %s)' % (r2.filename, r2.rows, r2.columns))

                assert m == r2.rows, msg
                assert n == r2.columns, msg

                a2 = r2.get_data()

                assert numpy.allclose(numpy.nanmin(a1), numpy.nanmin(a2))
                assert numpy.allclose(numpy.nanmax(a1), numpy.nanmax(a2))

                msg = ('Array values of written raster array were not as '
                       'expected')
                assert nan_allclose(a1, a2), msg

                msg = 'Geotransforms were different'
                assert r1.get_geotransform() == r2.get_geotransform(), msg

                p1 = r1.get_projection(proj4=True)
                p2 = r2.get_projection(proj4=True)
                msg = 'Projections were different: %s != %s' % (p1, p2)
                assert p1 == p1, msg

                # Need to set this since we always use the latest version.
                r2.keywords['keyword_version'] = r1.keywords['keyword_version']
                self.assertEqual(r1.keywords, r2.keywords)

                # Use overridden == and != to verify
                assert r1 == r2
                assert not r1 != r2

                # Check equality within tolerance
                r3 = r1.copy()

                r3.data[-1, -1] += 1.0e-5  # This is within tolerance
                assert r1 == r3

                r3.data[-1, -1] += 1.0e-2  # This is outside tolerance
                assert r1 != r3

                # Check that equality raises exception when type is wrong
                try:
                    r1 == Vector()
                except TypeError:
                    pass
                else:
                    msg = 'Should have raised TypeError'
                    raise Exception(msg)

    test_reading_and_writing_of_real_rasters.slow = True

    def test_no_projection(self):
        """Raster layers with no projection causes Exception to be raised
        """

        rastername = 'grid_without_projection.asc'
        filename = '%s/%s' % (TESTDATA, rastername)
        try:
            read_layer(filename)
        except RuntimeError:
            pass
        else:
            msg = 'Should have raised RuntimeError'
            raise Exception(msg)

    def test_bad_ascii_data(self):
        """ASC raster files with bad data causes good error message

        This example is courtesy of Hyeuk Ryu
        """

        # Bad file
        asc_filename = os.path.join(TESTDATA, 'bad_ascii_format.asc')
        try:
            read_layer(asc_filename)
        except ReadLayerError, e:
            # Check that error message is reasonable, e.g.
            # File /home/nielso/sandpit/inasafe_data/test/bad_ascii_format.asc
            # exists, but could not be read. Please check if the file can
            # be opened with e.g. qgis or gdalinfo

            msg = 'Unexpected error message for corrupt asc file: %s' % e
            assert 'exists' in str(e), msg
            assert 'gdalinfo' in str(e), msg
            assert 'qgis' in str(e), msg
            assert 'Please' in str(e), msg

        # No file
        asc_filename = 'nonexisting_ascii_file_234xxxlcrhgqjk.asc'
        try:
            read_layer(asc_filename)
        except ReadLayerError, e:
            # Check that this error message reflects that file did not exist
            msg = 'Unexpected error message for non existing asc file: %s' % e
            assert 'Could not find file' in str(e), msg

    test_bad_ascii_data.slow = True

    def test_nodata_value(self):
        """NODATA value is correctly handled for GDAL layers
        """

        # Read files with -9999 as nominated nodata value
        for filename in [os.path.join(TESTDATA, 'Population_2010_clip.tif'),
                         os.path.join(HAZDATA,
                                      'Lembang_Earthquake_Scenario.asc'),
                         os.path.join(TESTDATA,
                                      'Earthquake_Ground_Shaking.asc')]:

            R = read_layer(filename)
            A = R.get_data(nan=True)

            # Verify nodata value
            amin = numpy.nanmin(A.flat[:])
            msg = ('True raster minimum must exceed -9999. '
                   'We got %f for file %s' % (amin, filename))
            assert amin > -9999, msg

            # Then try with a number
            A = R.get_data(nan=-100000)

            # Verify nodata value
            amin = numpy.nanmin(A.flat[:])
            msg = ('Raster must have -100000 as its minimum for this test. '
                   'We got %f for file %s' % (amin, filename))
            assert amin == -100000, msg

            # Try with illegal nan values
            for illegal in [{}, (), [], None, 'a', 'oeuu']:
                try:
                    R.get_data(nan=illegal)
                except InaSAFEError:
                    pass
                else:
                    msg = ('Illegal nan value %s should have raised '
                           'exception' % illegal)
                    raise RuntimeError(msg)

    test_nodata_value.slow = True

    def test_vector_extrema(self):
        """Vector extremum calculation works
        """

        for layername in ['test_buildings.shp',
                          'tsunami_building_exposure.shp']:

            filename = '%s/%s' % (TESTDATA, layername)
            L = read_layer(filename)

            if layername == 'tsunami_building_exposure.shp':
                attributes = L.get_data()

                for name in ['STR_VALUE', 'CONT_VALUE']:
                    minimum, maximum = L.get_extrema(name)
                    assert minimum <= maximum

                    x = [a[name] for a in attributes]
                    assert numpy.allclose([min(x), max(x)],
                                          [minimum, maximum],
                                          rtol=1.0e-12, atol=1.0e-12)

            elif layername == 'test_buildings.shp':
                minimum, maximum = L.get_extrema('FLOOR_AREA')
                assert minimum == maximum  # All identical
                assert maximum == 250

                try:
                    L.get_extrema('NONEXISTING_ATTRIBUTE_NAME_8462')
                except VerificationError:
                    pass
                else:
                    msg = ('Non existing attribute name should have '
                           'raised VerificationError')
                    raise Exception(msg)

                try:
                    L.get_extrema()
                except RuntimeError:
                    pass
                else:
                    msg = ('Missing attribute name should have '
                           'raised RuntimeError')
                    raise Exception(msg)

    def test_raster_extrema(self):
        """Raster extrema (including NAN's) are correct.
        """

        for rastername in ['Earthquake_Ground_Shaking_clip.tif',
                           'Population_2010_clip.tif',
                           'shakemap_padang_20090930.asc',
                           'population_padang_1.asc',
                           'population_padang_2.asc']:

            filename = '%s/%s' % (TESTDATA, rastername)
            R = read_layer(filename)

            # Check consistency of raster

            # Use numpy to establish the extrema instead of gdal
            minimum, maximum = R.get_extrema()

            # Check that arrays with NODATA value replaced by NaN's agree
            a = R.get_data(nan=False)
            b = R.get_data(nan=True)

            assert a.dtype == b.dtype
            assert numpy.nanmax(a - b) == 0
            assert numpy.nanmax(b - a) == 0
            assert numpy.nanmax(numpy.abs(a - b)) == 0

            # Check that extrema are OK
            assert numpy.allclose(maximum, numpy.nanmax(a[:]))
            assert numpy.allclose(maximum, numpy.nanmax(b[:]))
            assert numpy.allclose(minimum, numpy.nanmin(b[:]))

            # Check that nodata can be replaced by 0.0
            c = R.get_data(nan=0.0)
            msg = '-9999 should have been replaced by 0.0 in %s' % rastername
            assert min(c.flat[:]) != -9999, msg

    test_raster_extrema.slow = True

    def test_bins(self):
        """Linear and quantile bins are correct
        """

        for filename in ['%s/population_padang_1.asc' % TESTDATA,
                         '%s/test_grid.asc' % TESTDATA]:

            R = read_layer(filename)
            rmin, rmax = R.get_extrema()

            for N in [2, 3, 5, 7, 10, 16]:
                linear_intervals = R.get_bins(N=N, quantiles=False)

                assert linear_intervals[0] == rmin
                assert linear_intervals[-1] == rmax

                d = (rmax - rmin) / N
                for i in range(N):
                    assert numpy.allclose(linear_intervals[i], rmin + i * d)

                quantiles = R.get_bins(N=N, quantiles=True)
                A = R.get_data(nan=True).flat[:]

                mask = numpy.logical_not(numpy.isnan(A))  # Omit NaN's
                l1 = len(A)
                A = A.compress(mask)
                l2 = len(A)

                if filename == '%s/test_grid.asc' % TESTDATA:
                    # Check that NaN's were removed
                    assert l1 == 35
                    assert l2 == 30

                # Assert that there are no NaN's
                assert not numpy.alltrue(numpy.isnan(A))

                number_of_elements = len(A)
                average_elements_per_bin = number_of_elements / N

                # Count elements in each bin and check
                i0 = quantiles[0]
                for i1 in quantiles[1:]:
                    count = numpy.sum((i0 < A) & (A < i1))
                    if i0 == quantiles[0]:
                        refcount = count

                    if i1 < quantiles[-1]:
                        # Number of elements in each bin must vary by no
                        # more than 1
                        assert abs(count - refcount) <= 1
                        assert abs(count - average_elements_per_bin) <= 3
                    else:
                        # The last bin is allowed vary by more
                        pass

                    i0 = i1

    test_bins.slow = True

    def test_raster_to_vector_points(self):
        """Raster layers can be converted to vector point layers
        """

        filename = '%s/test_grid.asc' % TESTDATA
        R = read_layer(filename)

        # Check data directly
        # pylint: disable=unbalanced-tuple-unpacking
        coordinates, values = R.to_vector_points()
        # pylint: disable=unbalanced-tuple-unpacking
        # pylint: disable=unpacking-non-sequence
        longitudes, latitudes = R.get_geometry()
        # pylint: enable=unbalanced-tuple-unpacking
        # pylint: enable=unpacking-non-sequence
        a = R.get_data()
        M, N = a.shape
        L = M * N

        assert numpy.allclose(coordinates[:N, 0], longitudes)
        assert numpy.allclose(coordinates[:L:N, 1], latitudes[::-1])
        assert nan_allclose(a.flat[:], values)

        # Generate vector layer
        V = R.to_vector_layer()
        geometry = V.get_geometry()
        msg = ('Vector geometry should have been a list. I got %s' % str(
            type(geometry))[1:-1])
        assert isinstance(geometry, list), msg
        attributes = V.get_data()

        # Store it for visual inspection e.g. with QGIS
        # out_filename = unique_filename(suffix='.shp')
        # V.write_to_file(out_filename)

        # Check against cells that were verified manually using QGIS
        assert numpy.allclose(geometry[5], [96.97137053, -5.34965715])
        assert numpy.allclose(attributes[5]['value'], 3)
        assert numpy.allclose(attributes[5]['value'], a[1, 0])

        assert numpy.allclose(geometry[11], [97.0021116, -5.38039821])
        assert numpy.allclose(attributes[11]['value'], -50.6014, rtol=1.0e-6)
        assert numpy.allclose(attributes[11]['value'], a[2, 1], rtol=1.0e-6)

        assert numpy.allclose(geometry[16], [97.0021116, -5.411139276])
        assert numpy.allclose(attributes[16]['value'], -15, rtol=1.0e-6)
        assert numpy.allclose(attributes[16]['value'], a[3, 1], rtol=1.0e-6)

        assert numpy.allclose(geometry[23], [97.06359372, -5.44188034])
        assert numpy.isnan(attributes[23]['value'])
        assert numpy.isnan(a[4, 3])

    def test_raster_to_vector_points2(self):
        """Raster layers can be converted to vector point layers (real data)

        # See qgis project in test data: raster_point_and_clipping_test.qgs
        """

        filename = '%s/population_5x5_jakarta.asc' % TESTDATA
        R = read_layer(filename)

        # Check data directly
        # pylint: disable=unbalanced-tuple-unpacking
        coordinates, values = R.to_vector_points()
        # pylint: disable=unbalanced-tuple-unpacking
        # pylint: disable=unpacking-non-sequence
        longitudes, latitudes = R.get_geometry()
        # pylint: enable=unbalanced-tuple-unpacking
        # pylint: enable=unpacking-non-sequence
        A = R.get_data()
        M, N = A.shape
        L = M * N

        assert numpy.allclose(coordinates[:N, 0], longitudes)
        assert numpy.allclose(coordinates[:L:N, 1], latitudes[::-1])
        assert nan_allclose(A.flat[:], values)

        # Generate vector layer
        V = R.to_vector_layer()
        geometry = V.get_geometry()
        attributes = V.get_data()

        # Store it for visual inspection e.g. with QGIS
        # out_filename = unique_filename(suffix='.shp')
        # V.write_to_file(out_filename)

        # Systematic check of all cells
        i = 0
        for m, lat in enumerate(latitudes[::-1]):  # Start from bottom
            for n, lon in enumerate(longitudes):  # The fastest varying dim

                # Test location
                x = geometry[i]
                y = [lon, lat]
                msg = 'Got %s but expected %s' % (x, y)
                assert numpy.allclose(x, y), msg

                # Test value
                assert numpy.allclose(attributes[i]['value'],
                                      A[m, n], rtol=1.0e-6)

                i += 1

    def test_get_bounding_box(self):
        """Bounding box is correctly extracted from file.

        Reference data::

            gdalinfo Earthquake_Ground_Shaking_clip.tif
            Driver: GTiff/GeoTIFF
            Files: Earthquake_Ground_Shaking_clip.tif
            Size is 345, 263
            Coordinate System is:
            GEOGCS["WGS 84",
                DATUM["WGS_1984",
                    SPHEROID["WGS 84",6378137,298.2572235630016,
                        AUTHORITY["EPSG","7030"]],
                    AUTHORITY["EPSG","6326"]],
                PRIMEM["Greenwich",0],
                UNIT["degree",0.0174532925199433],
                AUTHORITY["EPSG","4326"]]
            Origin = (99.364169565217395,-0.004180608365019)
            Pixel Size = (0.008339130434783,-0.008361216730038)
            Metadata:
            AREA_OR_POINT=Point
            TIFFTAG_XRESOLUTION=1
            TIFFTAG_YRESOLUTION=1
            TIFFTAG_RESOLUTIONUNIT=1 (unitless)
            Image Structure Metadata:
            COMPRESSION=LZW
            INTERLEAVE=BAND
            Corner Coordinates:
            Upper Left  (  99.3641696,  -0.0041806)
                        ( 99d21'51.01"E,  0d 0'15.05"S)
            Lower Left  (  99.3641696,  -2.2031806)
                        ( 99d21'51.01"E,  2d12'11.45"S)
            Upper Right ( 102.2411696,  -0.0041806)
                        (102d14'28.21"E,  0d 0'15.05"S)
            Lower Right ( 102.2411696,  -2.2031806)
                        (102d14'28.21"E,  2d12'11.45"S)
            Center      ( 100.8026696,  -1.1036806)
                        (100d48'9.61"E,  1d 6'13.25"S)
            Band 1 Block=256x256 Type=Float64, ColorInterp=Gray


        Note post gdal 1.8 it is::
            Upper Left  (  99.3600000,   0.0000000)
                        ( 99d21'36.00"E,  0d 0' 0.01"N)
            Lower Left  (  99.3600000,  -2.1990000)
                        ( 99d21'36.00"E,  2d11'56.40"S)
            Upper Right ( 102.2370000,   0.0000000)
                        (102d14'13.20"E,  0d 0' 0.01"N)
            Lower Right ( 102.2370000,  -2.1990000)
                        (102d14'13.20"E,  2d11'56.40"S)
            Center      ( 100.7985000,  -1.0995000)
                        (100d47'54.60"E,  1d 5'58.20"S)
        """

        # Note there are two possible correct values of bbox depending on
        # the version of gdal:
        # http://trac.osgeo.org/gdal/wiki/rfc33_gtiff_pixelispoint

        # Get gdal version number
        x = gdal.VersionInfo('').replace('dev', '').split()
        y = x[1].split('.')[:2]
        z = ''.join(y)  # Turn into number and
        if z.endswith(','):
            z = z[:-1]  # Remove trailing comma

        # Reference bbox for vector data
        ref_bbox = {'tsunami_building_exposure.shp': [150.15238387897742,
                                                      -35.71084183517241,
                                                      150.18779267086208,
                                                      -35.70131768155173]}

        # Select correct reference bbox for rasters
        if float(z) < 17:
            ref_bbox['Earthquake_Ground_Shaking_clip.tif'] = [99.3641696,
                                                              -2.2031806,
                                                              102.2411696,
                                                              -0.0041806]
        else:
            ref_bbox['Earthquake_Ground_Shaking_clip.tif'] = [99.36,
                                                              -2.199,
                                                              102.237,
                                                              0.0]

        for filename in ['Earthquake_Ground_Shaking_clip.tif',
                         'tsunami_building_exposure.shp']:
            abspath = os.path.join(TESTDATA, filename)
            bbox = get_bounding_box(abspath)
            msg = ('Got bbox %s from filename %s, but expected %s '
                   % (str(bbox), filename, str(ref_bbox[filename])))
            assert numpy.allclose(bbox, ref_bbox[filename]), msg

            # Check the conversions
            bbox_string = bboxlist2string(bbox)

            # Check the check :-)
            check_bbox_string(bbox_string)

            # Check that it works for layer objects instantiated from file
            L = read_layer(abspath)
            L_bbox = L.get_bounding_box()
            msg = ('Got bbox %s from filename %s, but expected %s '
                   % (str(L_bbox), filename, str(ref_bbox[filename])))
            assert numpy.allclose(L_bbox, ref_bbox[filename]), msg

            # Check that it works for layer objects instantiated from data
            if L.is_raster:
                D = Raster(data=L.get_data(),
                           projection=L.get_projection(),
                           geotransform=L.get_geotransform())
            elif L.is_vector:
                D = Vector(data=L.get_data(),
                           projection=L.get_projection(),
                           geometry=L.get_geometry())
            else:
                msg = 'Unexpected layer object: %s' % str(L)
                raise RuntimeError(msg)

            # Check that get_bounding_box works for data instantiated layers
            D_bbox = D.get_bounding_box()
            msg = ('Got bbox %s from layer %s, but expected %s '
                   % (str(D_bbox), str(D), str(L_bbox)))
            assert numpy.allclose(D_bbox, L_bbox), msg

    def test_layer_API(self):
        """Vector and Raster instances have a similar API
        """

        # Exceptions
        exclude = [
            'get_topN', 'get_bins', 'get_geotransform', 'get_nodata_value',
            'get_attribute_names', 'get_resolution', 'get_geometry_type',
            'get_geometry_name', 'to_vector_points', 'to_vector_layer',
            'as_qgis_native',  # added in InaSAFE 2.0
            'read_from_qgis_native'  # added in InaSAFE 2.0
        ]

        V = Vector()  # Empty vector instance
        R = Raster()  # Empty raster instance

        assert same_API(V, R, exclude=exclude)

        for filename in [os.path.join(TESTDATA,
                                      'test_buildings.shp'),
                         os.path.join(HAZDATA,
                                      'Lembang_Earthquake_Scenario.asc')]:

            L = read_layer(filename)

            assert same_API(L, V, exclude=exclude)
            assert same_API(L, R, exclude=exclude)

    def test_keywords_file(self):
        """Keywords can be written and read
        """

        kwd_filename = unique_filename(suffix='.keywords')
        keywords = {'impact_summary': 'Describing the layer',
                    'category': 'impact',
                    'subcategory': 'flood',
                    'layer': None,
                    'kw': 'with:colon',
                    'with spaces': 'trailing_ws ',
                    ' preceding_ws': ' mixed spaces ',
                    'number': 31,
                    'a_float ': 13.42,
                    'a_tuple': (1, 4, 'a'),
                    'a_list': [2, 5, 'b'],
                    'a_dict': {'I': 'love', 'cheese': 'cake', 'number': 5},
                    'a_nested_thing': [2, {'k': 17.8}, 'b', (1, 2)],
                    'an_expression': '37 + 5',  # Evaluate to '37 + 5', not 42
                    # Potentially dangerous - e.g. if calling rm
                    'dangerous': '__import__("os").system("ls -l")',
                    'yes': True,
                    'no': False}

        write_keywords(keywords, kwd_filename)
        msg = 'Keywords file %s was not created' % kwd_filename
        assert os.path.isfile(kwd_filename), msg

        fid = open(kwd_filename)
        for line in fid.readlines():
            fields = line.split(':')

            k = fields[0]
            v = ':'.join(fields[1:])

            msg = 'Did not find keyword "%s" in %s' % (k, keywords.keys())
            assert k in keywords, msg

            msg = 'Got value "%s", expected "%s"' % (v.strip(),
                                                     str(keywords[k]).strip())
            assert v.strip() == str(keywords[k]).strip(), msg
        fid.close()

        x = read_keywords(kwd_filename)
        os.remove(kwd_filename)

        assert isinstance(x, dict)

        # Check keyword names
        for key in x:
            msg = 'Read unexpected key %s' % key
            assert key in keywords, msg

        for key in keywords:
            msg = 'Expected key %s was not read from %s' % (key,
                                                            kwd_filename)
            assert key in x, msg

        # Check keyword values
        for key in keywords:
            refval = keywords[key]  # Expected value
            newval = x[key]  # Value from keywords file

            # Catch all - comparing string reprentations
            msg = ('Expected value "%s" was not read from "%s". '
                   'I got "%s"' % (refval, kwd_filename, newval))
            assert str(refval).strip() == str(newval), msg

            # Check None
            if refval is None:
                assert newval is None

            # Check Booleans - explicitly
            if refval is True:
                assert newval is True

            if refval is False:
                assert newval is False

            # Check equality of python structures
            if not isinstance(refval, basestring):
                msg = 'Expected %s but got %s' % (refval, newval)
                assert newval == refval, msg

        # Check catching wrong extensions
        kwd_filename = unique_filename(suffix='.xxxx')
        try:
            write_keywords(keywords, kwd_filename)
        except VerificationError:
            pass
        else:
            msg = 'Should have raised assertion error for wrong extension'
            raise Exception(msg)

        # Make a spatial layer with these keywords
        V = read_layer('%s/test_buildings.shp' % TESTDATA)
        V = Vector(data=V.get_data(),
                   geometry=V.get_geometry(),
                   projection=V.get_projection(),
                   keywords=keywords)
        assert keywords['impact_summary'] == V.get_impact_summary()
        for key, val in V.get_keywords().items():
            msg = ('Expected keywords[%s] to be "%s" but '
                   'got "%s"' % (key, keywords[key], val))

            assert keywords[key] == val, msg
            # if key in [' preceding_ws', 'with spaces']:
            #    # Accept that surrounding whitespace may be stripped
            #    assert keywords[key].strip() == val, msg
            # else:
            #    assert keywords[key] == val, msg

    def test_empty_keywords_file(self):
        """Empty keywords can be handled
        """

        kwd_filename = unique_filename(suffix='.keywords')
        write_keywords({}, kwd_filename)

        msg = 'Keywords file %s was not created' % kwd_filename
        assert os.path.isfile(kwd_filename), msg

        x = read_keywords(kwd_filename)
        os.remove(kwd_filename)

        assert isinstance(x, dict)
        assert len(x) == 0

    def test_keywords_with_colon(self):
        """Keywords and values with colons raise error messages
        """

        # Colon in key
        kwd_filename = unique_filename(suffix='.keywords')
        keywords = {'with_a_colon:in_it': 'value'}  # This one is illegal

        try:
            write_keywords(keywords, kwd_filename)
        except VerificationError:
            pass
        else:
            msg = 'Colon in keywords key %s was not caught' % keywords
            raise Exception(msg)

        # Colon in value
        kwd_filename = unique_filename(suffix='.keywords')
        keywords = {'with_a_colon': 'take: that!'}  # This one is ok
        k = 'with_a_colon'

        write_keywords(keywords, kwd_filename)
        x = read_keywords(kwd_filename)
        assert k in x.keys()
        assert x[k] == keywords[k]

    def test_bounding_box_conversions(self):
        """Bounding boxes can be converted between list and string
        """

        # Good ones
        for x in [[105, -7, 108, -5],
                  [106.5, -6.5, 107, -6],
                  [94.972335, -11.009721, 141.014, 6.073612333333],
                  [105.3, -8.5, 110.0, -5.5],
                  [105.6, -7.8, 110.5, -5.1]]:
            bbox_string = bboxlist2string(x)
            bbox_list = bboxstring2list(bbox_string)

            assert numpy.allclose(x, bbox_list, rtol=1.0e-6, atol=1.0e-6)

        for x in ['105,-7,108,-5',
                  '106.5, -6.5, 107,-6',
                  '94.972335,-11.009721,141.014,6.073612333333']:
            bbox_list = bboxstring2list(x)

            # Check that numbers are numerically consistent
            assert numpy.allclose([float(z) for z in x.split(',')],
                                  bbox_list, rtol=1.0e-6, atol=1.0e-6)

        # Bad ones
        for bbox in [[105, -7, 'x', -5],
                     [106.5, -6.5, -6],
                     [94.972335, 0, -11.009721, 141.014, 6]]:
            try:
                bbox_string = bboxlist2string(bbox)
            except BoundingBoxError:
                pass
            else:
                msg = 'Should have raised BoundingBoxError'
                raise Exception(msg)

        for x in ['106.5,-6.5,-6',
                  '106.5,-6.5,-6,4,10',
                  '94.972335,x,141.014,6.07']:
            try:
                bbox_list = bboxstring2list(x)
            except BoundingBoxError:
                pass
            else:
                msg = 'Should have raised exception: %s' % x
                raise Exception(msg)

    def test_bounding_box_intersection(self):
        """Intersections of bounding boxes work
        """

        west_java = [105, -7, 108, -5]
        jakarta = [106.5, -6.5, 107, -6]

        # Test commutative law
        assert numpy.allclose(bbox_intersection(west_java, jakarta),
                              bbox_intersection(jakarta, west_java))

        # Test inclusion
        assert numpy.allclose(bbox_intersection(west_java, jakarta), jakarta)

        # Ignore Bounding Boxes that are None
        assert numpy.allclose(
            bbox_intersection(west_java, jakarta, None),
            jakarta)

        # Realistic ones
        bbox1 = [94.972335, -11.009721, 141.014, 6.073612333333]
        bbox2 = [105.3, -8.5, 110.0, -5.5]
        bbox3 = [105.6, -7.8, 110.5, -5.1]

        ref1 = [max(bbox1[0], bbox2[0]),
                max(bbox1[1], bbox2[1]),
                min(bbox1[2], bbox2[2]),
                min(bbox1[3], bbox2[3])]
        assert numpy.allclose(bbox_intersection(bbox1, bbox2), ref1)
        assert numpy.allclose(bbox_intersection(bbox1, bbox2), bbox2)

        ref2 = [max(bbox3[0], bbox2[0]),
                max(bbox3[1], bbox2[1]),
                min(bbox3[2], bbox2[2]),
                min(bbox3[3], bbox2[3])]
        assert numpy.allclose(bbox_intersection(bbox3, bbox2), ref2)
        assert numpy.allclose(bbox_intersection(bbox2, bbox3), ref2)

        # Multiple boxes
        assert numpy.allclose(bbox_intersection(bbox1, bbox2, bbox3),
                              bbox_intersection(ref1, ref2))

        assert numpy.allclose(bbox_intersection(bbox1, bbox2, bbox3,
                                                west_java, jakarta),
                              jakarta)

        # From actual example
        b1 = [94.972335000000001, -11.009721000000001,
              141.014002, 6.0736119999999998]
        b2 = (95.059660952000002, -10.997409961000001,
              141.00132578099999, 5.9109226959999983)
        b3 = (94.972335000000001, -11.009721000000001,
              141.0140016666665, 6.0736123333332639)

        res = bbox_intersection(b1, b2, b3)
        assert numpy.allclose(res, [95.059660952, -10.997409961,
                                    141.001325781, 5.910922695999998],
                              rtol=1.0e-12, atol=1.0e-12)

        # Empty intersection should return None
        assert bbox_intersection(bbox2, [50, 2, 53, 4]) is None

        # Deal with invalid boxes
        try:
            bbox_intersection(bbox1, [53, 2, 40, 4])
        except BoundingBoxError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            bbox_intersection(bbox1, [50, 7, 53, 4])
        except BoundingBoxError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            bbox_intersection(bbox1, 'blko ho skrle')
        except BoundingBoxError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            bbox_intersection(bbox1)
        except VerificationError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            bbox_intersection('')
        except VerificationError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

        try:
            bbox_intersection()
        except VerificationError:
            pass
        else:
            msg = 'Should have raised exception'
            raise Exception(msg)

    def test_minimal_bounding_box(self):
        """Bounding box minimal size can be controlled
        """

        big = (95.06, -11.0, 141.0, 5.9)
        mid = [103.28, -8.46, 109.67, -4.68]
        sml = (106.818998, -6.18585170, 106.82264510, -6.1810)

        min_res = 0.008333333333000
        eps = 1.0e-4

        # Check that sml box is actually too small
        assert sml[2] - sml[0] < min_res
        assert sml[3] - sml[1] < min_res

        for bbox in [big, mid, sml]:
            # Calculate minimal bounding box
            adjusted_bbox = minimal_bounding_box(bbox, min_res, eps=eps)

            # Check that adjusted box exceeds minimal resolution
            assert adjusted_bbox[2] - adjusted_bbox[0] > min_res
            assert adjusted_bbox[3] - adjusted_bbox[1] > min_res

            # Check that if box was adjusted eps was applied
            if bbox[2] - bbox[0] <= min_res:
                assert numpy.allclose(adjusted_bbox[2] - adjusted_bbox[0],
                                      min_res + (2 * eps))

            if bbox[3] - bbox[1] <= min_res:
                assert numpy.allclose(adjusted_bbox[3] - adjusted_bbox[1],
                                      min_res + (2 * eps))

            # Check that input box was not changed
            assert adjusted_bbox is not bbox

    def test_buffered_bounding_box(self):
        """Bounding box can be buffered
        """

        big = (95.06, -11.0, 141.0, 5.9)
        mid = [103.28, -8.46, 109.67, -4.68]
        sml = (106.818998, -6.18585170, 106.82264510, -6.1810)

        for bbox in [big, mid, sml]:

            # Set common resolution which is bigger than the smallest box
            resolution = (0.1, 0.2)

            # Calculate minimal bounding box
            adjusted_bbox = buffered_bounding_box(bbox, resolution)

            # Check that adjusted box exceeds minimal resolution
            assert adjusted_bbox[2] - adjusted_bbox[0] > 2 * resolution[0]
            assert adjusted_bbox[3] - adjusted_bbox[1] > 2 * resolution[1]

            # Check that input box was not changed
            assert adjusted_bbox is not bbox

    def test_array2wkt(self):
        """Conversion to wkt data works

        It should create something like this
            'POLYGON((0 1, 2 3, 4 5, 6 7, 8 9))'
        """

        # Arrays first
        A = numpy.arange(10)
        A = A.reshape(5, 2)

        wkt = array_to_wkt(A, geom_type='POLYGON')
        assert wkt.startswith('POLYGON((')
        fields = wkt[9:-2].split(',')
        for i, field in enumerate(fields):
            x, y = field.split()
            assert numpy.allclose(A[i, :], [float(x), float(y)])

        # Then list
        wkt = array_to_wkt(A.tolist(), geom_type='POLYGON')
        assert wkt.startswith('POLYGON((')
        fields = wkt[9:-2].split(',')
        for i, field in enumerate(fields):
            x, y = field.split()
            assert numpy.allclose(A[i, :], [float(x), float(y)])

        # Then a linestring example (note one less bracket)
        wkt = array_to_wkt(A, geom_type='LINESTRING')
        assert wkt.startswith('LINESTRING(')
        fields = wkt[11:-1].split(',')
        for i, field in enumerate(fields):
            x, y = field.split()
            assert numpy.allclose(A[i, :], [float(x), float(y)])

    def test_polygon_area(self):
        """Polygon areas are computed correctly
        """

        # Create closed simple polygon (counter clock wise)
        p = numpy.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        a = calculate_polygon_area(p)
        msg = 'Calculated area was %f, expected 1.0 deg^2' % a
        assert numpy.allclose(a, 1), msg

        # Create closed simple polygon (clock wise)
        p = numpy.array([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
        a = calculate_polygon_area(p)
        msg = 'Calculated area was %f, expected 1.0 deg^2' % a
        assert numpy.allclose(a, 1), msg

        a = calculate_polygon_area(p, signed=True)
        msg = 'Calculated signed area was %f, expected -1.0 deg^2' % a
        assert numpy.allclose(a, -1), msg

        # Not starting at zero
        # Create closed simple polygon (counter clock wise)
        p = numpy.array([[168, -2], [169, -2], [169, -1],
                         [168, -1], [168, -2]])
        a = calculate_polygon_area(p)

        msg = 'Calculated area was %f, expected 1.0 deg^2' % a
        assert numpy.allclose(a, 1), msg

        # Realistic polygon
        filename = '%s/%s' % (TESTDATA, 'test_polygon.shp')
        layer = read_layer(filename)
        geometry = layer.get_geometry()

        p = geometry[0]
        a = calculate_polygon_area(p)

        # Verify against area reported by qgis (only three decimals)
        qgis_area = 0.003
        assert numpy.allclose(a, qgis_area, atol=1.0e-3)

        # Verify against area reported by ESRI ARC (very good correspondence)
        esri_area = 2.63924787273461e-3
        assert numpy.allclose(a, esri_area, rtol=0, atol=1.0e-10)

    def test_polygon_centroids(self):
        """Polygon centroids are computed correctly
        """

        # Create closed simple polygon (counter clock wise)
        p = numpy.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        c = calculate_polygon_centroid(p)

        msg = ('Calculated centroid was (%f, %f), expected '
               '(0.5, 0.5)' % tuple(c))
        assert numpy.allclose(c, [0.5, 0.5]), msg

        # Create closed simple polygon (clock wise)
        # FIXME (Ole): Not sure whether to raise an exception or
        #              to return absolute value in this case
        p = numpy.array([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
        c = calculate_polygon_centroid(p)

        msg = ('Calculated centroid was (%f, %f), expected '
               '(0.5, 0.5)' % tuple(c))
        assert numpy.allclose(c, [0.5, 0.5]), msg

        # Not starting at zero
        # Create closed simple polygon (counter clock wise)
        p = numpy.array([[168, -2], [169, -2], [169, -1],
                         [168, -1], [168, -2]])
        c = calculate_polygon_centroid(p)

        msg = ('Calculated centroid was (%f, %f), expected '
               '(168.5, -1.5)' % tuple(c))
        assert numpy.allclose(c, [168.5, -1.5]), msg

        # Realistic polygon
        filename = '%s/%s' % (TESTDATA, 'test_polygon.shp')
        layer = read_layer(filename)
        geometry = layer.get_geometry()

        p = geometry[0]
        c = calculate_polygon_centroid(p)

        # Check against reference centroid
        reference_centroid = [106.7036938, -6.134533855]  # From qgis
        assert numpy.allclose(c, reference_centroid, rtol=1.0e-8)

        # Store centroid to file (to e.g. check with qgis)
        out_filename = unique_filename(prefix='test_centroid', suffix='.shp')
        V = Vector(data=None,
                   projection=DEFAULT_PROJECTION,
                   geometry=[c],
                   name='Test centroid')
        V.write_to_file(out_filename)

        # Another realistic polygon
        p = numpy.array([[106.7922547, -6.2297884],
                         [106.7924589, -6.2298087],
                         [106.7924538, -6.2299127],
                         [106.7922547, -6.2298899],
                         [106.7922547, -6.2297884]])

        c = calculate_polygon_centroid(p)

        # Check against reference centroid from qgis
        reference_centroid = [106.79235602697445, -6.229849764722536]
        msg = 'Got %s but expected %s' % (str(c), str(reference_centroid))
        assert numpy.allclose(c, reference_centroid, rtol=1.0e-8), msg

        # Store centroid to file (to e.g. check with qgis)
        out_filename = unique_filename(prefix='test_centroid', suffix='.shp')
        V = Vector(data=None,
                   projection=DEFAULT_PROJECTION,
                   geometry=[c],
                   name='Test centroid')
        V.write_to_file(out_filename)

    def test_line_to_points(self):
        """Points along line are computed correctly
        """
        delta = 1
        # Create simple line
        l = numpy.array([[0, 0], [2, 0]])
        v = points_along_line(l, 1)

        expected_v = [[0, 0], [1, 0], [2, 0]]
        msg = ('Calculated points were %s, expected '
               '%s' % (v, expected_v))
        assert numpy.allclose(v, expected_v), msg

        # Not starting at zero
        # Create line
        l2 = numpy.array([[168, -2], [170, -2], [170, 0]])
        v2 = points_along_line(l2, delta)

        expected_v2 = [[168, -2], [169, -2], [170, -2], [170, -1], [170, 0]]
        msg = ('Calculated points were %s, expected '
               '%s' % (v2, expected_v2))
        assert numpy.allclose(v2, expected_v2), msg

        # Realistic polygon
        filename = '%s/%s' % (TESTDATA, 'indonesia_highway_sample.shp')
        layer = read_layer(filename)
        geometry = layer.get_geometry()

        p = geometry[0]
        c = points_along_line(p, delta)

        # Check against reference centroid
        expected_v = [
            [106.7168975, -6.15530081],
            [106.85224176, -6.15344678],
            [106.93660016, -6.21370279]]
        assert numpy.allclose(c, expected_v, rtol=1.0e-8)

        # Store points to file (to e.g. check with qgis)
        out_filename = unique_filename(prefix='test_points_along_line',
                                       suffix='.shp')
        # noinspection PyArgumentEqualDefault
        v = Vector(data=None,
                   projection=DEFAULT_PROJECTION,
                   geometry=[c],
                   name='Test points_along_line')
        v.write_to_file(out_filename)

    def test_geotransform2bbox(self):
        """Bounding box can be extracted from geotransform
        """

        M = 5
        N = 10
        for gt in GEOTRANSFORMS:
            bbox = geotransform_to_bbox(gt, M, N)

            # FIXME: Need better tests here, but this is better than nothing

            # Lower bounds
            assert bbox[0] == gt[0]

            # Upper bounds
            assert bbox[3] == gt[3]

    def test_geotransform2resolution(self):
        """Resolution can be extracted from geotransform
        """

        for gt in GEOTRANSFORMS:
            res = geotransform_to_resolution(gt, isotropic=False)
            assert len(res) == 2
            assert numpy.allclose(res[0], gt[1], rtol=0, atol=1.0e-12)
            assert numpy.allclose(res[1], - gt[5], rtol=0, atol=1.0e-12)

            res = geotransform_to_resolution(gt, isotropic=True)
            assert numpy.allclose(res, gt[1], rtol=0, atol=1.0e-12)
            assert numpy.allclose(res, - gt[5], rtol=0, atol=1.0e-12)

    def test_reading_and_writing_of_vector_line_data(self):
        """Vector line data can be read and written correctly
        """

        # Read and verify test data
        vectorname = 'indonesia_highway_sample.shp'

        filename = '%s/%s' % (TESTDATA, vectorname)
        layer = read_layer(filename)
        geometry = layer.get_geometry()
        attributes = layer.get_data()

        # Check basic data integrity
        N = len(layer)

        assert len(geometry) == N
        assert len(attributes) == N
        assert len(attributes[0]) == 3

        assert FEATURE_COUNTS[vectorname] == N
        assert isinstance(layer.get_name(), basestring)

        # Check projection
        wkt = layer.get_projection(proj4=False)
        assert wkt.startswith('GEOGCS')

        assert layer.projection == Projection(DEFAULT_PROJECTION)

        # Check each line
        for i in range(N):
            geom = geometry[i]
            n = geom.shape[0]
            # A line should have more than one point.
            assert n > 1
            # A point should have two dimensions.
            assert geom.shape[1] == 2

            # Check that not all points are the same
            max_dist = 0
            for j in range(n):
                d = numpy.sum((geom[j] - geom[0]) ** 2) / n
                if d > max_dist:
                    max_dist = d
            assert max_dist > 0

        expected_features = {0: {'LANES': 2,
                                 'TYPE': 'primary',
                                 'NAME': 'route1'},
                             1: {'LANES': 1,
                                 'TYPE': 'secondary',
                                 'NAME': 'route2'}}

        for i in range(N):
            # Consistency with attributes read manually with qgis

            if i in expected_features:
                att = attributes[i]
                exp = expected_features[i]

                for key in exp:
                    msg = ('Expected attribute %s was not found in feature %i'
                           % (key, i))
                    assert key in att, msg

                    a = att[key]
                    e = exp[key]
                    msg = 'Got %s: "%s" but expected "%s"' % (key, a, e)
                    assert a == e, msg

        # Write data back to file
        # FIXME (Ole): I would like to use gml here, but OGR does not
        #              store the spatial reference! Ticket #18
        out_filename = unique_filename(suffix='.shp')
        Vector(geometry=geometry, data=attributes, projection=wkt,
               geometry_type='line').write_to_file(out_filename)

        # Read again and check
        layer = read_layer(out_filename)
        assert layer.is_line_data
        geometry_new = layer.get_geometry()
        attributes_new = layer.get_data()

        N = len(layer)
        assert len(geometry_new) == N
        assert len(attributes_new) == N

        for i in range(N):
            assert numpy.allclose(geometry[i],
                                  geometry_new[i],
                                  rtol=1.0e-6)  # OGR works in single precision

            assert len(attributes_new[i]) == 3
            for key in attributes_new[i]:
                assert attributes_new[i][key] == attributes[i][key]

    def test_multipart_polygon_can_be_read(self):
        """Multipart polygons are be converted to singlepart
        """

        filename = ('%s/boundaries/rw_jakarta.shp' % DATADIR)
        L0 = read_layer(filename)
        assert len(L0) == 2685
        assert L0.is_polygon_data

        geometry = L0.get_geometry(as_geometry_objects=True)
        attributes = L0.get_data()
        projection = L0.get_projection()
        keywords = L0.get_keywords()

        # Store temporarily e.g. for inspection with QGIS
        tmp_filename = unique_filename(suffix='.shp')
        Vector(geometry=geometry, data=attributes,
               projection=projection,
               keywords=keywords).write_to_file(tmp_filename)

        # Read again
        L1 = read_layer(tmp_filename)

        assert len(L1) == len(L0)
        assert L1.is_polygon_data

        for i in range(len(L0)):
            # Check geometry
            g0 = L0.get_geometry(as_geometry_objects=True)[i]
            g1 = L1.get_geometry(as_geometry_objects=True)[i]
            assert numpy.allclose(g0.outer_ring, g1.outer_ring)
            assert len(g0.inner_rings) == len(g1.inner_rings)

            for j in range(len(g0.inner_rings)):
                assert numpy.allclose(g0.inner_rings[j], g1.inner_rings[j])

            # Check attributes
            v0 = L0.get_data()[i]
            v1 = L1.get_data()[i]
            assert v0 == v1

        # Check projection
        assert L0.projection == L1.projection

        # Compare all
        # Need to set this since we always use the latest version.
        L1.keywords['keyword_version'] = L0.keywords['keyword_version']
        assert L0 == L1

    test_multipart_polygon_can_be_read.slow = True

    def test_projection_comparisons(self):
        """Projection information can be correctly compared
        """

        # Although the two test datasets have the same projection,
        # this example failed with the message:
        # The reason was that comparison was done with get_projection()
        # rather than the projection objects themselves.

        # Projections must be the same: I got
        # GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",
        #       SPHEROID["WGS_1984",6378137,298.257223563]],
        #       PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]] and
        # GEOGCS["WGS 84",DATUM["WGS_1984",
        #       SPHEROID["WGS 84",6378137,298.257223563,
        #       AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],
        #       AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,
        #       AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,
        #       AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/rw_jakarta_singlepart.shp' % TESTDATA)
        exposure_filename = ('%s/indonesia_highway_sample.shp' % TESTDATA)

        # Read
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        Hp = H.projection
        Ep = E.projection
        msg = 'Projections did not match: %s != %s' % (Hp, Ep)
        assert Hp == Ep, msg

    test_projection_comparisons.slow = True

    def Xtest_reading_and_writing_of_multiband_rasters(self):
        """Multiband rasters can be read and written correctly
        """

        # FIXME (Ole, Sep 2012): WORK IN PROGRESS
        rastername = ('201208140700_Jakarta_200m_Sobek_Hypothetical_'
                      'Scenario_ACCESSA.nc')

        filename = '%s/%s' % (TESTDATA, rastername)
        R1 = read_layer(filename)

        # Check consistency of raster
        A1 = R1.get_data()
        M, N = A1.shape

        msg = ('Dimensions of raster array do not match those of '
               'raster file %s' % R1.filename)
        assert M == R1.rows, msg
        assert N == R1.columns, msg
        # More...

    def test_compatible_projections(self):
        """Projections that are compatible but not identical are recognised

        This is a test for issue #304
        """

        # Read two layers with compatible projections
        hazard_filename = '%s/donut.shp' % TESTDATA
        exposure_filename = ('%s/pop_merapi_prj_problem.asc' % TESTDATA)
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        # Verify that their projection strings are different
        assert H.get_projection() != E.get_projection()
        assert H.get_projection(proj4=True) != E.get_projection(proj4=True)

        # But the InaSAFE comparison does pass
        assert H.projection == E.projection


if __name__ == '__main__':
    suite = unittest.makeSuite(TestIO, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
