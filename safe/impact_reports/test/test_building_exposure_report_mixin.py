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

__date__ = '02/04/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from collections import OrderedDict

from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


# noinspection PyArgumentList
class BuildingExposureReportMixinTest(unittest.TestCase):
    """Test the ReportMixin.

    .. versionadded:: 3.1
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests."""
        self.building_mixin_blank = BuildingExposureReportMixin()
        self.building_mixin = BuildingExposureReportMixin()
        self.building_mixin.buildings = {
            'School': 100,
            'University': 10,
            'Residential': 20000,
            'Religious': 3
        }
        self.building_mixin.affected_buildings = OrderedDict([
            ('Hazard Level 2', {
                'School': OrderedDict([
                    ('Affected', 50),
                    ('Value', 90000000)
                ]),
                'University': OrderedDict([
                    ('Affected', 0),
                    ('Value', 0)
                ]),
                'Residential': OrderedDict([
                    ('Affected', 12000),
                    ('Value', 1234567000)
                ]),
                'Religious': OrderedDict([
                    ('Affected', 0),
                    ('Value', 0)
                ])
            }),
            ('Hazard Level 1', {
                'School': OrderedDict([
                    ('Affected', 25),
                    ('Value', 50000000)
                ]),
                'University': OrderedDict([
                    ('Affected', 1),
                    ('Value', 11111111111)
                ]),
                'Residential': OrderedDict([
                    ('Affected', 1000),
                    ('Value', 123456000)
                ]),
                'Religious': OrderedDict([
                    ('Affected', 1),
                    ('Value', 10000000000)
                ])
            })
        ])

    def tearDown(self):
        """Run after each test."""
        del self.building_mixin_blank
        del self.building_mixin

    def test_0001_generate_report(self):
        """Generate a blank report."""
        blank_report = self.building_mixin_blank.generate_report().to_text()
        self.assertIn('**Unaffected buildings**, 0', blank_report)
        self.assertIn('**Building type**, **Total**', blank_report)
        self.assertIn('**Unaffected buildings**, 0', blank_report)

    def test_0002_action_checklist(self):
        """The default action check list."""
        action_checklist = self.building_mixin_blank.action_checklist()
        action_checklist = action_checklist.to_text()
        self.assertIn(
            u'Are the critical facilities still open?',
            action_checklist)
        self.assertIn(
            u'Which structures have warning capacity (eg. sirens, '
            u'speakers, etc.)?',
            action_checklist)
        self.assertIn(
            u'Which buildings will be evacuation centres?',
            action_checklist)
        self.assertIn(
            u'Where will we locate the operations centre?',
            action_checklist
        )
        self.assertIn(
            u'Where will we locate warehouse and/or distribution '
            u'centres?',
            action_checklist
        )
        self.assertNotIn(
            u'Where will the students from the 0 closed schools go to study?',
            action_checklist
        )
        self.assertNotIn(
            u'Where will the patients from the %s closed hospitals '
            u'go for treatment and how will we transport them?',
            action_checklist)

    def test_0003_impact_summary(self):
        """Test the buildings impact summary."""
        impact_summary = self.building_mixin.impact_summary()
        impact_summary = impact_summary.to_text()

        self.assertIn(
            u'**Hazard Level 2**, 12,050, 1,324,567,000', impact_summary)
        self.assertIn(
            u'**Hazard Level 1**, 1,027, 21,284,567,111', impact_summary)
        self.assertIn(u'**Affected buildings**, 13,077', impact_summary)
        self.assertIn(u'**Unaffected buildings**, 7,036', impact_summary)
        self.assertIn(u'**Total**, 20,113', impact_summary)

    def test_0004_buildings_breakdown(self):
        """Test the buildings breakdown."""
        buildings_breakdown = self.building_mixin.buildings_breakdown()
        buildings_breakdown = buildings_breakdown.to_text()
        self.assertIn(u'**Religious**, 0, 1, **3**', buildings_breakdown)
        self.assertIn(
            u'**Residential**, 12,000, 1,000, **20,000**', buildings_breakdown)
        self.assertIn(u'**School**, 50, 25, **100**', buildings_breakdown)
        self.assertIn(u'**University**, 0, 1, **10**', buildings_breakdown)

    def test_0005_schools_closed(self):
        """Test schools closed as expected."""
        schools_closed_default = self.building_mixin_blank.schools_closed
        schools_closed = self.building_mixin.schools_closed
        message = 'Default should not have any closed schools.'
        self.assertEqual(schools_closed_default, 0, message)
        message = 'Schools closed in scenario not as expected.'
        self.assertEqual(schools_closed, 75, message)

    def test_0006_hospitals_closed(self):
        """Test hospitals closed as expected."""
        hospitals_closed_default = self.building_mixin_blank.hospitals_closed
        hospitals_closed = self.building_mixin.hospitals_closed
        message = 'Default should not have any closed hospitals.'
        self.assertEqual(hospitals_closed_default, 0, message)
        message = 'Hospitals closed in scenario not as expected.'
        self.assertEqual(hospitals_closed, 0, message)

    def test_0007_general_methods(self):
        """Test general methods."""
        default_count_usage = self.building_mixin_blank._count_usage('School')
        message = 'Default count is not as expected.'
        self.assertEqual(default_count_usage, 0, message)
        count_usage = self.building_mixin._count_usage('School')
        message = 'Count is not as expected.'
        self.assertEqual(count_usage, 75, message)
        default_impact_breakdown = self.building_mixin_blank._impact_breakdown
        message = 'The default impact breakdown should be empty.'
        self.assertListEqual(default_impact_breakdown, [], message)
        impact_breakdown = self.building_mixin._impact_breakdown
        message = 'The default impact breakdown should be empty.'
        self.assertListEqual(impact_breakdown, ['Affected', 'Value'], message)
        default_categories = self.building_mixin_blank._affected_categories
        message = 'The default categories should be empty.'
        self.assertListEqual(default_categories, [], message)
        categories = self.building_mixin._affected_categories
        message = 'The categories are not as expected.'
        self.assertListEqual(
            categories,
            ['Hazard Level 2', 'Hazard Level 1'],
            message)

    def test_0008_building_counts(self):
        """Test the building counts."""
        default_affected = self.building_mixin_blank.total_affected_buildings
        default_unaffected = (
            self.building_mixin_blank.total_unaffected_buildings)
        default_total = self.building_mixin_blank.total_buildings
        message = 'Defaults counts should be 0.'
        self.assertEqual(default_total, 0, message)
        self.assertEqual(default_unaffected, 0, message)
        self.assertEqual(default_affected, 0, message)
        affected = self.building_mixin.total_affected_buildings
        unaffected = self.building_mixin.total_unaffected_buildings
        total = self.building_mixin.total_buildings
        message = (
            'The total number of buildings should equal the sum of affected '
            'and unaffected.')
        self.assertEqual(total, unaffected + affected, message)
        message = 'The total number of buildings is not as expected.'
        self.assertEqual(total, 20113, message)
        message = 'The affected number of buildings is not as expected.'
        self.assertEqual(affected, 13077, message)
        message = 'The unaffected number of buildings is not as expected.'
        self.assertEqual(unaffected, 7036, message)

    def test_0009_consolidate_to_other(self):
        """Test consolidating smaller building types to 'other'."""
        total_buildings_before = self.building_mixin.total_buildings
        affected_other_before = self.building_mixin._count_usage('Other')
        message = (
            'There should be no affected buildings of type other before '
            'consolidating.')
        self.assertEqual(affected_other_before, 0, message)
        other_in_buildings_before = (
            'Other' in self.building_mixin.buildings.keys())
        message = (
            'There should be no buildings of type other before '
            'consolidation.')
        self.assertFalse(other_in_buildings_before, message)
        self.building_mixin._consolidate_to_other()
        total_buildings_after = self.building_mixin.total_buildings
        message = (
            'The total number of buildings should remain the same '
            'even after consolidation.')
        self.assertEqual(
            total_buildings_before,
            total_buildings_after,
            message)
        affected_other_after = self.building_mixin._count_usage('Other')
        message = 'The affected other buildings are not as expected.'
        self.assertEqual(affected_other_after, 2, message)
        other_in_buildings_after = (
            'Other' in self.building_mixin.buildings.keys())
        message = 'The type other should be in buildings.'
        self.assertTrue(other_in_buildings_after, message)
        total_other_after = self.building_mixin.buildings['Other']
        message = (
            'The total number of other after consolidation is '
            'not as expected.')
        self.assertEqual(total_other_after, 13, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(BuildingExposureReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
