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
    hazard_generic
)

from safe.definitionsv4.utilities import (
    definition,
    purposes_for_layer,
    hazards_for_layer
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


if __name__ == '__main__':
    unittest.main()
