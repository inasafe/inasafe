# coding=utf-8
"""Test Field Mapping Tab."""


import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app, load_test_vector_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gui.widgets.field_mapping_tab import FieldMappingTab
from safe.definitions.field_groups import age_ratio_group, gender_ratio_group
from safe.definitions.constants import qvariant_numbers
from safe.definitions.fields import female_ratio_field

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestFieldMappingTab(unittest.TestCase):

    """Test cases for FieldMappingTab class."""

    def test_init(self):
        """Test FieldMappingTab initialization."""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid_complex.geojson',
            with_keywords=False, clone_to_memory=True)
        layer.keywords = {}

        field_mapping = FieldMappingTab(age_ratio_group, PARENT, IFACE)
        field_mapping.set_layer(layer)

        # Empty keywords should give empty for all aspect
        parameter_values = field_mapping.get_parameter_value()
        self.assertEqual(parameter_values['fields'], {})
        for v in list(parameter_values['values'].values()):
            self.assertIsNone(v)

        # Make sure all keys exist
        fields_keys = list(parameter_values['fields'].keys())
        values_keys = list(parameter_values['values'].keys())
        age_ratio_fields_keys = [field['key'] for field in age_ratio_group[
            'fields']]
        for key in fields_keys + values_keys:
            self.assertIn(key, age_ratio_fields_keys)

        # Check field list
        fields = []
        for index in range(field_mapping.field_list.count()):
            fields.append(field_mapping.field_list.item(index))
        labels = [i.text() for i in fields]

        for field in layer.dataProvider().fields():
            if field.type() not in qvariant_numbers:
                continue
            self.assertIn(field.name(), labels)

    def test_init_gender_ratio(self):
        """Test FieldMappingTab initialization for gender ratio."""
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid_complex.geojson',
            with_keywords=False, clone_to_memory=True)
        layer.keywords = {
            'inasafe_default_values': {
                female_ratio_field['key']: 0.7
            }
        }

        field_mapping = FieldMappingTab(gender_ratio_group, PARENT, IFACE)
        field_mapping.set_layer(layer)

        parameter_values = field_mapping.get_parameter_value()
        self.assertEqual(parameter_values['fields'], {})
        for k, v in list(parameter_values['values'].items()):
            if k == female_ratio_field['key']:
                self.assertEqual(0.7, v)
            else:
                message = 'Key {key} gives not None, but {value}'.format(
                    key=k, value=v)
                self.assertIsNone(v, message)

        # Make sure all keys exist
        fields_keys = list(parameter_values['fields'].keys())
        values_keys = list(parameter_values['values'].keys())
        gender_ratio_fields_keys = [
            field['key'] for field in gender_ratio_group[
            'fields']]
        for key in fields_keys + values_keys:
            self.assertIn(key, gender_ratio_fields_keys)

        # Check field list
        fields = []
        for index in range(field_mapping.field_list.count()):
            fields.append(field_mapping.field_list.item(index))
        labels = [i.text() for i in fields]

        for field in layer.dataProvider().fields():
            if field.type() not in qvariant_numbers:
                continue
            self.assertIn(field.name(), labels)

if __name__ == '__main__':
    unittest.main()
