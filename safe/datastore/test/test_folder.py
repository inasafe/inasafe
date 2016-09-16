# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Clipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest

from tempfile import mkdtemp
from os.path import join
from qgis.core import QgsVectorLayer, QgsRasterLayer
from PyQt4.QtCore import QDir

from safe.test.utilities import (
    get_qgis_app,
    standard_data_path)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.datastore.folder import Folder


class TestFolder(unittest.TestCase):
    """Test the folder datastore."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_folder_datastore(self):
        """Test if we can store shapefiles."""
        path = QDir(mkdtemp())
        data_store = Folder(path)
        self.assertTrue(data_store.is_writable())

        path = mkdtemp()
        layer_name = 'flood_test'
        data_store = Folder(path)

        # We do not have any layer yet.
        self.assertEqual(len(data_store.layers()), 0)

        # Let's add a vector layer.
        layer = standard_data_path('hazard', 'flood_multipart_polygons.shp')
        vector_layer = QgsVectorLayer(layer, 'Flood', 'ogr')
        result = data_store.add_layer(vector_layer, layer_name)
        self.assertTrue(result[0])
        self.assertEqual(result[1], '%s.shp' % layer_name)

        # We try to add the layer twice with the same name.
        result = data_store.add_layer(vector_layer, layer_name)
        self.assertFalse(result[0])

        # We have imported one layer.
        self.assertEqual(len(data_store.layers()), 1)

        # Check if we have the correct URI.
        self.assertIsNone(data_store.layer_uri(layer_name))
        expected = join(path, layer_name + '.shp')
        self.assertEqual(data_store.layer_uri(layer_name + '.shp'), expected)

        # This layer do not exist
        self.assertIsNone(data_store.layer_uri('fake_layer'))

        # Let's add a raster layer.
        layer = standard_data_path('hazard', 'classified_hazard.tif')
        raster_layer = QgsRasterLayer(layer, 'Flood')
        self.assertTrue(data_store.add_layer(raster_layer, layer_name))
        self.assertEqual(len(data_store.layers()), 2)

        # Check the URI for the raster layer.
        expected = join(path, layer_name + '.tif')
        self.assertEqual(data_store.layer_uri(layer_name + '.tif'), expected)

if __name__ == '__main__':
    unittest.main()
