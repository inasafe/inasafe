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


class RemoveFeaturesTest(unittest.TestCase):

    def setUp(self):
        self.provider = InaSafeProvider()
        Processing.addProvider(self.provider, True)

    def tearDown(self):
        Processing.removeProvider(self.provider)

    def test_run_algorithm(self):
        """Test removing features."""
        layer_1 = test_data_path('other', 'join_layer_1.shp')
        layer_2 = test_data_path('other', 'join_layer_2.shp')

        output = unique_filename(suffix='-test.shp')

        result = runalg(
            'inasafe:removingunmatchedfeatures',
            layer_1,
            'id',
            layer_2,
            'id',
            output)
        result_layer = QgsVectorLayer(result['OUTPUT'], 'result', 'ogr')
        self.assertEqual(result_layer.featureCount(), 6)

        list_id = []
        for f in result_layer.getFeatures():
            list_id.append(f.attributes()[0])
        self.assertEqual(list_id, [2, 3, 5, 6, 8, 9])

        # Delete shapefile.
        directory = dirname(output)
        base_name = splitext(basename(output))[0]
        for f in listdir(directory):
            if f.startswith(base_name):
                remove(join(directory, f))

if __name__ == '__main__':
    suite = unittest.makeSuite(RemoveFeaturesTest, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
