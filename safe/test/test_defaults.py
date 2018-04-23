# coding=utf-8
"""Unit tests for the defaults module."""

import os
import unittest

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QFile

from safe.defaults import (
    black_inasafe_logo_path,
    white_inasafe_logo_path,
    supporters_logo_path,
    default_north_arrow_path)


class TestDefaults(unittest.TestCase):
    """Tests for working with the defaults module."""

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_white_inasafe_logo_path(self):
        """Verify the call to default InaSAFE logo path works."""
        # Check if it exists
        logo_path = QFile(white_inasafe_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_black_inasafe_logo_path(self):
        """Verify the call to default InaSAFE logo path works."""
        # Check if it exists
        logo_path = QFile(black_inasafe_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_supporters_logo_path(self):
        """Verify the call to default supporters logo path works."""
        # Check if it exists
        logo_path = QFile(supporters_logo_path())
        self.assertTrue(QFile.exists(logo_path))

    def test_default_north_arrow_path(self):
        """Verify the call to default north arrow path works."""
        # Check if it exists
        path = QFile(default_north_arrow_path())
        self.assertTrue(QFile.exists(path))
