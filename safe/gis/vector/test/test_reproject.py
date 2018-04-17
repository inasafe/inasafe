# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

from qgis.core import QgsCoordinateReferenceSystem

from safe.gis.vector.reproject import reproject

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestReprojectVector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reproject_vector(self):
        """Test we can reproject a vector layer."""

        layer = load_test_vector_layer('exposure', 'buildings.shp')

        output_crs = QgsCoordinateReferenceSystem(3857)

        reprojected = reproject(layer=layer, output_crs=output_crs)

        self.assertEqual(reprojected.crs(), output_crs)
        self.assertEqual(
            reprojected.featureCount(), layer.featureCount())
        self.assertDictEqual(layer.keywords, reprojected.keywords)
