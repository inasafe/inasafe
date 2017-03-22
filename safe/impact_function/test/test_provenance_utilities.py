# coding=utf-8
"""Test for Provenance Utilities."""

import unittest
from safe.definitions import (
    hazard_earthquake,
    exposure_population,
    hazard_category_single_event
)
from safe.impact_function.provenance_utilities import (
    get_map_title,
    get_analysis_question,
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

    def test_get_analysis_question(self):
        """Test for get_analysis_question."""
        question = get_analysis_question(
            hazard_earthquake, exposure_population)
        expected = (
            'In the event of a {hazard_name}, {exposure_measure} '
            '{exposure_name} might be affected?').format(
                hazard_name=hazard_earthquake['name'],
                exposure_measure=exposure_population['measure_question'],
                exposure_name=exposure_population['name'])
        self.assertEqual(question, expected)

if __name__ == '__main__':
    unittest.main()
