# coding=utf-8
"""Test for Settings Utilities."""

import unittest
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from PyQt4.QtCore import QSettings
from safe.definitions.default_settings import inasafe_default_settings
from safe.utilities.settings import (
    general_setting,
    set_general_setting,
    delete_general_setting,
    setting,
    set_setting,
    delete_setting
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestSettings(unittest.TestCase):
    """Test Settings"""

    def setUp(self):
        """Fixture run before all tests"""
        self.qsettings = QSettings('InaSAFETest')
        self.qsettings.clear()

    def tearDown(self):
        """Fixture run after each test"""
        # Make sure it's empty
        self.qsettings.clear()

    def test_read_write_setting(self):
        """Test read and write setting."""
        # General Setting
        set_general_setting('key', 'value', self.qsettings)
        self.assertEqual(
            'value', general_setting('key', qsettings=self.qsettings))
        delete_general_setting('key', qsettings=self.qsettings)
        self.assertEqual('default', general_setting(
            'key', default='default', qsettings=self.qsettings))

        set_general_setting('key', 'True', self.qsettings)
        self.assertEqual(
            'True',
            general_setting(
                'key', qsettings=self.qsettings, expected_type=str))
        self.assertEqual(
            True,
            general_setting(
                'key', qsettings=self.qsettings, expected_type=bool))
        delete_general_setting('key', qsettings=self.qsettings)
        self.assertEqual('default', general_setting(
            'key', default='default', qsettings=self.qsettings))

        set_general_setting('key', 'false', self.qsettings)
        self.assertEqual(
            'false',
            general_setting(
                'key', qsettings=self.qsettings, expected_type=str))
        self.assertEqual(
            False,
            general_setting(
                'key', qsettings=self.qsettings, expected_type=bool))
        delete_general_setting('key', qsettings=self.qsettings)
        self.assertEqual('default', general_setting(
            'key', default='default', qsettings=self.qsettings))

        # Under InaSAFE scope
        set_setting('key', 'value', self.qsettings)
        self.assertEqual('value', setting('key', qsettings=self.qsettings))
        delete_setting('key', qsettings=self.qsettings)
        self.assertEqual('default', setting(
            'key',default='default', qsettings=self.qsettings))

        # Using InaSAFE setting default
        key = 'developer_mode'
        actual_value = inasafe_default_settings.get(key)
        self.assertEqual(actual_value, setting(key, qsettings=self.qsettings))


if __name__ == '__main__':
    unittest.main()
