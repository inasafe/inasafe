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

import unittest
from osgeo import ogr

from safe.gis.gdal_ogr_tools import polygonize_thresholds, polygonize
from safe.test.utilities import standard_data_path


class TestGDALOGRTools(unittest.TestCase):

    def test_polygonize_thresholds(self):
        """Test polygonize raster using gdal with some thresholds."""

        raster_path = standard_data_path('hazard', 'jakarta_flood_design.tif')

        inside_file_name, inside_layer_name, outside_file_name, \
            outside_layer_name = polygonize_thresholds(
                raster_path, 0.5)

        # Syntactic sugar to ignore unused vars.
        _ = inside_layer_name
        _ = outside_layer_name

        driver = ogr.GetDriverByName('ESRI Shapefile')

        data_source = driver.Open(inside_file_name, 0)
        layer = data_source.GetLayer()
        feature_count = layer.GetFeatureCount()
        # print 'inside %s' % (inside_file_name)
        self.assertEquals(feature_count, 3)

        data_source2 = driver.Open(outside_file_name, 0)
        layer2 = data_source2.GetLayer()
        feature_count2 = layer2.GetFeatureCount()
        # print 'outside %s' % (outside_file_name)
        self.assertEquals(feature_count2, 1)

    def test_polygonize(self):
        """Test if we can polygonize a raster using GDAL."""

        raster_path = standard_data_path(
            'hazard', 'classified_flood_20_20.asc')
        driver = ogr.GetDriverByName('ESRI Shapefile')
        expected_field_name = 'my_field'

        shapefile = polygonize(raster_path, 1, expected_field_name)
        data_source = driver.Open(shapefile, 0)
        layer = data_source.GetLayer()

        layer_definition = layer.GetLayerDefn()
        field_name = layer_definition.GetFieldDefn(0).GetName()
        self.assertEqual(field_name, expected_field_name)

        self.assertEquals(layer.GetFeatureCount(), 400)

        layer.SetAttributeFilter('%s = 1' % expected_field_name)
        self.assertEquals(layer.GetFeatureCount(), 133)

        layer.SetAttributeFilter('%s = 2' % expected_field_name)
        self.assertEquals(layer.GetFeatureCount(), 134)

        layer.SetAttributeFilter('%s = 3' % expected_field_name)
        self.assertEquals(layer.GetFeatureCount(), 133)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestGDALOGRTools, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
