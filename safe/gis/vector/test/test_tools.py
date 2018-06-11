# coding=utf-8
"""Unit Test for Vector Tools."""


import unittest

from qgis.core import QgsWkbTypes

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


from safe.gis.vector.tools import create_memory_layer

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestVectorTools(unittest.TestCase):

    """Test for Vector Tools."""

    def test_copy_vector_layer(self):
        """Test we can create a memory layer."""
        layer = load_test_vector_layer('exposure', 'buildings.shp')
        new_layer = create_memory_layer(
            'New layer', layer.geometryType(), layer.crs(), layer.fields())
        self.assertTrue(new_layer.isValid())
        self.assertEqual(new_layer.name(), 'New layer')
        self.assertEqual(new_layer.fields(), layer.fields())
        self.assertEqual(new_layer.crs(), layer.crs())
        self.assertEqual(new_layer.wkbType(), QgsWkbTypes.MultiPolygon)

        # create_memory_layer should also accept a list of fields, not a QgsFields object
        field_list = [f for f in layer.fields()]
        new_layer = create_memory_layer(
            'New layer', layer.geometryType(), layer.crs(), field_list)
        self.assertTrue(new_layer.isValid())
        self.assertEqual(new_layer.name(), 'New layer')
        self.assertEqual(new_layer.fields(), layer.fields())
        self.assertEqual(new_layer.crs(), layer.crs())
        self.assertEqual(new_layer.wkbType(), QgsWkbTypes.MultiPolygon)


if __name__ == '__main__':
    unittest.main()
