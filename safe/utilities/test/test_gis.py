# coding=utf-8
"""Test for GIS utilities functions."""
import unittest

# noinspection PyUnresolvedReferences
import qgis
from PyQt4.QtCore import QVariant
from safe.gui.tools.test.test_keywords_dialog import (
    make_polygon_layer,
    clone_padang_layer,
    make_point_layer)
from safe.utilities.gis import layer_attribute_names, is_polygon_layer


class TestQGIS(unittest.TestCase):
    def test_get_layer_attribute_names(self):
        """Test we can get the correct attributes back"""
        layer = make_polygon_layer()

        # with good attribute name
        attributes, position = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String], 'TEST_STRIN')  # Not a typo...
        expected_attributes = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        expected_position = 2
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        assert (attributes == expected_attributes), message
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        assert (position == expected_position), message

        # with non existing attribute name
        attributes, position = layer_attribute_names(
            layer,
            [QVariant.Int, QVariant.String],
            'MISSING_ATTR')
        expected_attributes = ['KAB_NAME', 'TEST_INT', 'TEST_STRIN']
        expected_position = None
        message = 'expected_attributes, got %s, expected %s' % (
            attributes, expected_attributes)
        assert (attributes == expected_attributes), message
        message = 'expected_position, got %s, expected %s' % (
            position, expected_position)
        assert (position == expected_position), message

        # with raster layer
        layer, _ = clone_padang_layer()
        attributes, position = layer_attribute_names(layer, [], '')
        message = 'Should return None, None for raster layer, got %s, %s' % (
            attributes, position)
        assert (attributes is None and position is None), message

    def test_is_polygonal_layer(self):
        """Test we can get the correct attributes back"""
        layer = make_polygon_layer()
        message = 'isPolygonLayer, %s layer should be polygonal' % layer
        assert is_polygon_layer(layer), message

        layer = make_point_layer()
        message = '%s layer should be polygonal' % layer
        assert not is_polygon_layer(layer), message

        layer, _ = clone_padang_layer()
        message = ('%s raster layer should not be polygonal' % layer)
        assert not is_polygon_layer(layer), message


if __name__ == '__main__':
    unittest.main()
