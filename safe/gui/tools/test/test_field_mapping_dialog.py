# coding=utf-8

"""Tests for field mapping dialog."""

import unittest
import logging

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app, load_test_vector_layer
from safe.common.exceptions import KeywordNotFoundError

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.definitions.fields import female_ratio_field
from safe.gui.tools.field_mapping_dialog import FieldMappingDialog


LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestFieldMappingDialog(unittest.TestCase):

    """Test Field Mapping Dialog."""

    def test_init(self):
        """Test init the tool."""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid_complex.geojson',
            with_keywords=False, clone_to_memory=True)

        field_mapping_dialog = FieldMappingDialog(parent=PARENT, iface=IFACE)

        # Raise exception when there is no keywords
        with self.assertRaises(KeywordNotFoundError):
            field_mapping_dialog.set_layer(layer, {})

        # Set layer with keywords
        keywords = {'layer_purpose': layer_purpose_aggregation['key']}
        field_mapping_dialog.set_layer(layer, keywords)

        # Click OK
        field_mapping_dialog.accept()
        # Check the saved metadata
        self.assertDictEqual(
            keywords,
            {
                'layer_purpose': layer_purpose_aggregation['key'],
                'inasafe_default_values': {},
                'inasafe_fields': {}
            }
        )

        # Set layer with keywords
        keywords = {
            'layer_purpose': layer_purpose_aggregation['key'],
            'inasafe_default_values': {female_ratio_field['key']: 0.7},
        }
        field_mapping_dialog.set_layer(layer, keywords)

        # Click OK
        field_mapping_dialog.accept()
        # Check the saved metadata
        self.assertDictEqual(
            keywords,
            {
                'layer_purpose': layer_purpose_aggregation['key'],
                'inasafe_default_values': {female_ratio_field['key']: 0.7},
                'inasafe_fields': {}
            }
        )


if __name__ == '__main__':
    suite = unittest.makeSuite(TestFieldMappingDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
