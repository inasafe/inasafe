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

from tempfile import mktemp
from qgis.core import QgsVectorLayer
from PyQt4.QtCore import QFileInfo
from osgeo import gdal

from safe.test.utilities import (
    get_qgis_app,
    standard_data_path)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.datastore.geopackage import GeoPackage


class TestGeoPackage(unittest.TestCase):
    """Test the GeoPackage datastore."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(
        gdal.VersionInfo('VERSION_NUM') < 1110000,
        'GDAL 1.11 is required for geopackage.')
    def test_create_geopackage(self):
        """Test if we can store geopackage."""
        path = QFileInfo(mktemp() + '.gpkg')
        self.assertFalse(path.exists())
        data_store = GeoPackage(path)
        path.refresh()
        self.assertTrue(path.exists())

        layer_name = 'flood_test'

        # Let's add a vector layer.
        layer = standard_data_path('hazard', 'flood_multipart_polygons.shp')
        vector_layer = QgsVectorLayer(layer, 'Flood', 'ogr')
        result = data_store.add_layer(vector_layer, layer_name)
        self.assertTrue(result[0])

        # We should have one layer.
        layers = data_store.layers()
        self.assertEqual(len(layers), 1)
        self.assertIn(layer_name, layers)

        # Test the URI of the new layer.
        expected = path.absoluteFilePath() + '|layername=' + layer_name
        self.assertEqual(data_store.layer_uri(layer_name), expected)

        # Test a fake layer.
        self.assertIsNone(data_store.layer_uri('fake_layer'))


if __name__ == '__main__':
    unittest.main()
