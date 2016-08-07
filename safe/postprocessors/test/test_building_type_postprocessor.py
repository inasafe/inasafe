# -*- coding: utf-8 -*-
"""**Postprocessors package.**

Test building type postprocessor
"""

import unittest

from safe.postprocessors.building_type_postprocessor import (
    BuildingTypePostprocessor)

__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '21/07/2015'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


class TestBuildingTypePostprocessor(unittest.TestCase):
    postprocessor = BuildingTypePostprocessor()

    def tearDown(self):
        """Run after each test."""
        self.postprocessor.clear()

    def test_process_integer_values(self):
        """Test for checking when the value is integer."""
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            'Building type': True,
            'target_field': 'affected',
            'value_mapping': {'government': ['Government']},
            'impact_attrs': [
                {'type': 'Government', 'affected': 1},
                {'type': 'Government', 'affected': 0},
                {'type': 'Government', 'affected': 1},
                {'type': 'Government', 'affected': 0},
            ]}
        self.postprocessor.setup(params)
        self.postprocessor.process()
        results = self.postprocessor.results()
        self.assertEqual(results['Government']['value'], '2')

    def test_process_string_values(self):
        """Test for checking when the value is string."""
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            'Building type': True,
            'target_field': 'affected',
            'value_mapping': {'government': ['Government']},
            'impact_attrs': [
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Government', 'affected': 'Not Affected'},
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Government', 'affected': 'Not Affected'},
            ]}
        self.postprocessor.setup(params)
        self.postprocessor.process()
        results = self.postprocessor.results()
        self.assertEqual(results['Government']['value'], '2')

    def test_total_affected_calculated_correctly(self):
        """Test for checking the total affected and value mapping"""
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            'Building type': True,
            'target_field': 'affected',
            'value_mapping': {
                'government': ['Government'],
                'economy': ['Economy'],
            },
            'impact_attrs': [
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Museum', 'affected': 'Zone 2'},
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Government', 'affected': 'Not Affected'},
                {'type': 'School', 'affected': 'Zone 3'},
            ]}
        self.postprocessor.setup(params)
        self.postprocessor.process()
        results = self.postprocessor.results()
        self.assertEqual(results['Government']['value'], '2')
        self.assertEqual(results['Other']['value'], '2')

        self.postprocessor.clear()
        # Same as above, but we add the school in the value mapping.
        params = {
            'impact_total': 0,
            'key_attribute': 'type',
            'Building type': True,
            'target_field': 'affected',
            'value_mapping': {
                'government': ['Government', 'School'],
                'economy': ['Economy'],
            },
            'impact_attrs': [
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Museum', 'affected': 'Zone 2'},
                {'type': 'Government', 'affected': 'Zone 1'},
                {'type': 'Government', 'affected': 'Not Affected'},
                {'type': 'School', 'affected': 'Zone 3'},
            ]}
        self.postprocessor.setup(params)
        self.postprocessor.process()
        results = self.postprocessor.results()
        self.assertEqual(results['Government']['value'], '3')
        self.assertEqual(results['Other']['value'], '1')


if __name__ == '__main__':
    suite = unittest.makeSuite(TestBuildingTypePostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
