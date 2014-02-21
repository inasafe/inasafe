# coding=utf-8
"""Unit tests for the defaults module."""

import os
import unittest
from safe_qgis.utilities.defaults import breakdown_defaults, disclaimer


class TestDefaults(unittest.TestCase):
    """Tests for working with the defaults module.
    """

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_breakdown_defaults(self):
        """Test we can get breakdown defaults.
        """
        expected = {
            'FEM_RATIO_KEY': 'female ratio default',
            'YOUTH_RATIO': 0.263,
            'ELDER_RATIO': 0.078,
            'NO_DATA': u'No data',
            'FEM_RATIO': 0.5,
            'AGGR_ATTR_KEY': 'aggregation attribute',
            'FEM_RATIO_ATTR_KEY': 'female ratio attribute',
            'ADULT_RATIO': 0.659}
        actual = breakdown_defaults()
        self.assertEquals(expected, actual)

    def test_disclaimer(self):
        """Verify the disclaimer works.

        This text will proably change a lot so just test to ensure it is
        not empty.
        """
        actual = disclaimer()
        self.assertTrue(len(actual) > 0)
