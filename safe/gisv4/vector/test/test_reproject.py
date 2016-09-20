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
    standard_data_path)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
)

from safe.gisv4.vector.reproject import reproject


class TestReprojectVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reproject_vector(self):
        """Test we can reproject a vector layer."""

        layer = standard_data_path('exposure', 'buildings.shp')
        vector_layer = QgsVectorLayer(layer, 'Buildings', 'ogr')

        output_crs = QgsCoordinateReferenceSystem(3857)

        reprojected = reproject(layer=vector_layer, output_crs=output_crs)

        self.assertEqual(reprojected.crs(), output_crs)
        self.assertEqual(
            reprojected.featureCount(), vector_layer.featureCount())
        self.assertEqual(reprojected.name(), 'reprojected')
