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

__date__ = '25/08/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from collections import OrderedDict

from safe.impact_reports.road_exposure_report_mixin import (
    RoadExposureReportMixin)


# noinspection PyArgumentList
class RoadExposureReportMixinTest(unittest.TestCase):
    """Test the ReportMixin.

    .. versionadded:: 3.2
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests."""
        self.road_mixin_blank = RoadExposureReportMixin()
        self.road_mixin = RoadExposureReportMixin()
        self.road_mixin.road_lengths = OrderedDict([
            ('Main', 133.3),
            ('Side', 10),
            ('Bike', 1.2)])
        self.road_mixin.affected_road_lengths = OrderedDict([
            ('Flooded', {
                'Main': 2,
                'Side': 5.5,
                'Bike': 1.2})
        ])
        self.road_mixin.affected_road_categories = ['Flooded']

    def tearDown(self):
        """Run after each test."""
        del self.road_mixin_blank
        del self.road_mixin

    def test_0001_generate_report(self):
        """Generate a blank report."""
        blank_report = self.road_mixin_blank.generate_report().to_text()
        # self.assertListEqual(blank_report, expected_blank_report, message)
        self.assertIn('**Road Type**', blank_report)
        self.assertIn('**Total (m)**', blank_report)

    def test_0002_road_breakdown(self):
        """Test the buildings breakdown."""
        roads_breakdown = self.road_mixin.roads_breakdown().to_text()

        self.assertIn('**Breakdown by road type**', roads_breakdown)
        self.assertIn('Main', roads_breakdown)
        self.assertIn('133', roads_breakdown)
        self.assertIn('Side', roads_breakdown)
        self.assertIn('10', roads_breakdown)
        self.assertIn('Bike', roads_breakdown)
        self.assertIn('1', roads_breakdown)

    def test_0003_total(self):
        """Test general methods."""
        default_length = self.road_mixin_blank.total_road_length
        length = self.road_mixin.total_road_length
        message = 'Default length is not as expected.'
        self.assertEqual(default_length, 0, message)
        message = 'Real length is not as expected.'
        self.assertEqual(length, 144.5, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(RoadExposureReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
