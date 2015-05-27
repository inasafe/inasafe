# coding=utf-8
"""Tests for engine."""
import unittest
import cPickle
import numpy
import os
from os.path import join
from tempfile import mkdtemp

from safe.engine.core import calculate_impact
from safe.engine.interpolation import (
    interpolate_polygon_raster,
    interpolate_raster_vector_points,
    assign_hazard_values_to_exposure_data,
    tag_polygons_by_grid)
from safe.impact_functions import register_impact_functions
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.core import (
    read_layer,
    write_vector_data,
    write_raster_data)
from safe.storage.vector import Vector
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.gis.polygon import (
    separate_points_by_polygon,
    is_inside_polygon,
    inside_polygon,
    clip_lines_by_polygon,
    clip_grid_by_polygons,
    line_dictionary_to_geometry)
from safe.gis.interpolation2d import interpolate_raster
from safe.gis.numerics import (
    normal_cdf,
    log_normal_cdf,
    erf,
    ensure_numeric)
from safe.common.utilities import (
    VerificationError,
    unique_filename,
    temp_dir)
from safe.test.utilities import TESTDATA, HAZDATA, EXPDATA, test_data_path
from safe.common.exceptions import InaSAFEError


def linear_function(x, y):
    """Auxiliary function for use with interpolation test
    :param y:
    :param x:

    :returns: Average
    """
    return x + y / 2.0


