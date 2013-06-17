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

# Add parent directory to path to make test aware of other modules
# We should be able to remove this now that we use env vars. TS
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe_qgis.zonal_stats import calculateZonalStats
from safe_qgis.utilities import getErrorMessage
from safe_qgis.utilities_test import (
    unitTestDataPath,
    loadLayer,
    getQgisTestApp)
from safe_qgis.exceptions import StyleError
from safe_qgis.safe_interface import UNITDATA

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class ZonalStatsTest(unittest.TestCase):
    """Tests for zonal related functions.
    """
    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_zonal(self):
        """Test that zonal stats returns the expected output."""
        myRasterLayer, _ = loadLayer(os.path.join(
            UNITDATA, 'other', 'tenbytenraster.asc'))
        myVectorLayer, _ = loadLayer(os.path.join(
            UNITDATA, 'other', 'zonal_polygons.shp'))
        myResult = calculateZonalStats(
            theRasterLayer=myRasterLayer,
            thePolygonLayer=myVectorLayer)
        assert myResult
