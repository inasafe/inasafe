# coding=utf-8

"""Test for utilities module..
"""
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
    exposure_people_in_building,
    exposure_place,
    hazard_category_single_event,
    hazard_category_multiple_event
)

from safe.definitionsv4.utilities import (
    definition,
    purposes_for_layer,
    hazards_for_layer,
    exposures_for_layer,
    hazard_categories_for_layer
)


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
        hazard_categories = hazard_categories_for_layer('polygon')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        # Note(IS): Currently we don't count the hazard category. We can
        # update it later when we have use the hazard category
        # hazard_categories = hazard_categories_for_layer('line')
        # expected = []
        # self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = hazard_categories_for_layer('point')
        expected = [
            hazard_category_multiple_event,
            hazard_category_single_event
        ]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = hazard_categories_for_layer('raster')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = hazard_categories_for_layer('raster', 'earthquake')
        expected = [
            hazard_category_single_event,
            hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)


if __name__ == '__main__':
    unittest.main()
