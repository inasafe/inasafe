# coding=utf-8
"""Test for utilities module."""
import unittest
from copy import deepcopy
from tempfile import mkdtemp
from os.path import join, exists, split
import shutil

from safe import definitions

from safe.definitions import (
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_generic,
    hazard_cyclone,
    exposure_population,
    exposure_land_cover,
    exposure_road,
    exposure_structure,
    hazard_category_single_event,
    hazard_category_multiple_event,
    count_exposure_unit,
    unit_metres,
    unit_feet,
    unit_generic,
    exposure_fields,
    hazard_fields,
    flood_hazard_classes,
    flood_petabencana_hazard_classes,
    generic_hazard_classes,
    aggregation_fields,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_geometry_raster,
    layer_geometry_line,
    layer_geometry_point,
    layer_geometry_polygon,
    cyclone_au_bom_hazard_classes,
    unit_knots,
    population_field_groups,
    aggregation_field_groups,
    productivity_rate_field,
    production_cost_rate_field,
    production_value_rate_field,
    provenance_host_name,
    provenance_user
)
from safe.definitions.reports.components import map_report

from safe.definitions.utilities import (
    definition,
    purposes_for_layer,
    hazards_for_layer,
    exposures_for_layer,
    hazard_categories_for_layer,
    hazard_units,
    exposure_units,
    get_fields,
    get_classifications,
    get_allowed_geometries,
    all_default_fields,
    get_compulsory_fields,
    get_non_compulsory_fields,
    default_classification_thresholds,
    default_classification_value_maps,
    fields_in_field_groups,
    get_field_groups,
    update_template_component,
    get_name,
    set_provenance
)

