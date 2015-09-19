# coding=utf-8
"""Unit tests for the defaults module."""

import os
import unittest

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QFile

from safe.defaults import (
    disclaimer,
    get_defaults,
    black_inasafe_logo_path,
    white_inasafe_logo_path,
    supporters_logo_path,
    default_north_arrow_path)


class TestDefaults(unittest.TestCase):
    """Tests for working with the defaults module.
    """

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_get_defaults(self):
        """Test we can get the defaults.
        """
        expected = {
            'ADULT_RATIO_KEY': 'adult ratio default',
            'ADULT_RATIO_ATTR_KEY': 'adult ratio attribute',
            'ADULT_RATIO': 0.659,

            'FEMALE_RATIO_KEY': 'female ratio default',
            'FEMALE_RATIO_ATTR_KEY': 'female ratio attribute',
            'FEMALE_RATIO': 0.5,

            'ELDERLY_RATIO_ATTR_KEY': 'elderly ratio attribute',
            'ELDERLY_RATIO_KEY': 'elderly ratio default',
            'ELDERLY_RATIO': 0.078,

            'YOUTH_RATIO': 0.263,
            'YOUTH_RATIO_ATTR_KEY': 'youth ratio attribute',
            'YOUTH_RATIO_KEY': 'youth ratio default',

            'NO_DATA': u'No data',

            'AGGR_ATTR_KEY': 'aggregation attribute',
            'ISO19115_EMAIL': 'info@inasafe.org',
            'ISO19115_LICENSE': 'Free use with accreditation',
            'ISO19115_ORGANIZATION': 'InaSAFE.org',
            'ISO19115_TITLE': 'InaSAFE analysis result',
            'ISO19115_URL': 'http://inasafe.org'}

        actual = get_defaults()
        self.maxDiff = None
        self.assertDictEqual(expected, actual)

    def test_disclaimer(self):
        """Verify the disclaimer works.

        This text will probably change a lot so just test to ensure it is
        not empty.
        """
        actual = disclaimer()
        self.assertTrue(len(actual) > 0)

    def test_white_inasafe_logo_path(self):
        """Verify the call to default InaSAFE logo path works.
        """
        # Check if it exists
        logo_path = QFile(white_inasafe_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_black_inasafe_logo_path(self):
        """Verify the call to default InaSAFE logo path works.
        """
        # Check if it exists
        logo_path = QFile(black_inasafe_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_supporters_logo_path(self):
        """Verify the call to default supporters logo path works.
        """
        # Check if it exists
        logo_path = QFile(supporters_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_default_north_arrow_path(self):
        """Verify the call to default north arrow path works.
        """
        # Check if it exists
        path = QFile(default_north_arrow_path())
        self.assertTrue(QFile.exists(path))
