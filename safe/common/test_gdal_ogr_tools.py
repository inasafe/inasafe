# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : assefay@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'assefay@gmail.com'
__date__ = '20/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
import unittest
from osgeo import ogr
from safe.common.testing import UNITDATA

from safe.common.gdal_ogr_tools import (
    polygonize_thresholds)


class TestGDALOGRTools(unittest.TestCase):

    def test_polygonize_thresholds(self):
        """Test polygonize raster using gdal
        """

        raster_name = os.path.join(
            UNITDATA,
            'hazard',
            'jakarta_flood_design.tif')

        (inside_file_name, inside_layer_name, outside_file_name, \
             outside_layer_name) = \
             polygonize_thresholds(raster_name, 0.5)

        driver = ogr.GetDriverByName('ESRI Shapefile')

        dataSource = driver.Open(inside_file_name, 0)
        layer = dataSource.GetLayer()
        featureCount = layer.GetFeatureCount()
        #print 'inside %s' % (inside_file_name)
        self.assertEquals(featureCount, 3)

        dataSource2 = driver.Open(outside_file_name, 0)
        layer2 = dataSource2.GetLayer()
        featureCount2 = layer2.GetFeatureCount()
        #print 'outside %s' % (outside_file_name)
        self.assertEquals(featureCount2, 1)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestGDALOGRTools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