from safe.utilities.resources import resources_path


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefinitionsUtilities(unittest.TestCase):

    """Test Utilities Class for Definitions."""

    maxDiff = None

    def test_definition(self):
        """Test we can get definitions for keywords.

        .. versionadded:: 3.2

        """
        keyword = 'hazards'
        keyword_definition = definition(keyword)
        self.assertTrue('description' in keyword_definition)

    def test_get_name(self):
        """Test get_name method."""
        flood_name = get_name(hazard_flood['key'])
        self.assertEqual(flood_name, hazard_flood['name'])

        not_exist_key = 'Mega flux capacitor'
        not_found_name = get_name(not_exist_key)
        self.assertEqual(not_exist_key, not_found_name)

    def test_layer_purpose_for_layer(self):
        """Test for purpose_for_layer method."""
        expected = ['aggregation', 'exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('polygon'))

        expected = ['exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('raster'))

        expected = ['exposure']
        self.assertListEqual(expected, purposes_for_layer('line'))

    def test_hazards_for_layer(self):
        """Test for hazards_for_layer"""
        self.maxDiff = None
        hazards = hazards_for_layer(
            'polygon', 'single_event')
        hazards = [hazard['key'] for hazard in hazards]
        expected = [
            hazard_flood['key'],
            hazard_tsunami['key'],
            hazard_earthquake['key'],
            hazard_volcano['key'],
            hazard_volcanic_ash['key'],
            hazard_cyclone['key'],
            hazard_generic['key']
        ]
        self.assertItemsEqual(hazards, expected)

        hazards = hazards_for_layer('polygon')
        hazards = [hazard['key'] for hazard in hazards]
        expected = [
            hazard_flood['key'],
            hazard_tsunami['key'],
            hazard_earthquake['key'],
            hazard_volcano['key'],
            hazard_volcanic_ash['key'],
            hazard_cyclone['key'],
            hazard_generic['key']
        ]
        self.assertItemsEqual(hazards, expected)

        hazards = hazards_for_layer(
            'raster', 'single_event')
        hazards = [hazard['key'] for hazard in hazards]
        expected = [
            hazard_flood['key'],
            hazard_tsunami['key'],
            hazard_earthquake['key'],
            hazard_volcanic_ash['key'],
            hazard_cyclone['key'],
            hazard_generic['key']
        ]
        self.assertItemsEqual(hazards, expected)

    def test_exposures_for_layer(self):
        """Test for exposures_for_layer"""
        exposures = exposures_for_layer('polygon')
        expected = [
            exposure_structure,
            exposure_population,
            exposure_land_cover,
        ]
        self.assertItemsEqual(exposures, expected)

        exposures = exposures_for_layer('line')
        expected = [exposure_road]
        self.assertItemsEqual(exposures, expected)

    def test_hazard_categories_for_layer(self):
        """Test for hazard_categories_for_layer"""
        hazard_categories = hazard_categories_for_layer()
        expected = [
            hazard_category_multiple_event,
            hazard_category_single_event]
        self.assertListEqual(hazard_categories, expected)

    def test_exposure_units(self):
        """Test for exposure_units"""
        expected = [count_exposure_unit]
        self.assertItemsEqual(exposure_units('population'), expected)

    def test_hazards_units(self):
        """Test for hazard_units"""
        expected = [unit_metres, unit_feet, unit_generic]
        self.assertItemsEqual(hazard_units('flood'), expected)

    def test_hazards_classifications(self):
        """Test for get_hazards_classifications."""
        self.maxDiff = None
        expected = [
            flood_hazard_classes,
            flood_petabencana_hazard_classes,
            generic_hazard_classes]
        self.assertItemsEqual(
            get_classifications('flood'), expected)

    def test_get_compulsory_field(self):
        """Test get_compulsory_field method."""
        compulsory_field = get_compulsory_fields('exposure', 'structure')
        expected_fields = exposure_structure['compulsory_fields']
        self.assertListEqual([compulsory_field], expected_fields)

    def test_get_not_compulsory_field(self):
        """Test get_non_compulsory_field method."""
        non_compulsory_fields = get_non_compulsory_fields(
            'exposure', 'structure')
        expected_fields = [
            field for field in exposure_structure['fields'] if not field[
                'replace_null']]
        expected_fields += [
            field for field in exposure_structure['extra_fields'] if not
            field['replace_null']]
        expected_fields += [
            field for field in fields_in_field_groups(
                layer_purpose_exposure['field_groups']) if not
            field['replace_null']]

        for field in expected_fields:
            if field.get('replace_null'):
                expected_fields.remove(field)
        self.assertListEqual(non_compulsory_fields, expected_fields)

    def test_get_fields(self):
        """Test get_fields method."""
        fields = get_fields('exposure', 'structure')
        expected_fields = deepcopy(exposure_structure['compulsory_fields'])
        expected_fields += exposure_structure['fields']
        expected_fields += exposure_structure['extra_fields']
        expected_fields += fields_in_field_groups(
            layer_purpose_exposure['field_groups'])
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('hazard', 'flood')
        expected_fields = deepcopy(hazard_flood['compulsory_fields'])
        expected_fields += hazard_flood['fields']
        expected_fields += hazard_flood['extra_fields']
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('hazard')
        expected_fields = deepcopy(hazard_fields)
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('exposure')
        expected_fields = deepcopy(exposure_fields)
        expected_fields += fields_in_field_groups(
            layer_purpose_exposure['field_groups'])
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation')
        expected_fields = deepcopy(aggregation_fields)
        expected_fields += fields_in_field_groups(
            layer_purpose_aggregation['field_groups'])
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation', replace_null=True)
        expected_fields = deepcopy(aggregation_fields)
        expected_fields += fields_in_field_groups(
            layer_purpose_aggregation['field_groups'])
        expected_fields = [f for f in expected_fields if f['replace_null']]
        self.assertListEqual(fields, expected_fields)

        fields = get_fields(
            layer_purpose_exposure['key'],
            exposure_land_cover['key'],
            replace_null=False)
        expected_fields = deepcopy(exposure_land_cover['compulsory_fields'])
        expected_fields += deepcopy(exposure_fields)
        expected_fields += [
            productivity_rate_field,
            production_cost_rate_field,
            production_value_rate_field
        ]
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation', replace_null=False)
        expected_fields = deepcopy(aggregation_fields)
        expected_fields += fields_in_field_groups(
            layer_purpose_aggregation['field_groups'])
        expected_fields = [f for f in expected_fields if not f['replace_null']]
        self.assertListEqual(fields, expected_fields)

    def test_get_allowed_geometries(self):
        """Test get_allowed_geometries"""
        allowed_geometries = get_allowed_geometries(
            layer_purpose_hazard['key'])
        expected = [
            layer_geometry_polygon,
            layer_geometry_raster
        ]
        self.assertEqual(allowed_geometries, expected)

        allowed_geometries = get_allowed_geometries(
            layer_purpose_exposure['key'])
        expected = [
            layer_geometry_point,
            layer_geometry_line,
            layer_geometry_polygon,
            layer_geometry_raster
        ]
        self.assertEqual(allowed_geometries, expected)

    def test_all_default_fields(self):
        """Test all_default_fields method."""
        default_fields = all_default_fields()
        for default_field in default_fields:
            self.assertTrue(default_field.get('replace_null'), False)
            self.assertIsNotNone(default_field.get('default_value'))

    def test_classification_thresholds(self):
        """Test for classification_thresholds method."""
        thresholds = default_classification_thresholds(flood_hazard_classes)
        wet_class = flood_hazard_classes['classes'][0]
        dry_class = flood_hazard_classes['classes'][1]

        expected = {
            'dry': [
                dry_class['numeric_default_min'],
                dry_class['numeric_default_max']
            ],
            'wet': [
                wet_class['numeric_default_min'],
                wet_class['numeric_default_max']
            ]
        }
        self.assertDictEqual(thresholds, expected)

        unit_knots_key = unit_knots['key']
        thresholds = default_classification_thresholds(
            cyclone_au_bom_hazard_classes, unit_knots_key)
        category_5_class = cyclone_au_bom_hazard_classes['classes'][0]
        category_4_class = cyclone_au_bom_hazard_classes['classes'][1]
        category_3_class = cyclone_au_bom_hazard_classes['classes'][2]
        category_2_class = cyclone_au_bom_hazard_classes['classes'][3]
        category_1_class = cyclone_au_bom_hazard_classes['classes'][4]
        tropical_depression_class = cyclone_au_bom_hazard_classes['classes'][5]
        expected = {
            'tropical_depression': [
                tropical_depression_class['numeric_default_min'],
                tropical_depression_class['numeric_default_max'][
                    unit_knots_key]
            ],
            'category_1': [
                category_1_class['numeric_default_min'][unit_knots_key],
                category_1_class['numeric_default_max'][unit_knots_key]
            ],
            'category_2': [
                category_2_class['numeric_default_min'][unit_knots_key],
                category_2_class['numeric_default_max'][unit_knots_key]
            ],
            'category_3': [
                category_3_class['numeric_default_min'][unit_knots_key],
                category_3_class['numeric_default_max'][unit_knots_key]
            ],
            'category_4': [
                category_4_class['numeric_default_min'][unit_knots_key],
                category_4_class['numeric_default_max'][unit_knots_key]
            ],
            'category_5': [
                category_5_class['numeric_default_min'][unit_knots_key],
                category_5_class['numeric_default_max']
            ]
        }
        self.assertDictEqual(thresholds, expected)

    def test_classification_value_maps(self):
        """Test for classification_value_maps method."""
        value_maps = default_classification_value_maps(flood_hazard_classes)
        wet_class = flood_hazard_classes['classes'][0]
        dry_class = flood_hazard_classes['classes'][1]
        expected = {
            'dry': dry_class['string_defaults'],
            'wet': wet_class['string_defaults']
        }
        self.assertDictEqual(value_maps, expected)

        value_maps = default_classification_value_maps(
            cyclone_au_bom_hazard_classes)
        category_5_class = cyclone_au_bom_hazard_classes['classes'][0]
        category_4_class = cyclone_au_bom_hazard_classes['classes'][1]
        category_3_class = cyclone_au_bom_hazard_classes['classes'][2]
        category_2_class = cyclone_au_bom_hazard_classes['classes'][3]
        category_1_class = cyclone_au_bom_hazard_classes['classes'][4]
        tropical_depression_class = cyclone_au_bom_hazard_classes['classes'][5]
        expected = {
            'category_1': category_1_class.get('string_defaults', []),
            'category_2': category_2_class.get('string_defaults', []),
            'category_3': category_3_class.get('string_defaults', []),
            'category_4': category_4_class.get('string_defaults', []),
            'category_5': category_5_class.get('string_defaults', []),
            'tropical_depression': tropical_depression_class.get(
                'string_defaults', [])
        }
        self.assertDictEqual(value_maps, expected)

    def test_unique_definition_key(self):
        """Test to make sure all definitions have different key."""
        keys = {}
        for item in dir(definitions):
            if not item.startswith("__"):
                var = getattr(definitions, item)
                if isinstance(var, dict):
                    if not var.get('key'):
                        continue
                    if var.get('key') not in keys:
                        keys[var.get('key')] = [var]
                    else:
                        keys[var.get('key')].append(var)
        duplicate_keys = [k for k, v in keys.items() if len(v) > 1]
        message = 'There are duplicate keys: %s\n' % ', '.join(duplicate_keys)
        for duplicate_key in duplicate_keys:
            message += 'Duplicate key: %s\n' % duplicate_key
            for v in keys[duplicate_key]:
                message += v['name'] + ' ' + v['description'] + '\n'
        self.assertEqual(len(duplicate_keys), 0, message)

    def test_fields_in_field_groups(self):
        """Test for fields_in_field_groups method."""
        fields = fields_in_field_groups(population_field_groups)
        expected = []
        for field_group in population_field_groups:
            expected += field_group['fields']
        self.assertListEqual(fields, expected)

    def test_get_field_groups(self):
        """Test for get_field_groups method."""
        field_groups = get_field_groups(layer_purpose_aggregation['key'])
        expected = aggregation_field_groups
        self.assertListEqual(field_groups, expected)

        field_groups = get_field_groups(layer_purpose_exposure['key'])
        expected = []
        self.assertListEqual(field_groups, expected)

        field_groups = get_field_groups(
            layer_purpose_exposure['key'], exposure_population['key'])
        expected = population_field_groups
        self.assertListEqual(field_groups, expected)

        field_groups = get_field_groups(layer_purpose_hazard['key'])
        expected = []
        self.assertListEqual(field_groups, expected)

    def test_update_template_component(self):
        """Test for custom template component."""
        # Default qpt
        component = update_template_component(map_report, '.')
        self.assertDictEqual(component, map_report)

        # Custom qpt
        target_directory = mkdtemp()
        default_qpt = resources_path(
            'qgis-composer-templates',
            'inasafe-map-report-portrait.qpt')
        if exists(default_qpt):
            target_path = join(target_directory, split(default_qpt)[1])
            shutil.copy2(default_qpt, target_path)

        component = update_template_component(map_report, target_directory)
        self.assertTrue(component != map_report)

    def test_set_provenance(self):
        """Test for set_provenance."""
        provenance_collection = {}
        host_name_value = 'host_name'
        set_provenance(
            provenance_collection, provenance_host_name, host_name_value)
        expected = {provenance_host_name['provenance_key']: host_name_value}
        self.assertDictEqual(provenance_collection, expected)

        host_name_value = 'new_host_name'
        set_provenance(
            provenance_collection, provenance_host_name, host_name_value)
        expected = {provenance_host_name['provenance_key']: host_name_value}
        self.assertDictEqual(provenance_collection, expected)

        user_value = 'user'
        set_provenance(
            provenance_collection, provenance_user, user_value)
        expected = {
            provenance_host_name['provenance_key']: host_name_value,
            provenance_user['provenance_key']: user_value,
        }
        self.assertDictEqual(provenance_collection, expected)


if __name__ == '__main__':
    unittest.main()
