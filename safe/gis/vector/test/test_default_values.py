# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_local_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gis.vector.default_values import add_default_values
from safe.definitions.fields import (
    female_ratio_field,
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPrepareLayer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_value(self):
        """Test we can affect default value according to keywords."""
        layer = load_local_vector_layer(
            'issue-3325-default-value.geojson',
            clone_to_memory=True
        )

        # This layer do not have keywords, we need to monkey patch them.
        layer.keywords = {
            'layer_purpose': 'exposure',
            'inasafe_fields': {
            },
            'inasafe_default_values': {
                female_ratio_field['key']: 0.5
            }
        }
        add_default_values(layer)
        # These keywords should add a new column female_ratio with 0.5 inside.
        index = layer.fieldNameIndex(female_ratio_field['field_name'])
        self.assertNotEqual(-1, index)
        self.assertListEqual(
            layer.uniqueValues(index),
            [0.5]
        )

        layer = load_local_vector_layer(
            'issue-3325-default-value.geojson',
            clone_to_memory=True
        )
        # This layer do not have keywords, we need to monkey patch them.
        layer.keywords = {
            'layer_purpose': 'exposure',
            'inasafe_fields': {
                female_ratio_field['key']: 'value_1'
            },
            'inasafe_default_values': {
                female_ratio_field['key']: 0.5
            }
        }
        add_default_values(layer)
        # These keywords should not add a new column female_ratio.
        index = layer.fieldNameIndex(female_ratio_field['field_name'])
        self.assertEqual(-1, index)

        index = layer.fieldNameIndex('value_1')
        self.assertListEqual(
            sorted(layer.uniqueValues(index)),
            [0.5, 1]
        )
