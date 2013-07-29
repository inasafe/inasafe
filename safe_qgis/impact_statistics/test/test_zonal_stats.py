"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Zonal Tests.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '17/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import sys
import os

from qgis.core import QgsRectangle

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe_qgis.impact_statistics.zonal_stats import (
    calculate_zonal_stats, intersection_box)
from safe_qgis.utilities.utilities_for_testing import (
    load_layer, get_qgis_app)
from safe_qgis.safe_interface import UNITDATA

QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()


class ZonalStatsTest(unittest.TestCase):
    """Tests for zonal related functions.

        # Note there is a wierd issue on OSX where
        # geometry comes back as none all the time when testing
        # running the test again will randomly succeed in fetching geometries
        # properly.
    """
    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_zonal(self):
        """Test that zonal stats returns the expected output."""
        myRasterLayer, _ = load_layer(os.path.join(
            UNITDATA, 'other', 'tenbytenraster.asc'))
        myVectorLayer, _ = load_layer(os.path.join(
            UNITDATA, 'other', 'zonal_polygons.shp'))
        myResult = calculate_zonal_stats(
            raster_layer=myRasterLayer,
            polygon_layer=myVectorLayer)
        myExpectedResult = {
            0L: {'count': 4, 'sum': 34.0, 'mean': 8.5},  # BR polygon
            1L: {'count': 9, 'sum': 36.0, 'mean': 4.0},  # center polygon
            2L: {'count': 4, 'sum': 2.0, 'mean': 0.5},  # TL polygon
            3L: {'count': 4, 'sum': 2.0, 'mean': 0.5},  # BL Polygon
            4L: {'count': 4, 'sum': 34.0, 'mean': 8.5}}  # TR polygon
        self.maxDiff = None
        self.assertDictEqual(myExpectedResult, myResult)

    def test_zonal_with_exact_cell_boundaries(self):
        """Test that zonal stats returns the expected output."""
        myRasterLayer, _ = load_layer(os.path.join(
            UNITDATA, 'other', 'tenbytenraster.asc'))
        # Note this is a matrix of 11x11 polys - one per cell
        # and one poly extending beyond to the right of each row
        # and one poly extending beyond the bottom of each col
        myVectorLayer, _ = load_layer(os.path.join(
            UNITDATA, 'other', 'ten_by_ten_raster_as_polys.shp'))
        myResult = calculate_zonal_stats(
            raster_layer=myRasterLayer,
            polygon_layer=myVectorLayer)
        myExpectedResult = {
            0L: {'count': 1.0, 'sum': 0.0, 'mean': 0.0},  # TL polygon
            9L: {'count': 1.0, 'sum': 9.0, 'mean': 9.0},  # TR polygon
            25L: {'count': 1.0, 'sum': 3.0, 'mean': 3.0},  # Central polygon
            88L: {'count': 1.0, 'sum': 0.0, 'mean': 0.0},  # BL polygon
            108L: {'count': 1.0, 'sum': 9.0, 'mean': 9.0}}  # BR polygon
        # We will just check TL, TR, Middle, BL and BR cells
        myResult = {
            0L: myResult[0L],
            9L: myResult[9L],
            25L: myResult[25L],
            88L: myResult[88L],
            108L: myResult[108L]}
        self.maxDiff = None
        self.assertDictEqual(myExpectedResult, myResult)

    def test_cellInfoForBBox(self):
        """Test that cell info for bbox returns expected values."""
        myRasterBox = QgsRectangle(1535375.0, 5083255.0, 1535475.0, 5083355.0)
        myFeatureBox = QgsRectangle(1535455.0, 5083345.0, 1535465.0, 5083355.0)
        myCellSizeX = 10
        myCellSizeY = 10
        myOffsetX = 8
        myOffsetY = 0
        myCellsX = myCellsY = 1
        myExpectedResult = myOffsetX, myOffsetY, myCellsX, myCellsY
        myResult = intersection_box(
            myRasterBox, myFeatureBox, myCellSizeX, myCellSizeY)
        self.assertTupleEqual(myExpectedResult, myResult)

        # Now try with a poly bbox slightly larger than 1 px (1535470)
        myCellsX = 2
        myExpectedResult = myOffsetX, myOffsetY, myCellsX, myCellsY
        myFeatureBox = QgsRectangle(1535455.0, 5083345.0, 1535470.0, 5083355.0)
        myResult = intersection_box(
            myRasterBox, myFeatureBox, myCellSizeX, myCellSizeY)
        self.assertTupleEqual(myExpectedResult, myResult)
