# coding=utf-8
"""
Minimum Needs Tool Test Cases.

InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : christian@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from past.builtins import cmp

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.PyQt.QtCore import QSettings
import json

from parameters.parameter_exceptions import (
    InvalidMaximumError,
    ValueOutOfBounds)

from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.common.minimum_needs import MinimumNeeds


class TestNeedsProfile(NeedsProfile):
    """Since we don't want to change the actual minimum needs settings in
    QSettings, we are using a mock profile.

    :param test_profile: The mock replacement of Minimum Needs
    """
    # noinspection PyMissingConstructor
    def __init__(self, test_profile='Test Minimum Needs Settings'):
        self.settings = QSettings(test_profile)
        self.settings.clear()
        self.settings = QSettings(test_profile)
        self.local = 'en'
        minimum_needs = self._defaults()
        minimum_needs['provenance'] = 'Test'
        minimum_needs['profile'] = 'Test'
        self._root_directory = None
        self.minimum_needs = minimum_needs

    def __del__(self):
        self.settings.clear()


class MinimumNeedsTest(unittest.TestCase):
    """Test class to test QMinimum needs."""

    def setUp(self):
        """Test initialisation run before each test."""
        self.minimum_needs = TestNeedsProfile()

    def tearDown(self):
        """Run after each test."""
        self.minimum_needs.settings.clear()

    def test_precision_of(self):
        """Test determining precision of json file min needs resources."""
        resources = self.minimum_needs.minimum_needs['resources']
        default_precisions = []
        precision_influence = ['Maximum allowed', 'Minimum allowed', 'Default']
        for resource in resources:
            precisions = [1]
            for element in precision_influence:
                if resource[element] is not None and '.' in resource[element]:
                    precisions.append(
                        self.minimum_needs.precision_of(resource[element]))

            default_precisions.append(max(precisions))
        self.assertEqual([1, 1, 1, 1, 2], default_precisions)

    def test_01_loading_defaults(self):
        """Test loading the defaults on a blank settings."""
        full_minimum_needs = self.minimum_needs.get_full_needs()['resources']
        default_minimum_needs = MinimumNeeds._defaults()['resources']
        self.assertEqual(cmp(full_minimum_needs, default_minimum_needs), 0)

    def test_02_update_minimum_needs(self):
        """Change minimum needs and verify that the result are updated."""
        original_old = self.minimum_needs.get_full_needs()
        new_minimum_needs = {
            'resources': [{
                "Default": "5",
                "Minimum allowed": "1",
                "Maximum allowed": "10",
                "Frequency": "weekly",
                "Resource name": "Test resource",
                "Resource description": "Basic food",
                "Unit": "kilogram",
                "Units": "kilograms",
                "Unit abbreviation": "kg",
                "Readable sentence": (
                    "A displaced person should be provided with {{ Default }} "
                    "{{ Unit }}/{{ Units }}/{{ Unit abbreviation }} of "
                    "{{ Resource name }}. Though no less than "
                    "{{ Minimum allowed }} and no more than "
                    "{{ Maximum allowed }}. This should be provided "
                    "{{ Frequency }}.")
            }],
            'provenance': "Test",
            'profile': "Test"
        }
        self.minimum_needs.update_minimum_needs(new_minimum_needs)
        other_minimum_needs = TestNeedsProfile(test_profile='Other Test')
        other_old = other_minimum_needs.get_full_needs()

        original_new = self.minimum_needs.get_full_needs()

        # cmp compares dicts 0 == same, -1 == different
        self.assertEqual(cmp(original_old, other_old), 0)
        self.assertEqual(cmp(original_old, original_new), -1)

    def test_03_root_directory(self):

        minimum_needs2 = TestNeedsProfile()
        self.assertIsNone(minimum_needs2._root_directory)
        if minimum_needs2.root_directory:
            self.assertIsNotNone(minimum_needs2._root_directory)
        self.assertEqual(
            minimum_needs2.root_directory,
            minimum_needs2._root_directory
        )

    def test_issue_2132(self):
        """Test that floats are cast to strings for precision handler."""
        profile = TestNeedsProfile()
        json_string = (
            '{"resources": [{'
            '"Resource name": "Rice", '
            '"Frequency": "weekly", '
            '"Default": 2.8, '
            '"Maximum allowed": 5.0, '
            '"Minimum allowed": 1.0, '
            '"Unit": "kg",'
            '"Units": "kgs",'
            '"Unit abbreviation": "kg",'
            '"Resource description": "Rice as a staple food",'
            '"Readable sentence": "Test sentence"'
            '}],'
            '"provenance": "Test provenance"}')
        profile.minimum_needs = json.loads(json_string)
        profile.get_needs_parameters()

    def test_maximum_greater_than_minimum(self):
        """Test that that if maximum is less than minimum causes error."""
        profile = TestNeedsProfile()
        json_string = (
            '{"resources": [{'
            '"Resource name": "Rice", '
            '"Frequency": "weekly", '
            '"Default": 2.8, '
            '"Maximum allowed": 6.0, '
            '"Minimum allowed": 7.0, '
            '"Unit": "kg",'
            '"Units": "kgs",'
            '"Unit abbreviation": "kg",'
            '"Resource description": "Rice as a staple food",'
            '"Readable sentence": "Test sentance"'
            '}]}')
        profile.minimum_needs = json.loads(json_string)
        self.assertRaises(InvalidMaximumError, profile.get_needs_parameters)

    def test_default_is_valid(self):
        """Test that that if maximum is less than minimum causes error."""
        profile = TestNeedsProfile()
        json_string = (
            '{"resources": [{'
            '"Resource name": "Rice", '
            '"Frequency": "weekly", '
            '"Default": 10, '
            '"Maximum allowed": 9.0, '
            '"Minimum allowed": 2.0, '
            '"Unit": "kg",'
            '"Units": "kgs",'
            '"Unit abbreviation": "kg",'
            '"Resource description": "Rice as a staple food",'
            '"Readable sentence": "Test sentance"'
            '}]}')
        profile.minimum_needs = json.loads(json_string)
        self.assertRaises(ValueOutOfBounds, profile.get_needs_parameters)
