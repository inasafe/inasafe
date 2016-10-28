# coding=utf-8

import unittest
from osgeo import gdal

from safe.test.utilities import (
    get_qgis_app,
    load_local_vector_layer,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


from safe.gisv4.vector.tools import create_memory_layer
from safe.gisv4.vector.prepare_vector_layer import (
    prepare_vector_layer,
    copy_layer,
    copy_fields,
    remove_fields,
    _remove_rows,
    _add_id_column,
    _add_default_values,
)
from safe.definitionsv4.fields import (
    exposure_id_field,
    population_count_field,
    female_ratio_field,
    exposure_type_field
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

        remove_fields(new_layer, ['STRUCTURE', 'OSM_TYPE'])
        self.assertEqual(
            len(new_layer.fields().toList()), expected - 2)

        _add_id_column(new_layer)
        field_name = exposure_id_field['field_name']
        self.assertGreater(new_layer.fieldNameIndex(field_name), -1)

    @unittest.skipIf(
        int(gdal.VersionInfo('VERSION_NUM')) < 2010000,
        'GDAL 2.1 is required to edit GeoJSON.')
    def test_remove_rows(self):
        """Test we can remove rows."""

        layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson', clone=True)
        feature_count = layer.featureCount()
        _remove_rows(layer)
        self.assertEqual(layer.featureCount(), feature_count - 1)

    def test_default_value(self):
        """Test we can affect default value according to keywords."""
        layer = load_local_vector_layer(
            'issue-3325-default-value.geojson',
            clone_to_memory=True
        )

        # This layer do not have keywords, we need to monkey patch them.
        layer.keywords = {
            'inasafe_fields': {
            },
            'inasafe_default_value': {
                female_ratio_field['key']: 0.5
            }
        }
        _add_default_values(layer)
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
            'inasafe_fields': {
                female_ratio_field['key']: 'value_1'
            },
            'inasafe_default_value': {
                female_ratio_field['key']: 0.5
            }
        }
        _add_default_values(layer)
        # These keywords should not add a new column female_ratio.
        index = layer.fieldNameIndex(female_ratio_field['field_name'])
        self.assertEqual(-1, index)

        index = layer.fieldNameIndex('value_1')
        self.assertListEqual(
            sorted(layer.uniqueValues(index)),
            [0.5, 1]
        )

    def test_prepare_layer(self):
        """Test we can prepare a vector layer."""

        layer = load_test_vector_layer('exposure', 'building-points.shp')
        cleaned = prepare_vector_layer(layer)

        # Only 3 fields
        self.assertEqual(len(cleaned.fields().toList()), 3)

        # ET : I should check later the order.
        self.assertIn(
            cleaned.fieldNameIndex(exposure_id_field['field_name']),
            [0, 1, 2])

        self.assertIn(
            cleaned.fieldNameIndex(exposure_type_field['field_name']),
            [0, 1, 2])

        self.assertIn(
            cleaned.fieldNameIndex(population_count_field['field_name']),
            [0, 1, 2])
