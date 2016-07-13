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
        self.road_mixin_blank.question = ''
        self.road_mixin.question = ''
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

    def test_0001_generate_blank_data(self):
        """Generate a blank data."""
        blank_data = self.road_mixin_blank.generate_data()
        self.maxDiff = None
        expected = {
            'action check list': {
                'fields': [
                    'Which roads can be used to evacuate people or to '
                    'distribute logistics?',
                    'What type of vehicles can use the unaffected roads?',
                    'What sort of equipment will be needed to reopen roads & '
                    'where will we get it?',
                    'Which government department is responsible for '
                    'supplying equipment ?'
                ],
                'title': 'Action checklist'
            },
            'exposure': 'road',
            'impact summary': {
                'attributes': ['category', 'value'],
                'fields': [['Unaffected', 0], ['Total', 0]]},
            'impact table': {
                'attributes': [
                    'Road Type', 'Unaffected', 'Total'],
                'fields': []
            },
            'notes': {'fields': [], 'title': 'Notes and assumptions'},
            'question': ''}
        self.assertDictEqual(expected, blank_data)

    def test_0002_road_breakdown(self):
        """Test the buildings breakdown."""
        roads_breakdown = self.road_mixin.impact_table()['fields']

        expected = [
            ['Main', 2, 131.3, 133.3],
            ['Side', 5.5, 4.5, 10],
            ['Bike', 1.2, 0.0, 1.2]
        ]

        self.assertEquals(roads_breakdown, expected)

    def test_0003_total(self):
        """Test general methods."""
        default_length = self.road_mixin_blank.total_road_length
        message = 'Default length is not as expected.'
        self.assertEqual(default_length, 0, message)

        message = 'Real length is not as expected.'
        length = self.road_mixin.total_road_length
        self.assertEqual(length, 144.5, message)

    def test_0004_generate_data(self):
        """Test generating data."""
        self.maxDiff = None
        data = self.road_mixin.generate_data()
        expected = {
            'action check list': {
                'fields': [
                    'Which roads can be used to evacuate people or to '
                    'distribute logistics?',
                    'What type of vehicles can use the unaffected roads?',
                    'What sort of equipment will be needed to reopen roads & '
                    'where will we get it?',
                    'Which government department is responsible for '
                    'supplying equipment ?'
                ],
                'title': 'Action checklist'
            },
            'exposure': 'road',
            'impact summary': {
                'attributes': ['category', 'value'],
                'fields': [
                    ['Flooded', 8.7],
                    ['Unaffected', 135.8],
                    ['Total', 144.5]
                ]
            },
            'impact table': {
                'attributes': [
                    'Road Type', 'Flooded', 'Unaffected', 'Total'
                ],
                'fields': [
                    ['Main', 2, 131.3, 133.3],
                    ['Side', 5.5, 4.5, 10],
                    ['Bike', 1.2, 0.0, 1.2]
                ]
            },
            'notes': {
                'fields': [],
                'title': 'Notes and assumptions'
            },
            'question': ''
        }
        self.assertDictEqual(data, expected)


if __name__ == '__main__':
    suite = unittest.makeSuite(RoadExposureReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