class TestEngine(unittest.TestCase):
    """Tests for engine module."""

    def setUp(self):
        """Run before each test."""
        # ensure we are using english by default
        os.environ['LANG'] = 'en'
        # load impact function
        register_impact_functions()
        self.impact_function_manager = ImpactFunctionManager()

    # This one currently fails because the clipped input data has
    # different resolution to the full data. Issue #344
    #
    # This test is not finished, but must wait 'till #344 has been sorted
    @unittest.expectedFailure
    def test_polygon_hazard_raster_exposure_clipped_grids(self):
        """Rasters clipped by polygons irrespective of pre-clipping.

        Double check that a raster clipped by the QGIS front-end
        produces the same results as when full raster is used.
        """

        # Read test files
        hazard_filename = '%s/donut.shp' % TESTDATA
        exposure_filename_clip = ('%s/pop_merapi_clip.tif' % TESTDATA)
        exposure_filename_full = ('%s/pop_merapi_prj_problem.asc'
                                  % TESTDATA)

        H = read_layer(hazard_filename)
        E_clip = read_layer(exposure_filename_clip)
        E_full = read_layer(exposure_filename_full)

        # Establish whether full and clipped grids coincide
        # in clipped area
        gt_clip = E_clip.get_geotransform()
        gt_full = E_full.get_geotransform()

        msg = ('Resolutions were different. Geotransform full grid: %s, '
               'clipped grid: %s' % (gt_full, gt_clip))
        assert numpy.allclose(gt_clip[1], gt_full[1]), msg
        assert numpy.allclose(gt_clip[5], gt_full[5]), msg

        polygons = H.get_geometry(as_geometry_objects=True)

        # Clip
        res_clip, _ = clip_grid_by_polygons(E_clip.get_data(),
                                         E_clip.get_geotransform(),
                                         polygons)

        # print res_clip
        # print len(res_clip)

        res_full, _ = clip_grid_by_polygons(E_full.get_data(),
                                         E_full.get_geotransform(),
                                         polygons)

        assert len(res_clip) == len(res_full)

        for i in range(len(res_clip)):
            # print
            x = res_clip[i][0]
            y = res_full[i][0]

            # print x
            # print y
            msg = ('Got len(x) == %i, len(y) == %i. Should be the same'
                   % (len(x), len(y)))
            assert len(x) == len(y), msg

            # Check that they are inside the respective polygon
            P = polygons[i]
            idx = inside_polygon(x,  # pylint: disable=W0612
                                 P.outer_ring,
                                 holes=P.inner_rings)
            # print idx

            msg = ('Expected point locations to be the same in clipped '
                   'and full grids, Got %s and %s' % (x, y))
            assert numpy.allclose(x, y)

    def test_polygon_hazard_and_raster_exposure_big(self):
        """Rasters can be converted to points and clipped by polygons

        This is a test for the basic machinery needed for issue #91

        It uses over 400,000 gridpoints and 2704 complex polygons,
        each with 10-200 vertices, and serves a test for optimising
        the polygon clipping algorithm. With the optimisations requested
        in https://github.com/AIFDR/inasafe/issues/222 it takes about 100
        seconds on a good workstation while it takes over 2000 seconds
        without it.

        This test also runs the high level interpolation routine which assigns
        attributes to the new point layer. The runtime is virtually the same as
        the underlying function.
        """

        # Name input files
        polyhazard = join(TESTDATA, 'rw_jakarta_singlepart.shp')
        population = join(TESTDATA, 'Population_Jakarta_geographic.asc')

        # Get layers using API
        H = read_layer(polyhazard)
        E = read_layer(population)

        N = len(H)
        assert N == 2704

        # Run and test the fundamental clipping routine
        # import time
        # t0 = time.time()
        res, _ = clip_grid_by_polygons(
            E.get_data(),
            E.get_geotransform(),
            H.get_geometry(as_geometry_objects=True))
        # print 'Engine took %i seconds' % (time.time() - t0)

        assert len(res) == N

        # Characterisation test
        assert H.get_data()[0]['RW'] == 'RW 01'
        assert H.get_data()[0]['KAB_NAME'] == 'JAKARTA UTARA'
        assert H.get_data()[0]['KEC_NAME'] == 'TANJUNG PRIOK'
        assert H.get_data()[0]['KEL_NAME'] == 'KEBON BAWANG'

        geom = res[0][0]
        vals = res[0][1]
        assert numpy.allclose(vals[17], 1481.98)
        assert numpy.allclose(geom[17][0], 106.88927)  # LON
        assert numpy.allclose(geom[17][1], -6.114458)  # LAT

        # Then run and test the high level interpolation function
        # t0 = time.time()
        P, _ = interpolate_polygon_raster(
            H, E, layer_name='poly2raster_test', attribute_name='grid_value')
        # print 'High level function took %i seconds' % (time.time() - t0)
        # P.write_to_file('polygon_raster_interpolation_example_big.shp')

        # Characterisation tests (values verified using QGIS)
        attributes = P.get_data()[17]
        geometry = P.get_geometry()[17]

        assert attributes['RW'] == 'RW 01'
        assert attributes['KAB_NAME'] == 'JAKARTA UTARA'
        assert attributes['KEC_NAME'] == 'TANJUNG PRIOK'
        assert attributes['KEL_NAME'] == 'KEBON BAWANG'
        assert attributes['polygon_id'] == 0
        assert numpy.allclose(attributes['grid_value'], 1481.984)

        assert numpy.allclose(geometry[0], 106.88927)  # LON
        assert numpy.allclose(geometry[1], -6.11448)  # LAT

        # A second characterisation test
        attributes = P.get_data()[10000]
        geometry = P.get_geometry()[10000]

        assert attributes['RW'] == 'RW 06'
        assert attributes['KAB_NAME'] == 'JAKARTA UTARA'
        assert attributes['KEC_NAME'] == 'PENJARINGAN'
        assert attributes['KEL_NAME'] == 'KAMAL MUARA'
        assert attributes['polygon_id'] == 93
        assert numpy.allclose(attributes['grid_value'], 715.6508)

        assert numpy.allclose(geometry[0], 106.74137)  # LON
        assert numpy.allclose(geometry[1], -6.10634)  # LAT

        # A third characterisation test
        attributes = P.get_data()[99000]
        geometry = P.get_geometry()[99000]

        assert attributes['RW'] == 'RW 08'
        assert attributes['KAB_NAME'] == 'JAKARTA TIMUR'
        assert attributes['KEC_NAME'] == 'CAKUNG'
        assert attributes['KEL_NAME'] == 'CAKUNG TIMUR'
        assert attributes['polygon_id'] == 927
        assert numpy.allclose(attributes['grid_value'], 770.7628)

        assert numpy.allclose(geometry[0], 106.9675237)  # LON
        assert numpy.allclose(geometry[1], -6.16468982)  # LAT

    test_polygon_hazard_and_raster_exposure_big.slow = True

    def test_polygon_hazard_and_raster_exposure_small(self):
        """Exposure rasters can be clipped by polygon exposure

        This is a test for the basic machinery needed for issue #91
        """

        # Name input files
        polyhazard = join(TESTDATA, 'test_polygon_on_test_grid.shp')
        population = join(TESTDATA, 'test_grid.asc')

        # Get layers using API
        H = read_layer(polyhazard)
        E = read_layer(population)

        N = len(H)
        assert N == 4

        # Run underlying clipping routine
        res0, _ = clip_grid_by_polygons(
            E.get_data(),
            E.get_geotransform(),
            H.get_geometry(as_geometry_objects=True))
        assert len(res0) == N

        # Run higher level interpolation routine
        P, _ = interpolate_polygon_raster(
            H, E, layer_name='poly2raster_test', attribute_name='grid_value')

        # Verify result (numbers obtained from using QGIS)
        # P.write_to_file('poly2raster_test.shp')
        attributes = P.get_data()
        geometry = P.get_geometry()

        # Polygon 0
        assert attributes[0]['id'] == 0
        assert attributes[0]['name'] == 'A'
        assert numpy.allclose(attributes[0]['number'], 31415)
        assert numpy.allclose(attributes[0]['grid_value'], 50.8147)
        assert attributes[0]['polygon_id'] == 0

        assert attributes[1]['id'] == 0
        assert attributes[1]['name'] == 'A'
        assert numpy.allclose(geometry[1][0], 96.97137053)  # Lon
        assert numpy.allclose(geometry[1][1], -5.349657148)  # Lat
        assert numpy.allclose(attributes[1]['number'], 31415)
        assert numpy.allclose(attributes[1]['grid_value'], 3)
        assert attributes[1]['polygon_id'] == 0

        assert attributes[3]['id'] == 0
        assert attributes[3]['name'] == 'A'
        assert numpy.allclose(attributes[3]['number'], 31415)
        assert numpy.allclose(attributes[3]['grid_value'], 50.127)
        assert attributes[3]['polygon_id'] == 0

        # Polygon 1
        assert attributes[6]['id'] == 1
        assert attributes[6]['name'] == 'B'
        assert numpy.allclose(attributes[6]['number'], 13)
        assert numpy.allclose(attributes[6]['grid_value'], 50.338)
        assert attributes[6]['polygon_id'] == 1

        assert attributes[11]['id'] == 1
        assert attributes[11]['name'] == 'B'
        assert numpy.allclose(attributes[11]['number'], 13)
        assert numpy.allclose(attributes[11]['grid_value'], 50.5438)
        assert attributes[11]['polygon_id'] == 1

        assert attributes[13]['id'] == 1
        assert attributes[13]['name'] == 'B'
        assert numpy.allclose(geometry[13][0], 97.002111596)  # Lon
        assert numpy.allclose(geometry[13][1], -5.472621404)  # Lat
        assert numpy.allclose(attributes[13]['number'], 13)
        assert numpy.allclose(attributes[13]['grid_value'], 50.988)
        assert attributes[13]['polygon_id'] == 1

        # Polygon 2 (overlapping)
        assert attributes[16]['id'] == 2
        assert attributes[16]['name'] == 'Intersecting'
        assert numpy.allclose(attributes[16]['number'], 100)
        assert numpy.allclose(attributes[16]['grid_value'], 50.9574)
        assert attributes[16]['polygon_id'] == 2

        assert attributes[21]['id'] == 2
        assert attributes[21]['name'] == 'Intersecting'
        assert numpy.allclose(attributes[21]['number'], 100)
        assert numpy.allclose(attributes[21]['grid_value'], 50.2238)

        # Polygon 3
        assert attributes[23]['id'] == 3
        assert attributes[23]['name'] == 'D'
        assert numpy.allclose(geometry[23][0], 97.0021116)  # Lon
        assert numpy.allclose(geometry[23][1], -5.503362468)  # Lat
        assert numpy.allclose(attributes[23]['number'], -50)
        assert numpy.allclose(attributes[23]['grid_value'], 50.0377)
        assert attributes[23]['polygon_id'] == 3

    def test_tagging_polygons_by_raster_values(self):
        """Polygons can be tagged by raster values

        This is testing a simple application of clip_grid_by_polygons
        """

        # Name input files
        polygon = join(TESTDATA, 'test_polygon_on_test_grid.shp')
        grid = join(TESTDATA, 'test_grid.asc')

        # Get layers using API
        G = read_layer(grid)
        P = read_layer(polygon)

        # Run tagging routine
        R = tag_polygons_by_grid(P, G, threshold=50.85, tag='tag')
        assert len(R) == len(P)

        data = R.get_data()
        for d in data:
            assert 'tag' in d

        # Check against inspection with QGIS. Only polygon 1 and 2
        # contain grid points with values greater than 50.85
        assert data[0]['tag'] is False
        assert data[1]['tag'] is True
        assert data[2]['tag'] is True
        assert data[3]['tag'] is False

    def test_polygon_hazard_with_holes_and_raster_exposure(self):
        """Rasters can be clipped by polygons (with holes)

        This is testing that a collection of polygons - some with holes -
        can correctly clip and tag raster points.
        """

        # Name input files
        polyhazard = join(TESTDATA, 'donut.shp')
        population = join(TESTDATA, 'pop_merapi_clip.tif')

        # Get layers using API
        H = read_layer(polyhazard)
        E = read_layer(population)

        N = len(H)
        assert N == 10

        # Characterisation test
        assert H.get_data()[9]['KRB'] == 'Kawasan Rawan Bencana II'

        # Then run and test the high level interpolation function
        P, _ = interpolate_polygon_raster(
            H, E, layer_name='poly2raster_test', attribute_name='grid_value')

        # Possibly write result to file for visual inspection, e.g. with QGIS
        # P.write_to_file('polygon_raster_interpolation_example_holes.shp')

        # Characterisation tests (values verified using QGIS)
        # In internal polygon
        attributes = P.get_data()[43]
        # geometry = P.get_geometry()[43]
        assert attributes['KRB'] == 'Kawasan Rawan Bencana III'
        assert attributes['polygon_id'] == 8

        # In polygon ring
        attributes = P.get_data()[222]
        # geometry = P.get_geometry()[222]
        assert attributes['KRB'] == 'Kawasan Rawan Bencana II'
        assert attributes['polygon_id'] == 9

        # In one of the outer polygons
        attributes = P.get_data()[26]
        # geometry = P.get_geometry()[26]
        assert attributes['KRB'] == 'Kawasan Rawan Bencana I'
        assert attributes['polygon_id'] == 4

    test_polygon_hazard_with_holes_and_raster_exposure.slow = True

    def test_user_directory_when_saving(self):
        # These imports must be inside the test.
        from PyQt4.QtCore import QCoreApplication, QSettings
        from qgis.core import QgsApplication

        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationName('QGIS')
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationDomain('qgis.org')
        # noinspection PyCallByClass
        QCoreApplication.setApplicationName('QGIS2InaSAFETesting')

        # Save some settings
        settings = QSettings()
        temp_directory = temp_dir('testing_user_directory')
        temp_directory = mkdtemp(dir=temp_directory)
        settings.setValue(
            'inasafe/defaultUserDirectory', temp_directory.encode('utf-8'))

        # Setting layers
        hazard_filename = test_data_path('hazard', 'jakarta_flood_design.tif')
        exposure_filename = test_data_path(
            'exposure', 'buildings_osm_4326.shp')

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'FloodRasterBuildingFunction'
        plugin_list = self.impact_function_manager.filter_by_metadata(
            'id', plugin_name)
        IF = plugin_list[0].instance()

        calculate_impact(layers=[H, E], impact_function=IF)

        message = 'The user directory is empty : %s' % temp_directory
        assert os.listdir(temp_directory) != [], message

        settings.remove('inasafe/defaultUserDirectory')

    test_user_directory_when_saving.slow = False

    def test_data_sources_are_carried_forward(self):
        """Data sources are carried forward to impact layer."""
        hazard_filepath = test_data_path(
            'hazard', 'continuous_flood_20_20.asc')
        exposure_filepath = test_data_path('exposure', 'buildings.shp')

        hazard_layer = read_layer(hazard_filepath)
        exposure_layer = read_layer(exposure_filepath)
        hazard_title = hazard_layer.get_keywords()['title']
        exposure_title = exposure_layer.get_keywords()['title']
        hazard_source = hazard_layer.get_keywords()['source']
        exposure_source = exposure_layer.get_keywords()['source']

        function_id = 'FloodRasterBuildingFunction'
        impact_function = self.impact_function_manager.get(function_id)
        impact_vector = calculate_impact(
            layers=[hazard_layer, exposure_layer],
            impact_function=impact_function)

        self.assertEqual(
            impact_vector.get_keywords()['hazard_title'], hazard_title)
        self.assertEqual(
            impact_vector.get_keywords()['exposure_title'], exposure_title)
        self.assertEqual(
            impact_vector.get_keywords()['hazard_source'], hazard_source)
        self.assertEqual(
            impact_vector.get_keywords()['exposure_source'], exposure_source)

    test_data_sources_are_carried_forward.slow = True

    def test_raster_vector_interpolation_exception(self):
        """Exceptions are caught by interpolate_raster_points."""

        hazard_filename = (
            '%s/tsunami_max_inundation_depth_4326.tif' % TESTDATA)
        exposure_filename = ('%s/tsunami_building_exposure.shp' % TESTDATA)

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        try:
            interpolate_raster_vector_points(H, E, mode='oexoeua')
        except InaSAFEError:
            pass
        else:
            msg = 'Should have raised InaSAFEError'
            raise Exception(msg)
        # FIXME (Ole): Try some other error conditions

    def test_interpolation_wrapper(self):
        """Interpolation library works for linear function
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes

        # Define array where latitudes are rows and longitude columns
        A = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        longitudes = numpy.linspace(lon_ll + 0.5,
                                    lon_ll + numlon - 0.5, numlon)
        latitudes = numpy.linspace(lat_ll + 0.5,
                                   lat_ll + numlat - 0.5, numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A[numlat - 1 - i, j] = linear_function(
                    longitudes[j], latitudes[i])

        # Test first that original points are reproduced correctly
        for i, eta in enumerate(latitudes):
            for j, xi in enumerate(longitudes):

                val = interpolate_raster(longitudes, latitudes, A,
                                         [(xi, eta)], mode='linear')[0]
                assert numpy.allclose(val,
                                      linear_function(xi, eta),
                                      rtol=1e-12, atol=1e-12)

        # Then test that genuinly interpolated points are correct
        xis = numpy.linspace(lon_ll + 1, lon_ll + numlon - 1, 10 * numlon)
        etas = numpy.linspace(lat_ll + 1, lat_ll + numlat - 1, 10 * numlat)
        for xi in xis:
            for eta in etas:
                val = interpolate_raster(longitudes, latitudes, A,
                                         [(xi, eta)], mode='linear')[0]
                assert numpy.allclose(val,
                                      linear_function(xi, eta),
                                      rtol=1e-12, atol=1e-12)

    test_interpolation_wrapper.slow = True

    def test_interpolation_functions(self):
        """Interpolation using Raster and Vector objects
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes
        dlon = 1
        dlat = -1

        # Define array where latitudes are rows and longitude columns
        A = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        longitudes = numpy.linspace(lon_ll + 0.5,
                                    lon_ll + numlon - 0.5,
                                    numlon)
        latitudes = numpy.linspace(lat_ll + 0.5,
                                   lat_ll + numlat - 0.5,
                                   numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A[numlat - 1 - i, j] = linear_function(longitudes[j],
                                                       latitudes[i])

        # Write array to a raster file
        geotransform = (lon_ul, dlon, 0, lat_ul, 0, dlat)
        projection = ('GEOGCS["GCS_WGS_1984",'
                      'DATUM["WGS_1984",'
                      'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                      'PRIMEM["Greenwich",0.0],'
                      'UNIT["Degree",0.0174532925199433]]')

        raster_filename = unique_filename(suffix='.tif')
        write_raster_data(A,
                          projection,
                          geotransform,
                          raster_filename)

        # Write test interpolation point to a vector file
        coordinates = []
        for xi in longitudes:
            for eta in latitudes:
                coordinates.append((xi, eta))

        vector_filename = unique_filename(suffix='.shp')
        write_vector_data(data=None,
                          projection=projection,
                          geometry=coordinates,
                          filename=vector_filename)

        # Read both datasets back in
        R = read_layer(raster_filename)
        V = read_layer(vector_filename)

        # Then test that axes and data returned by R are correct
        x, y = R.get_geometry()  # pylint: disable=W0633,W0632
        msg = 'X axes was %s, should have been %s' % (longitudes, x)
        assert numpy.allclose(longitudes, x), msg
        msg = 'Y axes was %s, should have been %s' % (latitudes, y)
        assert numpy.allclose(latitudes, y), msg
        AA = R.get_data()
        msg = 'Raster data was %s, should have been %s' % (AA, A)
        assert numpy.allclose(AA, A), msg

        # Test interpolation function with default layer_name
        I = assign_hazard_values_to_exposure_data(R, V, attribute_name='value')
        # msg = 'Got name %s, expected %s' % (I.get_name(), V.get_name())
        # assert V.get_name() == I.get_name(), msg

        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        # Test that interpolated points are correct
        for i, (xi, eta) in enumerate(Icoordinates):

            z = Iattributes[i]['value']
            # print xi, eta, z, linear_function(xi, eta)
            assert numpy.allclose(z, linear_function(xi, eta),
                                  rtol=1e-12)

        # FIXME (Ole): Need test for values outside grid.
        #              They should be NaN or something

        # Cleanup
        # FIXME (Ole): Shape files are a collection of files. How to remove?
        os.remove(vector_filename)

    def test_interpolation_lembang(self):
        """Interpolation using Lembang data set
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/lembang_mmi_hazmap.asc' % TESTDATA
        exposure_filename = '%s/test_buildings.shp' % TESTDATA

        # Read input data
        hazard_raster = read_layer(hazard_filename)
        mmi_min, mmi_max = hazard_raster.get_extrema()

        exposure_vector = read_layer(exposure_filename)
        coordinates = exposure_vector.get_geometry()
        attributes = exposure_vector.get_data()

        # Test interpolation function
        I = assign_hazard_values_to_exposure_data(hazard_raster,
                                                  exposure_vector,
                                                  attribute_name='MMI')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        # Check that interpolated MMI was done as expected
        fid = open('%s/test_buildings_percentage_loss_and_mmi.txt' % TESTDATA)
        reference_points = []
        MMI = []
        for line in fid.readlines()[1:]:
            fields = line.strip().split(',')

            lon = float(fields[4][1:-1])
            lat = float(fields[3][1:-1])
            mmi = float(fields[-1][1:-1])

            reference_points.append((lon, lat))
            MMI.append(mmi)

        # Verify that coordinates are consistent
        msg = 'Interpolated coordinates do not match those of test data'
        assert numpy.allclose(Icoordinates, reference_points), msg

        # Verify interpolated MMI with test result
        for i in range(len(MMI)):
            calculated_mmi = Iattributes[i]['MMI']

            # Check that interpolated points are within range
            msg = ('Interpolated MMI %f was outside extrema: '
                   '[%f, %f]. ' % (calculated_mmi, mmi_min, mmi_max))
            assert mmi_min <= calculated_mmi <= mmi_max, msg

            # Check that result is within 2% - this is good enough
            # as this was calculated using EQRM and thus different.
            assert numpy.allclose(calculated_mmi, MMI[i], rtol=0.02)

            # Check that all original attributes were carried through
            # according to issue #101
            for key in attributes[i]:
                msg = 'Expected key %s in interpolated attributes' % key
                assert key in Iattributes[i], msg

                Ival = Iattributes[i][key]
                val = attributes[i][key]

                msg = ('Interpolated attribute %s did not have the '
                       'expected value %s. I got %s' % (key, val, Ival))

                try:
                    assert Ival == val, msg
                except AssertionError:
                    assert numpy.allclose(Ival, val, rtol=1.0e-6), msg

    test_interpolation_lembang.slow = True

    def test_interpolation_tsunami(self):
        """Interpolation using tsunami data set works

        This is test for issue #19 about interpolation overshoot
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = (
            '%s/tsunami_max_inundation_depth_4326.tif' % TESTDATA)
        exposure_filename = ('%s/tsunami_building_exposure.shp' % TESTDATA)

        # Read input data
        hazard_raster = read_layer(hazard_filename)
        depth_min, depth_max = hazard_raster.get_extrema()

        exposure_vector = read_layer(exposure_filename)
        coordinates = exposure_vector.get_geometry()

        # Test interpolation function
        I = assign_hazard_values_to_exposure_data(
            hazard_raster, exposure_vector, attribute_name='depth')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        # Verify interpolated values with test result
        for i in range(len(Icoordinates)):

            interpolated_depth = Iattributes[i]['depth']
            # Check that interpolated points are within range
            msg = ('Interpolated depth %f at point %i was outside extrema: '
                   '[%f, %f]. ' % (interpolated_depth, i,
                                   depth_min, depth_max))

            if not numpy.isnan(interpolated_depth):
                assert depth_min <= interpolated_depth <= depth_max, msg

    def test_interpolation_tsunami_maumere(self):
        """Interpolation using tsunami data set from Maumere

        This is a test for interpolation (issue #19)
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = ('%s/maumere_aos_depth_20m_land_wgs84.asc'
                           % HAZDATA)
        exposure_filename = ('%s/maumere_pop_prj.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        depth_min, depth_max = H.get_extrema()

        # Compare extrema to values read off QGIS for this layer
        assert numpy.allclose([depth_min, depth_max], [0.0, 16.68],
                              rtol=1.0e-6, atol=1.0e-10)

        E = read_layer(exposure_filename)
        coordinates = E.get_geometry()
        attributes = E.get_data()

        # Test the interpolation function
        I = assign_hazard_values_to_exposure_data(H, E, attribute_name='depth')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        N = len(Icoordinates)
        assert N == 891

        # Verify interpolated values with test result
        for i in range(N):

            interpolated_depth = Iattributes[i]['depth']
            pointid = attributes[i]['POINTID']

            if pointid == 263:

                # print i, pointid, attributes[i],
                # print interpolated_depth, coordinates[i]

                # Check that location is correct
                assert numpy.allclose(coordinates[i],
                                      [122.20367299, -8.61300358])

                # This is known to be outside inundation area so should
                # near zero
                print
                assert numpy.allclose(interpolated_depth, 0.0,
                                      rtol=1.0e-12, atol=1.0e-12)

            if pointid == 148:
                # Check that location is correct
                assert numpy.allclose(coordinates[i],
                                      [122.2045912, -8.608483265])

                # This is in an inundated area with a surrounding depths of
                # 4.531, 3.911
                # 2.675, 2.583
                assert interpolated_depth < 4.531
                assert interpolated_depth < 3.911
                assert interpolated_depth > 2.583
                assert interpolated_depth > 2.675

                # This is a characterisation test for bilinear interpolation
                # Akbar - 20 Feb 2014:
                # I changed the tolerance between interpolated_depth and the
                # expected result. The expected result when we do the full
                # safe test is 3.62477202599, while it is 3.62477204455 when
                # we do single test (computer also needs to rest?). The rtol
                # and atol was 1.0e-12
                print 'Interpolated depth is: %.12f' % interpolated_depth
                assert numpy.allclose([interpolated_depth], [3.62477204455],
                                      rtol=1.0e-8, atol=1.0e-8)

            # Check that interpolated points are within range
            msg = ('Interpolated depth %f at point %i was outside extrema: '
                   '[%f, %f]. ' % (interpolated_depth, i,
                                   depth_min, depth_max))

            if not numpy.isnan(interpolated_depth):
                assert depth_min <= interpolated_depth <= depth_max, msg

    test_interpolation_tsunami_maumere.slow = True

    def test_polygon_clipping(self):
        """Clipping using real polygon and point data from Maumere
        """

        # Test data
        polygon_filename = ('%s/test_poly.txt' % TESTDATA)  # Polygon 799
        points_filename = ('%s/test_points.txt' % TESTDATA)

        # Read
        polygon = []
        fid = open(polygon_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            polygon.append([float(fields[0]), float(fields[1])])
        polygon = ensure_numeric(polygon)

        points = []
        fid = open(points_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            points.append([float(fields[0]), float(fields[1])])
        points = ensure_numeric(points)

        # Clip
        inside, outside = separate_points_by_polygon(points, polygon)

        # Expected number of points inside
        assert len(inside) == 458

        # First 10 inside
        assert numpy.alltrue(inside[:10] == [2279, 2290, 2297, 2306, 2307,
                                             2313, 2316, 2319, 2321, 2322])

        # Last 10 outside
        assert numpy.alltrue(outside[-10:] == [3519, 3520, 3521, 3522, 3523,
                                               3524, 3525, 3526, 3527, 3528])
        # Store for viewing in e.g. QGis
        if False:  # True:
            Vector(geometry=[polygon]).write_to_file('test_poly.shp')
            pts_inside = points[inside]
            Vector(geometry=pts_inside).write_to_file('test_points_in.shp')
            pts_outside = points[outside]
            Vector(geometry=pts_outside).write_to_file('test_points_out.shp')

    test_polygon_clipping.slow = True

    def test_interpolation_from_polygons_one_poly(self):
        """Point interpolation using one polygon from Maumere works

        This is a test for interpolation (issue #48)
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to make test quick
        # Polygon #799 is the one used in separate test
        H = Vector(data=H_attributes[799:800],
                   geometry=H_geometry[799:800],
                   projection=H.get_projection())
        # H.write_to_file('MM_799.shp')  # E.g. to view with QGis

        E = read_layer(exposure_filename)
        E_attributes = E.get_data()

        # Test interpolation function
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')

        I_attributes = I.get_data()
        msg = 'Expected "depth", got %s' % I.get_name()
        assert I.get_name() == 'depth', msg

        N = len(I_attributes)
        assert N == len(E_attributes)

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        for i in range(N):
            category = I_attributes[i]['Category']
            if category is not None:
                count += 1

        msg = ('Expected 458 points tagged with category, '
               'but got only %i' % count)
        assert count == 458, msg

    test_interpolation_from_polygons_one_poly.slow = True

    def test_interpolation_from_polygons_multiple(self):
        """Point interpolation using multiple polygons from Maumere works

        This is a test for interpolation (issue #48)
        """

        # FIXME (Ole): Really should move this and subsequent tests to
        #              test_io.py

        # Name file names for hazard and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Full version
        H = Vector(data=H_attributes,
                   geometry=H_geometry,
                   projection=H.get_projection())

        E = read_layer(exposure_filename)
        E_attributes = E.get_data()

        # Test interpolation function
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')

        I_attributes = I.get_data()

        N = len(I_attributes)
        assert N == len(E_attributes)

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        counts = {}
        for i in range(N):
            attrs = I_attributes[i]
            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE]:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Count items in each specific category
            category = attrs['Category']
            if category not in counts:
                counts[category] = 0
            counts[category] += 1

        if len(H) == 192:
            # In case we used cut down version
            msg = ('Expected 100 points tagged with category "High", '
                   'but got only %i' % counts['High'])
            assert counts['High'] == 100, msg

            msg = ('Expected 739 points tagged with category "Very High", '
                   'but got only %i' % counts['Very High'])
            assert counts['Very High'] == 739, msg

            # Check default attribute too
            msg = ('Expected 839 points tagged with default attribute "%s", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts[DEFAULT_ATTRIBUTE]))
            assert counts[DEFAULT_ATTRIBUTE] == 839, msg

            msg = 'Affected and not affected does not add up'
            assert (counts[DEFAULT_ATTRIBUTE] +
                    counts['Not ' + DEFAULT_ATTRIBUTE]) == len(E), msg

        if len(H) == 1032:
            # The full version
            msg = ('Expected 2258 points tagged with category "High", '
                   'but got only %i' % counts['High'])
            assert counts['High'] == 2258, msg

            msg = ('Expected 1190 points tagged with category "Very High", '
                   'but got only %i' % counts['Very High'])
            assert counts['Very High'] == 1190, msg

            # Check default attribute too
            msg = ('Expected 3452 points tagged with default attribute '
                   '"%s = True", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts[DEFAULT_ATTRIBUTE]))
            assert counts[DEFAULT_ATTRIBUTE] == 3452, msg

            msg = ('Expected 76 points tagged with default attribute '
                   '"%s = False", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts['Not ' + DEFAULT_ATTRIBUTE]))
            assert counts['Not ' + DEFAULT_ATTRIBUTE] == 76, msg

            msg = 'Affected and not affected does not add up'
            assert (counts[DEFAULT_ATTRIBUTE] +
                    counts['Not ' + DEFAULT_ATTRIBUTE]) == len(E), msg

        # for key in counts:
        #    print key, counts[key]

    test_interpolation_from_polygons_multiple.slow = True

    def test_interpolation_from_polygons_error_handling(self):
        """Interpolation using polygons handles input errors as expected

        This catches situation where input data have different projections
        This is a test for interpolation (issue #48)
        """

        # Input data
        hazard_filename = ('%s/tsunami_polygon.shp' % TESTDATA)  # UTM
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)  # GEO

        # Read input data
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        # Check projection mismatch is caught
        try:
            assign_hazard_values_to_exposure_data(H, E)
        except VerificationError, e:
            msg = ('Projection mismatch should have been caught: %s'
                   % str(e))
            assert 'Projections' in str(e), msg
        else:
            msg = 'Should have raised error about projection mismatch'
            raise Exception(msg)

    test_interpolation_from_polygons_error_handling.slow = True

    def test_line_clipping_by_polygon(self):
        """Multiple lines are clipped correctly by complex polygon
        """

        # Test data

        # Polygon 799  (520 x 2)
        polygon_filename = ('%s/test_poly.txt' % TESTDATA)
        # 156 composite lines
        lines_filename = ('%s/test_lines.pck' % TESTDATA)

        # Read
        test_polygon = []
        fid = open(polygon_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            test_polygon.append([float(fields[0]), float(fields[1])])
        test_polygon = ensure_numeric(test_polygon)

        fid = open(lines_filename)
        test_lines = cPickle.load(fid)
        fid.close()

        # Clip
        inside_lines, outside_lines = clip_lines_by_polygon(test_lines,
                                                            test_polygon)

        # Convert dictionaries to lists of lines (to fit test)
        inside_line_geometry = line_dictionary_to_geometry(inside_lines)
        outside_line_geometry = line_dictionary_to_geometry(outside_lines)

        # These lines have compontes both inside and outside
        assert len(inside_line_geometry) == 14
        assert len(outside_line_geometry) == 167

        # Check that midpoints of each segment are correctly placed
        inside_centroids = []
        for line in inside_line_geometry:
            for i in range(len(line) - 1):
                seg0 = line[i]
                seg1 = line[i + 1]
                midpoint = (seg0 + seg1) / 2
                inside_centroids.append(midpoint)
                assert is_inside_polygon(midpoint, test_polygon)

        outside_centroids = []
        for line in outside_line_geometry:
            for i in range(len(line) - 1):
                seg0 = line[i]
                seg1 = line[i + 1]
                midpoint = (seg0 + seg1) / 2
                outside_centroids.append(midpoint)
                assert not is_inside_polygon(midpoint, test_polygon)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:  # True:
            P = Vector(geometry=[test_polygon])
            P.write_to_file('test_polygon.shp')

            L = Vector(geometry=test_lines, geometry_type='line')
            L.write_to_file('test_lines.shp')

            L = Vector(geometry=inside_line_geometry, geometry_type='line')
            L.write_to_file('inside_lines.shp')

            L = Vector(geometry=outside_line_geometry, geometry_type='line')
            L.write_to_file('outside_lines.shp')

            L = Vector(geometry=inside_centroids, geometry_type='point')
            L.write_to_file('inside_centroids.shp')

            L = Vector(geometry=outside_centroids, geometry_type='point')
            L.write_to_file('outside_centroids.shp')

        # Characterisation test based on against visual inspection with QGIS
        # print inside_line_geometry[6]
        assert numpy.allclose(inside_line_geometry[6],
                              [[122.23438722, -8.6277337],
                               [122.23316953, -8.62733247],
                               [122.23162128, -8.62683715],
                               [122.23156661, -8.62681168]])

        # print outside_line_geometry[5]
        assert numpy.allclose(outside_line_geometry[5],
                              [[122.18321143, -8.58901526],
                               [122.18353015, -8.58890024],
                               [122.18370883, -8.58884135],
                               [122.18376524, -8.58881115],
                               [122.18381025, -8.58878405],
                               [122.1838646, -8.58875119],
                               [122.18389685, -8.58873165],
                               [122.18394329, -8.58869283],
                               [122.18401084, -8.58862284],
                               [122.18408657, -8.58853526],
                               [122.18414936, -8.58845887],
                               [122.18425204, -8.58832279],
                               [122.18449009, -8.58804974],
                               [122.18457453, -8.58798668],
                               [122.18466284, -8.5878697]])

    test_line_clipping_by_polygon.slow = True

    def test_line_interpolation_from_polygons_one_poly(self):
        """Line clipping and interpolation using one polygon works

        This is a test for road interpolation (issue #55)
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/roads_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to polygon #799 to make test quick
        H = Vector(data=H_attributes[799:800],
                   geometry=H_geometry[799:800],
                   projection=H.get_projection())
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()
        E = read_layer(exposure_filename)

        # Test interpolation function
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()
        assert I.get_name() == 'depth'

        N = len(I_attributes)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:
            H.write_to_file('test_polygon.shp')
            E.write_to_file('test_lines.shp')
            I.write_to_file('interpolated_lines.shp')

        # Assert that all expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()

        # Attributes from polygons
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Attributes from original lines
        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # New attributes
        for name in [DEFAULT_ATTRIBUTE, 'polygon_id', 'parent_line_id']:
            msg = 'Did not find new attribute name "%s" in %s' % (name,
                                                                  I_names)
            # FIXME (Ole): Shapefiles cut name down to 10 characters.
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        counts = {}
        for i in range(N):

            # Check that default attribute is present
            attrs = I_attributes[i]
            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE]:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Check specific attribute
            category = I_attributes[i]['Category']
            if category is not None:
                assert category.lower() in ['high', 'very high']
                count += 1

        msg = ('Expected 14 lines tagged with category, '
               'but got only %i' % count)
        assert count == 14, msg
        assert len(I_geometry) == 14

        # Check default attribute too
        msg = ('Expected 14 segments tagged with default attribute '
               '"%s = True", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts[DEFAULT_ATTRIBUTE]))
        assert counts[DEFAULT_ATTRIBUTE] == 14, msg

        # Check against correctness verified in QGIS
        assert I_attributes[13]['highway'] == 'road'
        assert I_attributes[13]['osm_id'] == 69372744
        assert I_attributes[13]['polygon_id'] == 0
        assert I_attributes[13]['parent_line_id'] == 131

    test_line_interpolation_from_polygons_one_poly.slow = True

    def test_line_interpolation_from_multiple_polygons(self):
        """Line interpolation using multiple polygons works

        This is a test for road interpolation (issue #55)
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/roads_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to 500 polygons
        # (some e.g. #657 have thousands of vertices, others just a few)
        H = Vector(data=H_attributes[300:657] + H_attributes[658:800],
                   geometry=H_geometry[300:657] + H_geometry[658:800],
                   projection=H.get_projection())
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()
        E = read_layer(exposure_filename)

        # Test interpolation function
        # import time
        # t0 = time.time()
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')
        # print 'This took', time.time() - t0

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()
        assert I.get_name() == 'depth'

        N = len(I_attributes)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:  # True:
            H.write_to_file('test_polygon.shp')
            E.write_to_file('test_lines.shp')
            I.write_to_file('interpolated_lines.shp')

        # Assert that all expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()

        # Attributes from polygons
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Attributes from original lines
        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # New attributes
        for name in [DEFAULT_ATTRIBUTE, 'polygon_id', 'parent_line_id']:
            msg = 'Did not find new attribute name "%s" in %s' % (name,
                                                                  I_names)
            # FIXME (Ole): Shapefiles cut name down to 10 characters.
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        counts = {}
        for i in range(N):

            # Check that default attribute is present
            attrs = I_attributes[i]

            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE]:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Check specific attribute
            category = I_attributes[i]['Category']
            if category is not None:
                msg = 'category = %s' % category
                assert category.lower() in ['low', 'medium',
                                            'high', 'very high'], msg
                count += 1

        msg = ('Expected 103 lines tagged with category, '
               'but got only %i' % count)
        assert count == 103, msg
        assert len(I_geometry) == 103

        # Check default attribute too
        msg = ('Expected 103 segments tagged with default attribute '
               '"%s = True", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts[DEFAULT_ATTRIBUTE]))
        assert counts[DEFAULT_ATTRIBUTE] == 103, msg

        # Check against correctness verified in QGIS
        assert I_attributes[40]['highway'] == 'residential'
        assert I_attributes[40]['osm_id'] == 69373107
        assert I_attributes[40]['polygon_id'] == 111
        assert I_attributes[40]['parent_line_id'] == 54

        assert I_attributes[76]['highway'] == 'secondary'
        assert I_attributes[76]['Category'] == 'High'
        assert I_attributes[76]['osm_id'] == 69370718
        assert I_attributes[76]['polygon_id'] == 374
        assert I_attributes[76]['parent_line_id'] == 1

        assert I_attributes[85]['highway'] == 'secondary'
        assert I_attributes[85]['Category'] == 'Very High'
        assert I_attributes[85]['osm_id'] == 69371482
        assert I_attributes[85]['polygon_id'] == 453
        assert I_attributes[85]['parent_line_id'] == 133

    test_line_interpolation_from_multiple_polygons.slow = True

    def test_polygon_to_roads_interpolation_flood_example(self):
        """Roads can be tagged with values from flood polygons

        This is a test for road interpolation (issue #55)

        # The dataset is large: 2704 complex polygons
        and 108082 complex line features - so has been cut down
        in this test.

        The runtime for the whole set is in the order of more than
        1 hour. Cutting the number of lines down by a factor of 10 years
        brings it down to about 10 minutes (500 seconds).
        A factor of 100 gives about 1 minute.
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/rw_jakarta_singlepart.shp' % TESTDATA)
        exposure_filename = ('%s/indonesia_highway.shp' % EXPDATA)

        # Read all input data
        H = read_layer(hazard_filename)  # Polygons
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()
        assert len(H) == 2704

        E = read_layer(exposure_filename)  # Lines - this is slow to read
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()
        assert len(E) == 108082

        # Cut number of road features down
        # A factor of ten brings the runtime down to about 10 minutes.
        # A factor of ten brings the runtime down to less than 1 minute.
        E = Vector(data=E_attributes[:-1:100],
                   geometry=E_geometry[:-1:100],
                   projection=E.get_projection(),
                   geometry_type=E.geometry_type)

        # Test interpolation function
        # import time
        # t0 = time.time()
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')
        # print 'That took %f seconds' % (time.time() - t0)

        # TODO:
        # Keep only those roads that are marked FLOODPRONE == 'YES'

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        # Possibly generate files for visual inspection with e.g. QGis
        if False:
            L = Vector(geometry=H_geometry, geometry_type='polygon',
                       data=H_attributes)
            L.write_to_file('flood_polygon.shp')

            L = Vector(geometry=I_geometry, geometry_type='line',
                       data=I_attributes)
            L.write_to_file('flood_tagged_roads.shp')

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # FIXME (Ole): Finish this test
        # Check that attributes have been carried through
        # for i, attr in enumerate(I_attributes):
        #    pass
        #    # TODO
        # Check against correctness verified in QGIS
        # assert I_attributes[]['highway'] ==
        # assert I_attributes[]['osm_id'] ==
        # assert I_attributes[]['polygon_id'] ==
        # assert I_attributes[]['parent_line_id'] ==

    test_polygon_to_roads_interpolation_flood_example.slow = True

    def Xtest_polygon_to_roads_interpolation_jakarta_flood_example1(self):
        """Roads can be tagged with values from flood polygons

        This is a test for road interpolation (issue #55)

        # The dataset is: 2704 complex polygons and 18574 complex line features
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/rw_jakarta_singlepart.shp' % TESTDATA)
        exposure_filename = ('%s/jakarta_roads.shp' % EXPDATA)

        # Read all input data
        H = read_layer(hazard_filename)  # Polygons
        H_attributes = H.get_data()
        H_geometries = H.get_geometry()
        assert len(H) == 2704

        # Use only polygons marked as flood prone
        # to get the result quicker.
        cut_attributes = []
        cut_geometries = []
        for i in range(len(H)):
            val = H_attributes[i]['FLOODPRONE']
            if val is not None and val.lower().startswith('yes'):
                cut_attributes.append(H_attributes[i])
                cut_geometries.append(H_geometries[i])

        H = Vector(data=cut_attributes,
                   geometry=cut_geometries,
                   projection=H.get_projection(),
                   geometry_type=H.geometry_type)
        assert len(H) == 1011

        E = read_layer(exposure_filename)
        E_geometries = E.get_geometry()
        E_attributes = E.get_data()
        assert len(E) == 18574

        # Get statistics of road types
        road_types = {}
        E_attributes = E.get_data()
        for i in range(len(E)):
            roadtype = E_attributes[i]['TYPE']
            if roadtype in road_types:
                road_types[roadtype] += 1
            else:
                road_types[roadtype] = 0

        # for att in road_types:
        #    print att, road_types[att]
        assert road_types['residential'] == 14853

        # Remove residental roads
        cut_attributes = []
        cut_geometries = []
        for i in range(len(E)):
            val = E_attributes[i]['TYPE']
            if val != 'residential':
                cut_attributes.append(E_attributes[i])
                cut_geometries.append(E_geometries[i])

        # Cut even further for the purpose of testing
        E = Vector(data=cut_attributes[:-1:5],
                   geometry=cut_geometries[:-1:5],
                   projection=E.get_projection(),
                   geometry_type=E.geometry_type)
        assert len(E) == 744

        # Test interpolation function
        # import time
        # t0 = time.time()
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')
        # print ('Using 2704 individual polygons took %f seconds'
        #       % (time.time() - t0))
        # I.write_to_file('flood_prone_roads_jakarta_individual.shp')

        # Check against correctness verified in QGIS
        I_attributes = I.get_data()
        assert I_attributes[198]['TYPE'] == 'secondary'
        assert I_attributes[198]['NAME'] == 'Lingkar Mega Kuningan'
        assert I_attributes[198]['KEL_NAME'] == 'KUNINGAN TIMUR'
        assert I_attributes[198]['polygon_id'] == 235
        assert I_attributes[198]['parent_line_id'] == 333

    Xtest_polygon_to_roads_interpolation_jakarta_flood_example1.slow = True

    def Xtest_polygon_to_roads_interpolation_jakarta_flood_merged(self):
        """Roads can be tagged with values from flood polygons

        This is a test for road interpolation (issue #55)

        # The dataset is: 59 merged complex polygons and 18574
        # complex line features
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/RW_2007_dissolve.shp' % TESTDATA)
        exposure_filename = ('%s/jakarta_roads.shp' % EXPDATA)

        # Read all input data
        H = read_layer(hazard_filename)  # Polygons
        # H_attributes = H.get_data()
        # H_geometries = H.get_geometry()
        print len(H)
        assert len(H) == 35

        E = read_layer(exposure_filename)
        E_geometries = E.get_geometry()
        # E_attributes = E.get_data()
        assert len(E) == 18574

        # Get statistics of road types
        road_types = {}
        E_attributes = E.get_data()
        for i in range(len(E)):
            roadtype = E_attributes[i]['TYPE']
            if roadtype in road_types:
                road_types[roadtype] += 1
            else:
                road_types[roadtype] = 0

        # for att in road_types:
        #    print att, road_types[att]
        assert road_types['residential'] == 14853

        # Remove residental roads
        cut_attributes = []
        cut_geometries = []
        for i in range(len(E)):
            val = E_attributes[i]['TYPE']
            if val != 'residential':
                cut_attributes.append(E_attributes[i])
                cut_geometries.append(E_geometries[i])

        # Cut even further for the purpose of testing
        E = Vector(data=cut_attributes[:-1:5],
                   geometry=cut_geometries[:-1:5],
                   projection=E.get_projection(),
                   geometry_type=E.geometry_type)
        assert len(E) == 744

        # Test interpolation function
        import time
        t0 = time.time()
        print
        print 'start'
        I = assign_hazard_values_to_exposure_data(H, E,
                                                  layer_name='depth')
        print 'Using merged polygon took %f seconds' % (time.time() - t0)
        I.write_to_file('flood_prone_roads_jakarta_merged.shp')

        # Check against correctness verified in QGIS
        # I_attributes = I.get_data()
        # assert I_attributes[198]['TYPE'] == 'secondary'
        # assert I_attributes[198]['NAME'] == 'Lingkar Mega Kuningan'
        # assert I_attributes[198]['KEL_NAME'] == 'KUNINGAN TIMUR'
        # assert I_attributes[198]['polygon_id'] == 235
        # assert I_attributes[198]['parent_line_id'] == 333

    Xtest_polygon_to_roads_interpolation_jakarta_flood_merged.slow = True

    def test_layer_integrity_raises_exception(self):
        """Layers without keywords raise exception."""
        population = 'Population_Jakarta_geographic.asc'
        function_id = 'FloodEvacuationRasterHazardFunction'

        hazard_layers = ['Flood_Current_Depth_Jakarta_geographic.asc',
                         'Flood_Design_Depth_Jakarta_geographic.asc']

        for i, filename in enumerate(hazard_layers):
            hazard_filename = join(HAZDATA, filename)
            exposure_filename = join(TESTDATA, population)

            # Get layers using API
            hazard_layer = read_layer(hazard_filename)
            exposure_layer = read_layer(exposure_filename)

            impact_function = self.impact_function_manager.get(
                function_id)

            # Call impact calculation engine normally
            calculate_impact(layers=[hazard_layer, exposure_layer],
                             impact_function=impact_function)

            # Make keyword value empty and verify exception is raised
            expected_layer_purpose = exposure_layer.keywords['layer_purpose']
            exposure_layer.keywords['layer_purpose'] = ''
            try:
                calculate_impact(layers=[hazard_layer, exposure_layer],
                                 impact_function=impact_function)
            except VerificationError, e:
                # Check expected error message
                assert 'No value found' in str(e)
            else:
                msg = 'Empty keyword value should have raised exception'
                raise Exception(msg)

            # Restore for next test
            exposure_layer.keywords['layer_purpose'] = expected_layer_purpose

            # Remove critical keywords and verify exception is raised
            if i == 0:
                del hazard_layer.keywords['layer_purpose']
            else:
                del hazard_layer.keywords['layer_mode']

            try:
                calculate_impact(layers=[hazard_layer, exposure_layer],
                                 impact_function=impact_function)
            except VerificationError, e:
                # Check expected error message
                assert 'did not have required keyword' in str(e)
            else:
                msg = 'Missing keyword should have raised exception'
                raise Exception(msg)

    test_layer_integrity_raises_exception.slow = True

    def test_erf(self):
        """Test ERF approximation

        Reference data obtained from scipy as follows:
        A = (numpy.arange(20) - 10.) / 2
        F = scipy.special.erf(A)

        See also table at http://en.wikipedia.org/wiki/Error_function
        """

        # Simple tests
        assert numpy.allclose(erf(0), 0.0, rtol=1.0e-6, atol=1.0e-6)

        x = erf(1)
        r = 0.842700792949715
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = erf(0.5)
        r = 0.5204999
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = erf(3)
        r = 0.999977909503001
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Reference data
        R = [
            -1., -1., -0.99999998, -0.99999926, -0.99997791, -0.99959305,
            -0.99532227, -0.96610515, -0.84270079, -0.52049988, 0.,
            0.52049988, 0.84270079, 0.96610515, 0.99532227, 0.99959305,
            0.99997791, 0.99999926, 0.99999998, 1.]

        A = (numpy.arange(20) - 10.) / 2
        X = erf(A)
        msg = ('ERF was not correct. I got %s but expected %s' %
               (str(X), str(R)))
        assert numpy.allclose(X, R, atol=1.0e-6, rtol=1.0e-12), msg

    def test_normal_cdf(self):
        """Test Normal Cumulative Distribution Function

        Reference data obtained from scipy as follows:

        A = (numpy.arange(20) - 10.) / 5
        R = scipy.stats.norm.cdf(A)
        """

        # Simple tests
        x = normal_cdf(0.0)
        r = 0.5
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = normal_cdf(0.5)
        r = 0.69146246127401312
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = normal_cdf(3.50)
        r = 0.99976737092096446
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Out of bounds
        x = normal_cdf(-6)
        r = 0
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-6), msg

        x = normal_cdf(10)
        r = 1
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Reference data
        R = [0.02275013, 0.03593032, 0.05479929, 0.08075666, 0.11506967,
             0.15865525, 0.2118554, 0.27425312, 0.34457826, 0.42074029, 0.5,
             0.57925971, 0.65542174, 0.72574688, 0.7881446, 0.84134475,
             0.88493033, 0.91924334, 0.94520071, 0.96406968]

        A = (numpy.arange(20) - 10.) / 5
        X = normal_cdf(A)
        msg = ('CDF was not correct. I got %s but expected %s' %
               (str(X), str(R)))
        assert numpy.allclose(X, R, atol=1.0e-6, rtol=1.0e-12), msg

    def test_lognormal_cdf(self):
        """Test Log-normal Cumulative Distribution Function

        Reference data obtained from scipy as follows:

        A = (numpy.arange(20) - 10.) / 5
        R = scipy.stats.lognorm.cdf(A)
        """

        # Suppress warnings about invalid value in multiply and divide zero
        # http://comments.gmane.org/gmane.comp.python.numeric.general/43218
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.seterr.html
        old_numpy_setting = numpy.seterr(divide='ignore')

        # Simple tests
        x = log_normal_cdf(0.0)
        r = normal_cdf(numpy.log(0.0))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg
        numpy.seterr(**old_numpy_setting)

        x = log_normal_cdf(0.5)
        r = normal_cdf(numpy.log(0.5))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = log_normal_cdf(3.50)
        r = normal_cdf(numpy.log(3.5))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Out of bounds
        x = log_normal_cdf(10)
        r = normal_cdf(numpy.log(10))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-6), msg

if __name__ == '__main__':
    suite = unittest.makeSuite(TestEngine, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
