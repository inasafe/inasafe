# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test for Building Exposure Report Mixin**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Christian Christelis <christian@kartoza.com>'

__date__ = '27/07/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import safe.impact_functions.core  # pylint: disable=unused-import
from safe.impact_reports.population_exposure_report_mixin import (
    PopulationExposureReportMixin)


# noinspection PyArgumentList
class PopulationExposureReportMixinTest(unittest.TestCase):
    """Test the ReportMixin.

    .. versionadded:: 3.2
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests."""
        self.population_mixin_blank = PopulationExposureReportMixin()
        self.population_mixin = PopulationExposureReportMixin()
        self.population_mixin.affected_population['High'] = 100
        self.population_mixin.affected_population['Medium'] = 100
        self.population_mixin.affected_population['Low'] = 100
        self.population_mixin.total_population = 400
        self.population_mixin.unaffected_population = (
            self.population_mixin.total_population -
            self.population_mixin.total_affected_population)
        self.population_mixin.minimum_needs = [
            {
                'frequency': 'test frequency',
                'unit': {'abbreviation': 'u'},
                'name': 'test name 1',
                'value': '1',
            },
            {
                'frequency': 'test frequency',
                'unit': {'abbreviation': 'u'},
                'name': 'test name 2',
                'value': '2',
            }
        ]

    def tearDown(self):
        """Run after each test."""
        del self.population_mixin_blank
        del self.population_mixin

    def test_0001_generate_report(self):
        """Generate a blank report."""
        blank_report = self.population_mixin_blank.generate_report()
        blank_report = blank_report.to_text()
        expected_strings = [
            u'**Population needing evacuation <sup>1</sup>**, 0',
            u'**Unaffected population**, 0',
            u'Evacuated population minimum needs',
            u'Action checklist',
            u'How will warnings be disseminated?',
            u'How will we reach evacuated people?',
            (u'Are there enough shelters and relief items available '
             u'for 0 people?'),
            (u'If yes, where are they located and how will we '
             u'distribute them?'),
            (u'If no, where can we obtain additional relief items '
             u'from and how will we transport them to here?')]
        for item in expected_strings:
            self.assertIn(item, blank_report)

    def test_0002_category_ordering(self):
        """Test correct category ordering."""
        category_ordering = self.population_mixin.impact_category_ordering
        expected_category_ordering = ['High', 'Medium', 'Low']
        message = 'Category ordering is not as expected.'
        self.assertListEqual(
            category_ordering,
            expected_category_ordering,
            message)

    def test_0003_minimum_needs_breakdown(self):
        """Test minimum needs breakdown."""
        needs_breakdown = self.population_mixin.minimum_needs_breakdown()
        needs_breakdown = needs_breakdown.to_text()

        expected_needs = [
            u'Evacuated population minimum needs',
            u'**Relief items to be provided test frequency**',
            u'test name 1 [u], 300',
            u'test name 2 [u], 600'
        ]

        for item in expected_needs:
            self.assertIn(item, needs_breakdown)

    def test_0004_population_counts(self):
        """Test correct category ordering."""
        other_population_counts = self.population_mixin.other_population_counts
        affected_population = self.population_mixin.affected_population
        unaffected_population = self.population_mixin.unaffected_population
        total_affected_population = (
            self.population_mixin.total_affected_population)
        message = 'Total affected population is as expected.'
        self.assertEqual(
            total_affected_population,
            300,
            message)
        message = 'Total unaffected population is as expected.'
        self.assertEqual(
            unaffected_population,
            100,
            message)
        message = 'Total affected population is as expected.'
        self.assertEqual(
            total_affected_population,
            300,
            message)
        message = 'Other population is empty.'
        self.assertDictEqual(
            other_population_counts,
            {},
            message
        )
        expected_affected_population = {
            'High': 100,
            'Medium': 100,
            'Low': 100
        }
        message = 'Affected population is as expected.'
        self.assertDictEqual(
            affected_population,
            expected_affected_population,
            message)

    def test_0005_lookup_category(self):
        """Test the category lookup functionality"""
        high = self.population_mixin.lookup_category('High')
        low = self.population_mixin.lookup_category('Low')
        total = self.population_mixin.lookup_category('Total Impacted')
        nothing = self.population_mixin.lookup_category('Nothing')
        message = 'High population category as expected.'
        self.assertEqual(high, 100, message)
        message = 'Low population category as expected.'
        self.assertEqual(low, 100, message)
        message = 'Total population category as expected.'
        self.assertEqual(total, 300, message)
        message = 'Non-existent category should not have anything.'
        self.assertIsNone(nothing, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(PopulationExposureReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
