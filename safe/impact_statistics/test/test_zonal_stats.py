# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Zonal Tests.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '17/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import os

from qgis.core import QgsRectangle

from safe.impact_statistics.zonal_stats import (
    calculate_zonal_stats, intersection_box)
from safe.test.utilities import (
    load_layer,
    test_data_path,
    get_qgis_app)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ZonalStatsTest(unittest.TestCase):
    """Tests for zonal related functions.

        # Note there is a weird issue on OSX where
        # geometry comes back as none all the time when testing
        # running the test again will randomly succeed in fetching geometries
        # properly.
    """
    # noinspection PyPep8Naming
    def setUp(self):
        os.environ['INASAFE_LANG'] = 'en'

    # noinspection PyPep8Naming
    def tearDown(self):
        pass

    def test_zonal(self):
        """Test that zonal stats returns the expected output."""
        raster_layer, _ = load_layer(
            test_data_path('other', 'tenbytenraster.asc'))
        vector_layer, _ = load_layer(
            test_data_path('other', 'zonal_polygons.shp'))
        result = calculate_zonal_stats(
            raster_layer=raster_layer,
            polygon_layer=vector_layer)
        expected_result = {
            0L: {'count': 4, 'sum': 34.0, 'mean': 8.5},  # BR polygon
            1L: {'count': 9, 'sum': 36.0, 'mean': 4.0},  # center polygon
            2L: {'count': 4, 'sum': 2.0, 'mean': 0.5},  # TL polygon
            3L: {'count': 4, 'sum': 2.0, 'mean': 0.5},  # BL Polygon
            4L: {'count': 4, 'sum': 34.0, 'mean': 8.5}}  # TR polygon
        # noinspection PyPep8Naming
        self.maxDiff = None
        self.assertDictEqual(expected_result, result)

    def test_zonal_with_exact_cell_boundaries(self):
        """Test that zonal stats returns the expected output."""
        raster_layer, _ = load_layer(
            test_data_path('other', 'tenbytenraster.asc'))
        # Note this is a matrix of 11x11 polygons - one per cell
        # and one poly extending beyond to the right of each row
        # and one poly extending beyond the bottom of each col
        vector_layer, _ = load_layer(
            test_data_path('other', 'ten_by_ten_raster_as_polys.shp'))
        result = calculate_zonal_stats(
            raster_layer=raster_layer,
            polygon_layer=vector_layer)
        expected_result = {
            0L: {'count': 1.0, 'sum': 0.0, 'mean': 0.0},  # TL polygon
            9L: {'count': 1.0, 'sum': 9.0, 'mean': 9.0},  # TR polygon
            25L: {'count': 1.0, 'sum': 3.0, 'mean': 3.0},  # Central polygon
            88L: {'count': 1.0, 'sum': 0.0, 'mean': 0.0},  # BL polygon
            108L: {'count': 1.0, 'sum': 9.0, 'mean': 9.0}}  # BR polygon
        # We will just check TL, TR, Middle, BL and BR cells
        result = {
            0L: result[0L],
            9L: result[9L],
            25L: result[25L],
            88L: result[88L],
            108L: result[108L]}
        # noinspection PyPep8Naming
        self.maxDiff = None
        self.assertDictEqual(expected_result, result)

    def test_cell_info_for_bbox(self):
        """Test that cell info for bbox returns expected values."""
        raster_box = QgsRectangle(1535375.0, 5083255.0, 1535475.0, 5083355.0)
        feature_box = QgsRectangle(1535455.0, 5083345.0, 1535465.0, 5083355.0)
        cell_size_x = 10
        cell_size_y = 10
        offset_x = 8
        offset_y = 0
        cells_x = cells_y = 1
        expected_result = offset_x, offset_y, cells_x, cells_y
        result = intersection_box(
            raster_box, feature_box, cell_size_x, cell_size_y)
        self.assertTupleEqual(expected_result, result)

        # Now try with a poly bbox slightly larger than 1 px (1535470)
        cells_x = 2
        expected_result = offset_x, offset_y, cells_x, cells_y
        feature_box = QgsRectangle(1535455.0, 5083345.0, 1535470.0, 5083355.0)
        result = intersection_box(
            raster_box, feature_box, cell_size_x, cell_size_y)
        self.assertTupleEqual(expected_result, result)
