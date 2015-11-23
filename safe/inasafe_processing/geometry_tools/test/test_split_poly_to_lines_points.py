# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest
import logging
from os import listdir, remove
from os.path import dirname, basename, join, splitext

from safe.test.utilities import test_data_path, get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

LOGGER = logging.getLogger('InaSAFE')

from qgis.core import QgsVectorLayer
from processing.core.Processing import Processing
from processing import runalg

from safe.inasafe_processing.provider import InaSafeProvider
from safe.common.utilities import unique_filename


class SplitPolyToLinesTest(unittest.TestCase):

    def setUp(self):

        self.provider = InaSafeProvider()
        Processing.addProvider(self.provider, True)

        self.polygon_file = test_data_path(
            'other', 'split_poly_with_points_before-poly.shp')
        self.point_file = test_data_path(
            'other', 'split_poly_with_points_before-points.shp')
        self.result_file = test_data_path(
            'other', 'split_poly_with_points_after.shp')

    def tearDown(self):
        Processing.removeProvider(self.provider)

    def test_run_algorithm(self):
        """Test splitting a polygon layer with a point layer."""
        output = unique_filename(suffix='-test.shp')
        result = runalg(
            'inasafe:splitpolygonstolines',
            self.polygon_file,
            self.point_file,
            output)

        result_layer = QgsVectorLayer(result['OUTPUT'], 'result', 'ogr')
        expected_layer = QgsVectorLayer(self.result_file, 'expected', 'ogr')

        # Check the number of features.
        msg = 'The number of features is not the same.'
        self.assertEqual(
            result_layer.featureCount(), expected_layer.featureCount(), msg)

        # Check the WKT for each features
        result_features = result_layer.getFeatures()
        expected_features = expected_layer.getFeatures()
        for expected, result in zip(result_features, expected_features):
            expected_wkt = expected.geometry().exportToWkt()
            result_wkt = result.geometry().exportToWkt()
            msg = 'Different geometries'
            self.assertEqual(expected_wkt, result_wkt, msg)

        # Check if the attribute table is the same.
        msg = 'The attribute table is not the same.'
        self.assertEqual(
            result_layer.dataProvider().fieldNameMap(),
            expected_layer.dataProvider().fieldNameMap(),
            msg)

        # Delete shapefile.
        directory = dirname(output)
        base_name = splitext(basename(output))[0]
        for f in listdir(directory):
            if f.startswith(base_name):
                remove(join(directory, f))

if __name__ == '__main__':
    suite = unittest.makeSuite(SplitPolyToLinesTest, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
