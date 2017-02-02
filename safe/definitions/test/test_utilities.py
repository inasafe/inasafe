# coding=utf-8
"""Test for utilities module."""
import unittest

from safe.definitions import (
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_generic,
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
    generic_hazard_classes,
    aggregation_fields,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_geometry_raster,
    layer_geometry_line,
    layer_geometry_point,
    layer_geometry_polygon,
    cyclone_au_bom_hazard_classes,
    unit_knots
)
from safe.definitions.hazard import hazard_cyclone

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
    classification_thresholds
)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefinitionsUtilities(unittest.TestCase):
    """Test Utilities Class for Definitions."""

    def test_definition(self):
        """Test we can get definitions for keywords.

        .. versionadded:: 3.2

        """
        keyword = 'hazards'
        keyword_definition = definition(keyword)
        self.assertTrue('description' in keyword_definition)

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
        expected = [flood_hazard_classes, generic_hazard_classes]
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
        expected_fields = [field for field in exposure_structure['fields'] if
                           not field['replace_null']]
        expected_fields += [field for field in
                            exposure_structure['extra_fields'] if
                           not field['replace_null']]

        for field in expected_fields:
            if field.get('replace_null'):
                expected_fields.replace(field)
        self.assertListEqual(non_compulsory_fields, expected_fields)

    def test_get_fields(self):
        """Test get_fields method."""
        fields = get_fields('exposure', 'structure')
        expected_fields = exposure_structure['compulsory_fields']
        expected_fields += exposure_structure['fields']
        expected_fields += exposure_structure['extra_fields']
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('hazard', 'flood')
        expected_fields = hazard_flood['compulsory_fields']
        expected_fields += hazard_flood['fields']
        expected_fields += hazard_flood['extra_fields']
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('hazard')
        expected_fields = hazard_fields
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('exposure')
        expected_fields = exposure_fields
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation')
        expected_fields = aggregation_fields
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation', replace_null=True)
        expected_fields = [f for f in aggregation_fields if f['replace_null']]
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('aggregation', replace_null=False)
        expected_fields = [
            f for f in aggregation_fields if not f['replace_null']]
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
        print[x['key'] for x in expected]
        print[x['key'] for x in allowed_geometries]
        self.assertEqual(allowed_geometries, expected)

    def test_all_default_fields(self):
        """Test all_default_fields method."""
        default_fields = all_default_fields()
        for default_field in default_fields:
            self.assertTrue(default_field.get('replace_null'), False)
            self.assertIsNotNone(default_field.get('default_value'))

    def test_classification_thresholds(self):
        """Test for classification_thresholds method."""
        thresholds = classification_thresholds(flood_hazard_classes)
        expected = {
            'dry': [0, 0.9999999999999999],
            'wet': [1, 9999999999]
        }
        self.assertDictEqual(thresholds, expected)

        thresholds = classification_thresholds(
            cyclone_au_bom_hazard_classes, unit_knots)
        expected = {
            'category_1': [34, 47.0],
            'category_2': [47, 63.0],
            'category_3': [63, 85.0],
            'category_4': [85, 107.0],
            'category_5': [107, 9999999999],
            'tropical_depression': [0, 34.0]
        }
        self.assertDictEqual(thresholds, expected)

if __name__ == '__main__':
    unittest.main()
