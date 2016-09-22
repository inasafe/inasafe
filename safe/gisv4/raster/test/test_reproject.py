# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_raster_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsCoordinateReferenceSystem

from safe.gisv4.raster.reproject import reproject


class TestReprojectRaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reproject_raster(self):
        """Test we can reproject a raster layer."""
        layer = load_test_raster_layer('hazard', 'classified_flood_20_20.asc')

        output_crs = QgsCoordinateReferenceSystem(3857)

        reprojected = reproject(layer=layer, output_crs=output_crs)

        self.assertEqual(reprojected.crs(), output_crs)
        self.assertEqual(reprojected.name(), 'reprojected')
        self.assertDictEqual(layer.keywords, reprojected.keywords)
