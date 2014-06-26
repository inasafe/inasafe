# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Clipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import sys
import os
import shutil
from unittest import expectedFailure

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../..///'))
sys.path.append(pardir)

import numpy

from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsGeometry,
    QgsPoint)

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.safe_interface import (
    read_safe_layer,
    get_optimal_extent,
    HAZDATA, TESTDATA, EXPDATA, UNITDATA,
    nan_allclose,
    GetDataError,
    unique_filename)
from safe_qgis.exceptions import InvalidProjectionError, CallGDALError
from safe_qgis.utilities.clipper import (
    clip_layer,
    extent_to_kml,
    explode_multipart_geometry,
    clip_geometry)
from safe_qgis.utilities.utilities import qgis_version
from safe_qgis.utilities.utilities_for_testing import (
    set_canvas_crs,
    RedirectStreams,
    DEVNULL,
    GEOCRS,
    set_jakarta_extent,
    compare_wkt)

# Setup path names for test data sets
VECTOR_PATH = os.path.join(TESTDATA, 'Padang_WGS84.shp')
VECTOR_PATH2 = os.path.join(TESTDATA, 'OSM_subset_google_mercator.shp')
VECTOR_PATH3 = os.path.join(UNITDATA, 'exposure', 'buildings_osm_4326.shp')

RASTERPATH = os.path.join(HAZDATA, 'Shakemap_Padang_2009.asc')
RASTERPATH2 = os.path.join(TESTDATA, 'population_padang_1.asc')


