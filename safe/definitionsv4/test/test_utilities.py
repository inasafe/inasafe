# coding=utf-8
"""Test for utilities module.."""
import unittest

from safe.definitionsv4 import (
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
    density_exposure_unit,
    count_exposure_unit,
    unit_metres,
    unit_feet,
    unit_generic,
    exposure_fields,
    exposure_class_field,
    hazard_class_field,
    hazard_fields,
    hazard_value_field,
    flood_hazard_classes,
    generic_hazard_classes
)

from safe.definitionsv4.utilities import (
    definition,
    purposes_for_layer,
    hazards_for_layer,
    exposures_for_layer,
    hazard_categories_for_layer,
    hazard_units,
    exposure_units,
    get_fields,
    get_hazard_classifications
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
        hazards = hazards_for_layer(
            'polygon', 'single_event')
        # print [x['key'] for x in hazards]
        expected = [
            hazard_flood,
            hazard_tsunami,
            hazard_earthquake,
            hazard_volcano,
            hazard_volcanic_ash,
            hazard_generic
        ]
        self.assertItemsEqual(hazards, expected)

        hazards = hazards_for_layer('polygon')
        expected = [
            hazard_flood,
            hazard_tsunami,
            hazard_earthquake,
            hazard_volcano,
            hazard_volcanic_ash,
            hazard_generic
        ]
        self.assertItemsEqual(hazards, expected)

        hazards = hazards_for_layer(
            'point', 'single_event')
        expected = [hazard_volcano]
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
        expected = [count_exposure_unit, density_exposure_unit]
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
            get_hazard_classifications('flood'), expected)

    def test_get_fields(self):
        """Test get_fields method."""
        fields = get_fields('exposure', 'structure')
        expected_fields = exposure_fields + exposure_structure['extra_fields']
        expected_fields.remove(exposure_class_field)
        self.assertListEqual(fields, expected_fields)

        fields = get_fields('hazard', 'flood')
        expected_fields = hazard_fields + hazard_flood['extra_fields']
        expected_fields.remove(hazard_class_field)
        expected_fields.remove(hazard_value_field)
        self.assertListEqual(fields, expected_fields)


if __name__ == '__main__':
    unittest.main()
