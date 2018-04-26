# coding=utf-8
"""Unit Test for Prepare Vector Layer."""


import unittest
from osgeo import gdal

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


from safe.gis.vector.tools import create_memory_layer
from safe.gis.vector.prepare_vector_layer import (
    prepare_vector_layer,
    copy_layer,
    copy_fields,
    remove_fields,
    _remove_features,
    _add_id_column,
    _size_is_needed,
    _check_value_mapping,
    sum_fields,
    clean_inasafe_fields
)
from safe.definitions.fields import (
    exposure_id_field,
    population_count_field,
    female_ratio_field,
    exposure_type_field,
    female_count_field
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestPrepareLayer(unittest.TestCase):

    """Test for Prepare Vector Layer."""


    def _sorted_dict_values(_dict):
        """Make sure _dict values are sorted when list"""
        _ret = dict()
        for _k in _dict:
            try:
                _ret[_k] = sorted(_dict[_k]) 
            except:
                _ret[_k] = _dict[_k]
        return _ret

    def test_copy_vector_layer(self):
        """Test we can copy a vector layer."""
        layer = load_test_vector_layer('exposure', 'buildings.shp')
        new_layer = create_memory_layer(
            'New layer', layer.geometryType(), layer.crs(), layer.fields())
        new_layer.keywords = layer.keywords
        copy_layer(layer, new_layer)
        self.assertEqual(layer.featureCount(), new_layer.featureCount())
        self.assertEqual(
            len(layer.fields().toList()), len(new_layer.fields().toList()))

        expected = len(new_layer.fields().toList()) + 1
        new_fields = {'STRUCTURE': 'my_new_field'}
        copy_fields(new_layer, new_fields)
        self.assertEqual(
            len(new_layer.fields().toList()), expected)
        self.assertGreater(new_layer.fields().lookupField('my_new_field'), -1)

        remove_fields(new_layer, ['STRUCTURE', 'OSM_TYPE'])
        self.assertEqual(
            len(new_layer.fields().toList()), expected - 2)
        self.assertEqual(new_layer.fields().lookupField('STRUCTURE'), -1)
        self.assertEqual(new_layer.fields().lookupField('OSM_TYPE'), -1)

        _add_id_column(new_layer)
        field_name = exposure_id_field['field_name']
        self.assertGreater(new_layer.fields().lookupField(field_name), -1)

    @unittest.skipIf(
        int(gdal.VersionInfo('VERSION_NUM')) < 2010000,
        'GDAL 2.1 is required to edit GeoJSON.')
    def test_remove_rows(self):
        """Test we can remove rows."""

        layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson', clone=True)
        feature_count = layer.featureCount()
        _remove_features(layer)
        self.assertEqual(layer.featureCount(), feature_count - 1)

    def test_prepare_layer(self):
        """Test we can prepare a vector layer."""
        layer = load_test_vector_layer('exposure', 'building-points.shp')
        cleaned = prepare_vector_layer(layer)

        # Only 3 fields
        self.assertEqual(len(cleaned.fields().toList()), 2)

        # ET : I should check later the order.
        self.assertIn(
            cleaned.fields().lookupField(exposure_id_field['field_name']),
            [0, 1, 2])

        self.assertIn(
            cleaned.fields().lookupField(exposure_type_field['field_name']),
            [0, 1, 2])

    def test_size_needed(self):
        """Test we can add the size when it is needed."""
        # A building layer should be always false.
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')
        layer.keywords['inasafe_fields'] = {
            population_count_field['key']: population_count_field['field_name']
        }
        self.assertFalse(_size_is_needed(layer))
        layer.keywords['inasafe_fields'] = {
            female_ratio_field['key']: female_ratio_field['field_name']
        }
        self.assertFalse(_size_is_needed(layer))

        # But a road layer should be true only if it has a absolute value.
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')

        layer.keywords['inasafe_fields'] = {
            population_count_field['key']: population_count_field['field_name']
        }
        self.assertTrue(_size_is_needed(layer))

        layer.keywords['inasafe_fields'] = {
            female_ratio_field['key']: female_ratio_field['field_name']
        }
        self.assertFalse(_size_is_needed(layer))

    def test_check_value_mapping(self):
        """Test we can add missing exposure type to the other group."""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson')

        # No change
        value_map = {
            'commercial': ['shop'],
            'education': ['school'],
            'health': ['hospital'],
            'government': ['ministry'],
            'other': ['unknown']
        }
        layer.keywords['value_map'] = dict(value_map)
        layer = _check_value_mapping(layer)
        self.assertDictEqual(value_map, _sorted_dict_values(layer.keywords['value_map']))

        # Missing shop and unknown, the other group should be created.
        layer.keywords['value_map'] = {
            'education': ['school'],
            'health': ['hospital'],
            'government': ['ministry']
        }
        expected_value_map = {
            'education': ['school'],
            'health': ['hospital'],
            'government': ['ministry'],
            'other': ['shop', 'unknown']
        }
        layer = _check_value_mapping(layer)
        self.assertDictEqual(expected_value_map, _sorted_dict_values(layer.keywords['value_map'])

        # Missing shop, it should be added to the other group.
        layer.keywords['value_map'] = {
            'education': ['school'],
            'health': ['hospital'],
            'government': ['ministry'],
            'other': ['unknown']
        }
        expected_value_map = {
            'education': ['school'],
            'health': ['hospital'],
            'government': ['ministry'],
            'other': ['unknown', 'shop']
        }
        layer = _check_value_mapping(layer)
        self.assertDictEqual(expected_value_map, _sorted_dict_values(layer.keywords['value_map']))

    def test_own_id_column(self):
        """Test if we can re-use the column ID from the user."""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'buildings.geojson', clone=True)
        # This layer is set to use custom ID column. We should have the values
        # after preparing the vector layer.
        field = layer.fields().lookupField(exposure_id_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_values_before = layer.uniqueValues(field)
        self.assertEqual(
            unique_values_before,
            {10, 11, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110})
        _add_id_column(layer)
        field = layer.fields().lookupField(exposure_id_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_values_after = layer.uniqueValues(field)
        self.assertEqual(unique_values_after, unique_values_before)

        # Let's remove the keyword now to use the auto-increment ID
        del layer.keywords['inasafe_fields'][exposure_id_field['key']]
        _add_id_column(layer)
        field = layer.fields().lookupField(exposure_id_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_values_automatic = layer.uniqueValues(field)
        self.assertNotEqual(unique_values_automatic, unique_values_before)
        self.assertEqual(
            unique_values_automatic, set(
                range(
                    layer.featureCount())))

    def test_sum_fields(self):
        """Test sum_fields method."""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population_multi_fields.geojson', clone=True)
        sum_fields(
            layer, exposure_id_field['key'], ['F_0_4', 'F_5_9', 'F_9_15'])
        exposure_id__idx = layer.fields().lookupField(
            exposure_id_field['field_name'])
        F_0_4__idx = layer.fields().lookupField('F_0_4')
        F_5_9__idx = layer.fields().lookupField('F_5_9')
        F_9_15__idx = layer.fields().lookupField('F_9_15')
        for feature in layer.getFeatures():
            sum_value = (
                feature[F_0_4__idx] + feature[F_5_9__idx] + feature[
                    F_9_15__idx])
            self.assertEqual(feature[exposure_id__idx], sum_value)

        new_field__idx = layer.fields().lookupField(female_count_field['field_name'])
        # Check if the new field doesn't exist
        self.assertEqual(new_field__idx, -1)
        sum_fields(layer, female_count_field['key'], ['F_0_4', 'F_5_9'])
        new_field__idx = layer.fields().lookupField(female_count_field['field_name'])
        for feature in layer.getFeatures():
            sum_value = (feature[F_0_4__idx] + feature[F_5_9__idx])
            self.assertEqual(feature[new_field__idx], sum_value)

    def test_clean_inasafe_fields(self):
        """Test clean_inasafe_fields."""
        layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population_multi_fields.geojson', clone=True)
        original_female_fields = [
            'F_0_4',
            'F_5_9',
            'F_9_15',
            'F_15_30',
            'F_30_60',
            'F_60_100'
        ]
        layer.keywords = {
            'layer_purpose': 'exposure',
            'exposure': 'population',
            'inasafe_fields': {
                'exposure_id_field': 'exposure_id',
                'population_count_field': 'population',
                'female_count_field': original_female_fields
            }
        }
        clean_inasafe_fields(layer)

        # Check if the female count name does exist
        female_count_field_idx = layer.fields().lookupField(
            female_count_field['field_name'])
        self.assertGreater(female_count_field_idx, -1)

        # Check the keyword is updated properly
        expected_inasafe_fields = {
            population_count_field['key']: population_count_field[
                'field_name'],
            female_count_field['key']: female_count_field['field_name'],
            exposure_id_field['key']: exposure_id_field['field_name']
        }
        self.assertDictEqual(
            expected_inasafe_fields, layer.keywords['inasafe_fields'])

        # Check if the original fields are gone
        for original_female_field in original_female_fields:
            self.assertEqual(layer.fields().lookupField(original_female_field), -1)


if __name__ == '__main__':
    unittest.main()