# noinspection PyStringFormat,PyTypeChecker,PyCallByClass,PyArgumentList
class ClipperTest(unittest.TestCase):
    """Test the InaSAFE clipper"""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_clip_vector(self):
        """Vector layers can be clipped."""

        # Create a vector layer
        layer_name = 'padang'
        vector_layer = QgsVectorLayer(VECTOR_PATH, layer_name, 'ogr')

        message = (
            'Did not find layer "%s" in path "%s"' % (layer_name, VECTOR_PATH))
        assert vector_layer is not None, message
        assert vector_layer.isValid()
        # Create a bounding box
        bounding_box = [100.03, -1.14, 100.81, -0.73]

        # Clip the vector to the bbox
        result = clip_layer(vector_layer, bounding_box)

        # Check the output is valid
        assert(os.path.exists(result.source()))

    def test_clip_raster(self):
        """Raster layers can be clipped."""

        # Create a raster layer
        layer_name = 'shake'
        raster_layer = QgsRasterLayer(RASTERPATH, layer_name)

        message = (
            'Did not find layer "%s" in path "%s"' % (layer_name, RASTERPATH))
        assert raster_layer is not None, message

        # Create a bounding box
        bounding_box = [97, -3, 104, 1]

        # Clip the vector to the bbox
        result = clip_layer(raster_layer, bounding_box)

        # Check the output is valid
        assert os.path.exists(result.source())

        # Clip and give a desired resolution for the output
        # big pixel size
        size = 0.05
        result = clip_layer(raster_layer, bounding_box, size)
        new_raster_layer = QgsRasterLayer(result.source(), layer_name)
        assert new_raster_layer.isValid(), 'Resampled raster is not valid'
        message = (
            'Resampled raster has incorrect pixel size. Expected: %5f, '
            'Actual: %5f' % (size, new_raster_layer.rasterUnitsPerPixelX()))
        assert new_raster_layer.rasterUnitsPerPixelX() == size, message

    def test_clip_raster_small(self):
        """Raster layers can be clipped in small and precise size. For #710."""

        # Create a raster layer
        layer_name = 'shake'
        raster_layer = QgsRasterLayer(RASTERPATH, layer_name)

        message = (
            'Did not find layer "%s" in path "%s"' % (layer_name, RASTERPATH))
        assert raster_layer is not None, message

        # Create a bounding box
        bounding_box = [97, -3, 104, 1]

        # Clip the vector to the bbox
        result = clip_layer(raster_layer, bounding_box)

        # Check the output is valid
        assert os.path.exists(result.source())

        # Clip and give a desired resolution for the output

        # small pixel size and high precision

        # based on pixel size of Flood_Current_Depth_Jakarta_geographic.asc
        size = 0.00045228819716
        result = clip_layer(raster_layer, bounding_box, size)
        new_raster_layer = QgsRasterLayer(result.source(), layer_name)
        assert new_raster_layer.isValid(), 'Resampled raster is not valid'
        message = (
            'Resampled raster has incorrect pixel size. Expected: %.14f, '
            'Actual: %.14f' % (
                size, new_raster_layer.rasterUnitsPerPixelX()))
        result_size = new_raster_layer.rasterUnitsPerPixelX()
        self.assertAlmostEqual(result_size, size, places=13, msg=message)

    def test_clip_raster_with_no_extension(self):
        """Test we can clip a raster with no extension - see #659."""
        # Create a raster layer
        source_file = os.path.join(UNITDATA, 'other', 'tenbytenraster.asc')
        test_file = unique_filename(prefix='tenbytenraster-')
        shutil.copyfile(source_file, test_file)

        # Create a keywords file
        source_file = os.path.join(
            UNITDATA, 'other', 'tenbytenraster.keywords')
        keywords_file = test_file + '.keywords'
        shutil.copyfile(source_file, keywords_file)

        # Test the raster layer
        raster_layer = QgsRasterLayer(test_file, 'ten by ten')
        # Create a bounding box
        rectangle = [1535380, 5083260, 1535380 + 40, 5083260 + 40]
        # Clip the vector to the bounding box
        result = clip_layer(raster_layer, rectangle)
        # Check the output is valid
        assert os.path.exists(result.source())

    # See issue #349
    @expectedFailure
    def test_clip_one_pixel(self):
        """Test for clipping less than one pixel."""
        # Create a raster layer
        raster_path = os.path.join(EXPDATA, 'glp10ag.asc')
        title = 'people'
        raster_layer = QgsRasterLayer(raster_path, title)

        # Create very small bounding box
        small_bounding_box = [100.3430, -0.9089, 100.3588, -0.9022]

        # Clip the raster to the bbox
        try:
            _ = clip_layer(raster_layer, small_bounding_box)
        except CallGDALError:
            pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)
        else:
            message = "Failed, does not raise exception"
            raise Exception(message)

        # Create not very small bounding box
        not_small_bounding_box = [100.3430, -0.9089, 101.3588, -1.9022]

        # Clip the raster to the bbox
        result = clip_layer(raster_layer, not_small_bounding_box)
        assert result is not None, 'Should be a success clipping'

    def test_invalid_filenames_caught(self):
        """Invalid filenames raise appropriate exceptions.

        Wrote this test because test_clipBoth raised the wrong error
        when file was missing. Instead of reporting that, it gave
        Western boundary must be less than eastern. I got [0.0, 0.0, 0.0, 0.0]

        See issue #170
        """

        # Try to create a vector layer from non-existing filename
        name = 'stnhaoeu_78oeukqjkrcgA'
        path = 'OEk_tnshoeu_439_kstnhoe'

        with RedirectStreams(stdout=DEVNULL, stderr=DEVNULL):
            vector_layer = QgsVectorLayer(path, name, 'ogr')

        message = (
            'QgsVectorLayer reported "valid" for non existent path "%s" and '
            'name "%s".' % (path, name))
        assert not vector_layer.isValid(), message

        # Create a raster layer
        with RedirectStreams(stdout=DEVNULL, stderr=DEVNULL):
            raster_layer = QgsRasterLayer(path, name)
        message = (
            'QgsRasterLayer reported "valid" for non existent path "%s" and '
            'name "%s". ' % (path, name))
        assert not raster_layer.isValid(), message

    def test_clip_both(self):
        """Raster and Vector layers can be clipped."""

        # Create a vector layer
        layer_name = 'padang'
        vector_layer = QgsVectorLayer(VECTOR_PATH, layer_name, 'ogr')
        message = (
            'Did not find layer "%s" in path "%s"' % (layer_name, VECTOR_PATH))
        assert vector_layer.isValid(), message

        # Create a raster layer
        layer_name = 'shake'
        raster_layer = QgsRasterLayer(RASTERPATH, layer_name)
        message = (
            'Did not find layer "%s" in path "%s"' % (layer_name, RASTERPATH))
        assert raster_layer.isValid(), message

        # Create a bounding box
        view_port_geo_extent = [99.53, -1.22, 101.20, -0.36]

        # Get the Hazard extents as an array in EPSG:4326
        hazard_geo_extent = [
            raster_layer.extent().xMinimum(),
            raster_layer.extent().yMinimum(),
            raster_layer.extent().xMaximum(),
            raster_layer.extent().yMaximum()
        ]

        # Get the Exposure extents as an array in EPSG:4326
        exposure_geo_extent = [
            vector_layer.extent().xMinimum(),
            vector_layer.extent().yMinimum(),
            vector_layer.extent().xMaximum(),
            vector_layer.extent().yMaximum()
        ]

        # Now work out the optimal extent between the two layers and
        # the current view extent. The optimal extent is the intersection
        # between the two layers and the viewport.
        # Extent is returned as an array [xmin,ymin,xmax,ymax]
        geo_extent = get_optimal_extent(
            hazard_geo_extent, exposure_geo_extent, view_port_geo_extent)

        # Clip the vector to the bbox
        result = clip_layer(vector_layer, geo_extent)

        # Check the output is valid
        assert os.path.exists(result.source())
        read_safe_layer(result.source())

        # Clip the raster to the bbox
        result = clip_layer(raster_layer, geo_extent)

        # Check the output is valid
        assert os.path.exists(result.source())
        read_safe_layer(result.source())

        # -------------------------------
        # Check the extra keywords option
        # -------------------------------
        # Clip the vector to the bbox
        result = clip_layer(
            vector_layer, geo_extent, extra_keywords={'kermit': 'piggy'})

        # Check the output is valid
        assert os.path.exists(result.source())
        safe_layer = read_safe_layer(result.source())
        keywords = safe_layer.get_keywords()
        # message = 'Extra keyword was not found in %s: %s' % (myResult,
        # keywords)
        assert keywords['kermit'] == 'piggy'

        # Clip the raster to the bbox
        result = clip_layer(
            raster_layer, geo_extent, extra_keywords={'zoot': 'animal'})

        # Check the output is valid
        assert os.path.exists(result.source())
        safe_layer = read_safe_layer(result.source())
        keywords = safe_layer.get_keywords()

        message = ('Extra keyword was not found in %s: %s' %
                   (result.source(), keywords))
        assert keywords['zoot'] == 'animal', message

    def test_raster_scaling(self):
        """Raster layers can be scaled when resampled.

        This is a test for ticket #52

        Native test .asc data has

        Population_Jakarta_geographic.asc
        ncols         638
        nrows         649
        cellsize      0.00045228819716044

        Population_2010.asc
        ncols         5525
        nrows         2050
        cellsize      0.0083333333333333

        Scaling is necessary for raster data that represents density
        such as population per km^2
        """

        filenames = [
            'Population_Jakarta_geographic.asc',
            'Population_2010.asc'
        ]
        for filename in filenames:
            raster_path = ('%s/%s' % (TESTDATA, filename))

            # Get reference values
            safe_layer = read_safe_layer(raster_path)
            min_value, max_value = safe_layer.get_extrema()
            del max_value
            del min_value
            native_resolution = safe_layer.get_resolution()

            # Get the Hazard extents as an array in EPSG:4326
            bounding_box = safe_layer.get_bounding_box()

            resolutions = [
                0.02,
                0.01,
                0.005,
                0.002,
                0.001,
                0.0005,  # Coarser
                0.0002  # Finer
            ]
            # Test for a range of resolutions
            for resolution in resolutions:  # Finer
                # To save time only do two resolutions for the
                # large population set
                if filename.startswith('Population_2010'):
                    if resolution > 0.01 or resolution < 0.005:
                        break

                # Clip the raster to the bbox
                extra_keywords = {'resolution': native_resolution}
                raster_layer = QgsRasterLayer(raster_path, 'xxx')
                result = clip_layer(
                    raster_layer,
                    bounding_box,
                    resolution,
                    extra_keywords=extra_keywords
                )

                safe_layer = read_safe_layer(result.source())
                native_data = safe_layer.get_data(scaling=False)
                scaled_data = safe_layer.get_data(scaling=True)

                sigma_value = (safe_layer.get_resolution()[0] /
                               native_resolution[0]) ** 2

                # Compare extrema
                expected_scaled_max = sigma_value * numpy.nanmax(native_data)
                message = (
                    'Resampled raster was not rescaled correctly: '
                    'max(scaled_data) was %f but expected %f' %
                    (numpy.nanmax(scaled_data), expected_scaled_max))

                # FIXME (Ole): The rtol used to be 1.0e-8 -
                #              now it has to be 1.0e-6, otherwise we get
                #              max(scaled_data) was 12083021.000000 but
                #              expected 12083020.414316
                #              Is something being rounded to the nearest
                #              integer?
                assert numpy.allclose(expected_scaled_max,
                                      numpy.nanmax(scaled_data),
                                      rtol=1.0e-6, atol=1.0e-8), message

                expected_scaled_min = sigma_value * numpy.nanmin(native_data)
                message = (
                    'Resampled raster was not rescaled correctly: '
                    'min(scaled_data) was %f but expected %f' %
                    (numpy.nanmin(scaled_data), expected_scaled_min))
                assert numpy.allclose(expected_scaled_min,
                                      numpy.nanmin(scaled_data),
                                      rtol=1.0e-8, atol=1.0e-12), message

                # Compare element-wise
                message = 'Resampled raster was not rescaled correctly'
                assert nan_allclose(native_data * sigma_value, scaled_data,
                                    rtol=1.0e-8, atol=1.0e-8), message

                # Check that it also works with manual scaling
                manual_data = safe_layer.get_data(scaling=sigma_value)
                message = 'Resampled raster was not rescaled correctly'
                assert nan_allclose(manual_data, scaled_data,
                                    rtol=1.0e-8, atol=1.0e-8), message

                # Check that an exception is raised for bad arguments
                try:
                    safe_layer.get_data(scaling='bad')
                except GetDataError:
                    pass
                else:
                    message = 'String argument should have raised exception'
                    raise Exception(message)

                try:
                    safe_layer.get_data(scaling='(1, 3)')
                except GetDataError:
                    pass
                else:
                    message = 'Tuple argument should have raised exception'
                    raise Exception(message)

                # Check None option without keyword datatype == 'density'
                safe_layer.keywords['datatype'] = 'undefined'
                unscaled_data = safe_layer.get_data(scaling=None)
                message = 'Data should not have changed'
                assert nan_allclose(native_data, unscaled_data,
                                    rtol=1.0e-12, atol=1.0e-12), message

                # Try with None and density keyword
                safe_layer.keywords['datatype'] = 'density'
                unscaled_data = safe_layer.get_data(scaling=None)
                message = 'Resampled raster was not rescaled correctly'
                assert nan_allclose(scaled_data, unscaled_data,
                                    rtol=1.0e-12, atol=1.0e-12), message

                safe_layer.keywords['datatype'] = 'counts'
                unscaled_data = safe_layer.get_data(scaling=None)
                message = 'Data should not have changed'
                assert nan_allclose(native_data, unscaled_data,
                                    rtol=1.0e-12, atol=1.0e-12), message

    def test_raster_scaling_projected(self):
        """Attempt to scale projected density raster layers raise exception.

        Automatic scaling when resampling density data
        does not currently work for projected layers. See issue #123.

        For the time being this test checks that an exception is raised
        when scaling is attempted on projected layers.
        When we resolve issue #123, this test should be rewritten.
        """

        test_filename = 'Population_Jakarta_UTM48N.tif'
        raster_path = ('%s/%s' % (TESTDATA, test_filename))

        # Get reference values
        safe_layer = read_safe_layer(raster_path)
        min_value, max_value = safe_layer.get_extrema()
        native_resolution = safe_layer.get_resolution()

        print min_value, max_value
        print native_resolution

        # Define bounding box in EPSG:4326
        bounding_box = [106.61, -6.38, 107.05, -6.07]

        resolutions = [0.02, 0.01, 0.005, 0.002, 0.001]
        # Test for a range of resolutions
        for resolution in resolutions:

            # Clip the raster to the bbox
            extra_keywords = {'resolution': native_resolution}
            raster_layer = QgsRasterLayer(raster_path, 'xxx')
            try:
                clip_layer(
                    raster_layer,
                    bounding_box,
                    resolution,
                    extra_keywords=extra_keywords
                )
            except InvalidProjectionError:
                pass
            else:
                message = 'Should have raised InvalidProjectionError'
                raise Exception(message)

    def test_extent_to_kml(self):
        """Test if extent to KML is working."""
        extent = [100.03, -1.14, 100.81, -0.73]
        kml_filename = extent_to_kml(extent)
        assert os.path.exists(kml_filename)
        kml_file = open(kml_filename)
        kml = kml_file.read()
        kml_file.close()

        message = 'Generated KML was not as expected: %s' % kml
        assert '<?xml version' in kml, message
        for value in extent:
            assert str(value) in kml, message

    def test_vector_projections(self):
        """Test that vector input data is reprojected properly during clip."""
        # Input data is OSM in GOOGLE CRS
        # We are reprojecting to GEO and expecting the output shp to be in GEO
        # see https://github.com/AIFDR/inasafe/issues/119
        # and https://github.com/AIFDR/inasafe/issues/95
        vector_layer = QgsVectorLayer(
            VECTOR_PATH2, 'OSM Buildings', 'ogr')
        message = 'Failed to load osm buildings'
        assert vector_layer is not None, message
        assert vector_layer.isValid()
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        clip_rectangle = [106.52, -6.38, 107.14, -6.07]
        # Clip the vector to the bbox
        result = clip_layer(vector_layer, clip_rectangle)
        assert(os.path.exists(result.source()))

    def test_explode_multi_polygon_geometry(self):
        """Test exploding POLY multipart to single part geometries works."""
        geometry = QgsGeometry.fromWkt(
            'MULTIPOLYGON(((-0.966314 0.445890,'
            '-0.281133 0.555729,-0.092839 0.218369,-0.908780 0.035305,'
            '-0.966314 0.445890)),((-0.906164 0.003923,-0.077148 0.197447,'
            '0.043151 -0.074533,-0.882628 -0.296824,-0.906164 0.003923)))')
        collection = explode_multipart_geometry(geometry)
        message = 'Expected 2 parts from multipart polygon geometry'
        assert len(collection) == 2, message

    def test_explode_multi_line_geometry(self):
        """Test exploding LINES multipart to single part geometries works."""
        geometry = QgsGeometry.fromWkt(
            'MULTILINESTRING((-0.974159 0.526961,'
            ' -0.291594 0.644645), (-0.411893 0.728331,'
            ' -0.160834 0.568804))')
        collection = explode_multipart_geometry(geometry)
        message = 'Expected 2 parts from multipart line geometry'
        assert len(collection) == 2, message

    def test_explode_multi_point_geometry(self):
        """Test exploding POINT multipart to single part geometries works"""
        geometry = QgsGeometry.fromWkt(
            'MULTIPOINT((-0.966314 0.445890),'
            '(-0.281133 0.555729))')
        collection = explode_multipart_geometry(geometry)
        message = 'Expected 2 parts from multipart point geometry'
        assert len(collection) == 2, message

    def test_clip_geometry(self):
        """Test that we can clip a geometry using another geometry."""
        geometry = QgsGeometry.fromPolyline([
            QgsPoint(10, 10),
            QgsPoint(20, 20),
            QgsPoint(30, 30),
            QgsPoint(40, 40)]
        )

        clip_polygon = QgsGeometry.fromPolygon([
            [QgsPoint(20, 20),
             QgsPoint(20, 30),
             QgsPoint(30, 30),
             QgsPoint(30, 20),
             QgsPoint(20, 20)]]
        )

        result = clip_geometry(clip_polygon, geometry)

        expected_wkt = 'LINESTRING(20.0 20.0, 30.0 30.0)'
        # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        assert compare_wkt(expected_wkt, str(result.exportToWkt()))

        # Now poly on poly clip test
        clip_polygon = QgsGeometry.fromWkt(
            'POLYGON((106.8218 -6.1842,106.8232 -6.1842,'
            '106.82304963 -6.18317148,106.82179736 -6.18314774,'
            '106.8218 -6.1842))')
        geometry = QgsGeometry.fromWkt(
            'POLYGON((106.8216869 -6.1852067,106.8213233 -6.1843051,'
            '106.8212891 -6.1835559,106.8222566 -6.1835184,'
            '106.8227557 -6.1835076,106.8228588 -6.1851204,'
            '106.8216869 -6.1852067))')
        result = clip_geometry(clip_polygon, geometry)

        expected_wkt = (
            'POLYGON((106.82179833 -6.18353616,106.8222566 -6.1835184,'
            '106.8227557 -6.1835076,106.82279996 -6.1842,'
            '106.8218 -6.1842,106.82179833 -6.18353616))')
        # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        assert compare_wkt(expected_wkt, str(result.exportToWkt()))

        # Now point on poly test clip

        geometry = QgsGeometry.fromWkt('POINT(106.82241 -6.18369)')
        result = clip_geometry(clip_polygon, geometry)

        if qgis_version() > 10800:
            expected_wkt = 'POINT(106.82241 -6.18369)'
        else:
            expected_wkt = 'POINT(106.822410 -6.183690)'
            # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        assert compare_wkt(expected_wkt, str(result.exportToWkt()))

    def test_clip_vector_hard(self):
        """Vector layers can be hard clipped.

        Hard clipping will remove any dangling, non intersecting elements.
        """
        vector_layer = QgsVectorLayer(
            VECTOR_PATH3, 'OSM Buildings', 'ogr')
        message = 'Failed to load osm buildings'
        assert vector_layer is not None, message
        assert vector_layer.isValid()
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        clip_rectangle = [106.8218, -6.1842, 106.8232, -6.1830]

        # Clip the vector to the bbox
        result = clip_layer(vector_layer, clip_rectangle, hard_clip_flag=True)

        # Check the output is valid
        assert(os.path.exists(result.source()))

if __name__ == '__main__':
    suite = unittest.makeSuite(ClipperTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
