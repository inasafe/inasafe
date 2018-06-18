# coding=utf-8

"""Test for GIS utilities functions."""

import unittest

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsRectangle

from safe.definitions.constants import INASAFE_TEST
from safe.utilities.gis import (
    is_polygon_layer,
    is_raster_y_inverted,
    wkt_to_rectangle,
    validate_geo_array)
from safe.test.utilities import (
    clone_raster_layer,
    load_test_vector_layer,
    load_test_raster_layer,
    standard_data_path,
    get_qgis_app)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


class TestQGIS(unittest.TestCase):

    def test_is_polygonal_layer(self):
        """Test we can get the correct attributes back."""
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

        # Raster layer
        layer = clone_raster_layer(
            name='earthquake',
            extension='.tif',
            include_keywords=True,
            source_directory=standard_data_path('hazard')
        )
        message = ('%s raster layer should not be polygonal' % layer)
        self.assertFalse(is_polygon_layer(layer), message)

    def test_raster_y_inverted(self):
        """Test if we can detect an upside down raster."""
        # We should have one test with an inverted raster but as it's not
        # usual, I'm not going to spend time.
        layer = load_test_raster_layer('gisv4', 'hazard', 'earthquake.asc')
        self.assertFalse(is_raster_y_inverted(layer))

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


if __name__ == '__main__':
    unittest.main()
