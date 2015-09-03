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

    def tearDown(self):
        """Run after each test."""
        del self.road_mixin_blank
        del self.road_mixin

    def test_0001_generate_report(self):
        """Generate a blank report."""
        blank_report = self.road_mixin_blank.generate_report()
        expected_blank_report = [
            {'content': ''},
            {'content': ''},
            {'content': [u'Road Type', u'Total (m)'], 'header': True},
            {'content': [u'All', '0']},
            {'content': ''},
            {'content': u'Breakdown by road type', 'header': True},
            {'content': ''},
            {'content': ''}]
        message = 'Blank report is not as expected.'
        self.assertListEqual(blank_report, expected_blank_report, message)

    def test_0002_road_breakdown(self):
        """Test the buildings breakdown."""
        roads_breakdown = self.road_mixin.roads_breakdown()
        expected_roads_breakdown = [
            {'content': u'Breakdown by road type', 'header': True},
            {'content': ['Main', '133']},
            {'content': ['Side', '10']},
            {'content': ['Bike', '1']}]
        message = 'roads breakdown is not as expected.'
        self.assertListEqual(
            roads_breakdown,
            expected_roads_breakdown,
            message)

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
