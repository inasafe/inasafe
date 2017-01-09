# coding=utf-8
"""Test for GIS utilities functions."""
import unittest
import numpy

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from os.path import join
from qgis.core import QgsRectangle

from safe.utilities.gis import (
    is_polygon_layer,
    wkt_to_rectangle,
    validate_geo_array)
from safe.test.utilities import (
    TESTDATA,
    HAZDATA,
    clone_raster_layer,
    load_test_vector_layer,
    standard_data_path,
    get_qgis_app)
from safe.utilities.gis import get_optimal_extent
from safe.common.exceptions import BoundingBoxError, InsufficientOverlapError
from safe.storage.core import read_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestQGIS(unittest.TestCase):

    def test_is_polygonal_layer(self):
        """Test we can get the correct attributes back"""
        # Polygon layer
        layer = load_test_vector_layer(
            'aggregation',
            'district_osm_jakarta.geojson',
            clone=True
        )
        message = 'isPolygonLayer, %s layer should be polygonal' % layer
        self.assertTrue(is_polygon_layer(layer), message)

        # Point layer
        layer = load_test_vector_layer('hazard', 'volcano_point.geojson')
        message = '%s layer should be polygonal' % layer
        self.assertFalse(is_polygon_layer(layer), message)

        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=standard_data_path('hazard')
        )
        message = ('%s raster layer should not be polygonal' % layer)
        self.assertFalse(is_polygon_layer(layer), message)

    def test_rectangle_from_wkt(self):
        """Test we can a create a rectangle from a WKT."""
        rectangle = wkt_to_rectangle('POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))')
        self.assertTrue(isinstance(rectangle, QgsRectangle))

        rectangle = wkt_to_rectangle('POLYGON ((0 1, 1 1, 1 0, 0 0))')
        self.assertIsNone(rectangle)

    def test_validate_geo_array(self):
        """Test validate geographic extent method.

        .. versionadded:: 3.2
        """
        # Normal case
        min_longitude = 20.389938354492188
        min_latitude = -34.10782492987083
        max_longitude = 20.712661743164062
        max_latitude = -34.008273470938335
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertTrue(validate_geo_array(extent))

        # min_latitude >= max_latitude
        min_latitude = 34.10782492987083
        max_latitude = -34.008273470938335
        min_longitude = 20.389938354492188
        max_longitude = 20.712661743164062
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

        # min_longitude >= max_longitude
        min_latitude = -34.10782492987083
        max_latitude = -34.008273470938335
        min_longitude = 34.10782492987083
        max_longitude = -34.008273470938335
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

        # min_latitude < -90 or > 90
        min_latitude = -134.10782492987083
        max_latitude = -34.008273470938335
        min_longitude = 20.389938354492188
        max_longitude = 20.712661743164062
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

        # max_latitude < -90 or > 90
        min_latitude = -9.10782492987083
        max_latitude = 91.10782492987083
        min_longitude = 20.389938354492188
        max_longitude = 20.712661743164062
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

        # min_longitude < -180 or > 180
        min_latitude = -34.10782492987083
        max_latitude = -34.008273470938335
        min_longitude = -184.10782492987083
        max_longitude = 20.712661743164062
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

        # max_longitude < -180 or > 180
        min_latitude = -34.10782492987083
        max_latitude = -34.008273470938335
        min_longitude = 20.389938354492188
        max_longitude = 180.712661743164062
        extent = [min_longitude, min_latitude, max_longitude, max_latitude]
        self.assertFalse(validate_geo_array(extent))

    def test_get_optimal_extent(self):
        """Optimal extent is calculated correctly"""

        exposure_path = join(TESTDATA, 'Population_2010.asc')
        hazard_path = join(HAZDATA, 'Lembang_Earthquake_Scenario.asc')

        # Expected data
        haz_metadata = {
            'bounding_box': (
                105.3000035,
                -8.3749994999999995,
                110.2914705,
                -5.5667784999999999),
            'resolution': (
                0.0083330000000000001,
                0.0083330000000000001)}

        exp_metadata = {
            'bounding_box': (
                94.972335000000001,
                -11.009721000000001,
                141.0140016666665,
                6.0736123333332639),
            'resolution': (
                0.0083333333333333003,
                0.0083333333333333003)}

        # Verify relevant metada is ok
        H = read_layer(hazard_path)
        E = read_layer(exposure_path)

        hazard_bbox = H.get_bounding_box()
        assert numpy.allclose(hazard_bbox, haz_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_bbox = E.get_bounding_box()
        assert numpy.allclose(exposure_bbox, exp_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        hazard_res = H.get_resolution()
        assert numpy.allclose(hazard_res, haz_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_res = E.get_resolution()
        assert numpy.allclose(exposure_res, exp_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        # First, do some examples that produce valid results
        ref_box = [105.3000035, -8.3749995, 110.2914705, -5.5667785]
        view_port = [94.972335, -11.009721, 141.014002, 6.073612]

        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        # testing with viewport clipping disabled
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, None)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        view_port = [105.3000035,
                     -8.3749994999999995,
                     110.2914705,
                     -5.5667784999999999]
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Very small viewport fully inside other layers
        view_port = [106.0, -6.0, 108.0, -5.8]
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)

        assert numpy.allclose(bbox, view_port,
                              rtol=1.0e-12, atol=1.0e-12)

        # viewport that intersects hazard layer
        view_port = [107.0, -6.0, 112.0, -3.0]
        ref_box = [107, -6, 110.2914705, -5.5667785]

        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Then one where boxes don't overlap
        view_port = [105.3, -4.3, 110.29, -2.5]
        try:
            get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'did not overlap' in str(e), message
        else:
            message = ('Non ovelapping bounding boxes should have raised '
                       'an exception')
            raise Exception(message)

        # Try with wrong input data
        try:
            # noinspection PyTypeChecker
            get_optimal_extent(haz_metadata, exp_metadata, view_port)
        except BoundingBoxError:
            # good this was expected
            pass
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            # noinspection PyTypeChecker
            get_optimal_extent(None, None, view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'cannot be None' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            # noinspection PyTypeChecker
            get_optimal_extent('aoeush', 'oeuuoe', view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Instead i got "aoeush"' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)


if __name__ == '__main__':
    unittest.main()
