# coding=utf-8
"""Test for Provenance Utilities."""

import unittest
from safe.definitions import (
    hazard_earthquake,
    exposure_population,
    hazard_category_single_event,
    exposure_structure
)
from safe.impact_function.provenance_utilities import (
    get_map_title, get_map_legend_title
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestProvenanceUtilities(unittest.TestCase):
    """Test Provenance Utilities."""

    def test_get_map(self):
        """Test get map."""
        expected = 'Population affected by Earthquake event'
        result = get_map_title(
            hazard_earthquake,
            exposure_population,
            hazard_category_single_event)
        self.assertEqual(expected, result)

    def test_get_map_legend(self):
        """Test get map legend."""
        expected = 'Number of Structures'
        result = get_map_legend_title(exposure_structure)
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
