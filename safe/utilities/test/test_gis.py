# coding=utf-8
"""Test for GIS utilities functions."""
import unittest

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QVariant

from safe.utilities.gis import (
    layer_attribute_names,
    is_polygon_layer,
    validate_geo_array)
from safe.test.utilities import (
    clone_shp_layer,
    clone_raster_layer,
    test_data_path,
    get_qgis_app)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestQGIS(unittest.TestCase):
    def test_get_layer_attribute_names(self):
        """Test we can get the correct attributes back"""
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))

        # with good attribute name
        attributes, position = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String],
            'TEST_STR')
        expected_attributes = ['KAB_NAME', 'TEST_STR', 'TEST_INT']
        expected_position = 1
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        self.assertEqual(attributes, expected_attributes, message)
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        self.assertEqual(position, expected_position, message)

        # with non existing attribute name
        attributes, position = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String],
            'MISSING_ATTR')
        expected_attributes = ['KAB_NAME', 'TEST_STR', 'TEST_INT']
        expected_position = None
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        self.assertEqual(attributes, expected_attributes, message)
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        self.assertEqual(position, expected_position, message)

        # with raster layer
        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        attributes, position = layer_attribute_names(layer, [], '')
        message = 'Should return None, None for raster layer, got %s, %s' % (
            attributes, position)
        assert (attributes is None and position is None), message

    def test_is_polygonal_layer(self):
        """Test we can get the correct attributes back"""
        # Polygon layer
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=test_data_path('boundaries'))
        message = 'isPolygonLayer, %s layer should be polygonal' % layer
        self.assertTrue(is_polygon_layer(layer), message)

        # Point layer
        layer = clone_shp_layer(
            name='volcano_point',
            include_keywords=True,
            source_directory=test_data_path('hazard'))
        message = '%s layer should be polygonal' % layer
        self.assertFalse(is_polygon_layer(layer), message)

        layer = clone_raster_layer(
            name='padang_tsunami_mw8',
            extension='.tif',
            include_keywords=True,
            source_directory=test_data_path('hazard')
        )
        message = ('%s raster layer should not be polygonal' % layer)
        self.assertFalse(is_polygon_layer(layer), message)

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
