# coding=utf-8
"""Test for Settings Utilities."""

import unittest
import os
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from qgis.PyQt.QtCore import QSettings
from safe.definitions.default_settings import inasafe_default_settings
from safe.utilities.settings import (
    general_setting,
    set_general_setting,
    delete_general_setting,
    setting,
    set_setting,
    delete_setting,
    export_setting,
    import_setting,
)
from safe.definitions.utilities import generate_default_profile
from safe.common.utilities import unique_filename

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestSettings(unittest.TestCase):
    """Test Settings."""

    def setUp(self):
        """Fixture run before all tests."""
        self.qsettings = QSettings('InaSAFETest')
        self.qsettings.clear()

    def tearDown(self):
        """Fixture run after each test."""
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
            'key', default='default', qsettings=self.qsettings))

        # Using InaSAFE setting default
        key = 'developer_mode'
        actual_value = inasafe_default_settings.get(key)
        self.assertEqual(actual_value, setting(key, qsettings=self.qsettings))

    def test_read_write_dictionary(self):
        """Test for reading and writing dictionary in QSettings."""
        dictionary = {
            'a': 'a',
            'b': 1,
            'c': {
                'd': True,
                'e': {
                    'f': 1.0,
                    'g': 2
                }
            }
        }
        set_setting('key', dictionary, self.qsettings)
        value = setting('key', qsettings=self.qsettings)
        self.assertDictEqual(dictionary, value)

        profile_dictionary = generate_default_profile()
        set_setting('population_preference', profile_dictionary, self.qsettings)
        value = setting('population_preference', qsettings=self.qsettings)
        self.assertDictEqual(profile_dictionary, value)

    def test_export_import_setting(self):
        """Test for export_setting method."""
        profile_file = unique_filename(suffix='.json', dir='population_preference')
        original_settings = {
            'key': 'value',
            'key_bool': True,
            'population_preference': generate_default_profile(),
            'key_int': 1,
            'key_float': 2.0
        }
        # Write
        for key, value in list(original_settings.items()):
            set_setting(key, value, self.qsettings)
        # Export
        inasafe_settings = export_setting(profile_file, self.qsettings)
        # Check result
        self.assertTrue(os.path.exists(profile_file))
        self.assertEqual(inasafe_settings['key'], 'value')
        self.assertEqual(
            inasafe_settings['population_preference'], generate_default_profile())
        # Import
        read_setting = import_setting(profile_file, self.qsettings)
        self.assertDictEqual(inasafe_settings, read_setting)
        self.assertDictEqual(original_settings, read_setting)


if __name__ == '__main__':
    unittest.main()
