# coding=utf-8
"""Tests for utilities."""

import unittest
import os
import codecs
from unittest import expectedFailure

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    standard_data_path,
    get_qgis_app,
)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.utilities.utilities import (
    humanise_seconds,
    replace_accentuated_characters,
    is_plugin_installed,
    is_keyword_version_supported
)
from safe.utilities.gis import qgis_version
from safe.utilities.help import get_help_html
from safe.utilities.resources import (
    html_footer,
    html_help_header,
)
from safe.messaging import Message
from safe.gui.tools.help.dock_help import dock_help

class UtilitiesTest(unittest.TestCase):

    """Tests for reading and writing of raster and vector data."""

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_get_qgis_version(self):
        """Test we can get the version of QGIS."""
        version = qgis_version()
        message = 'Got version %s of QGIS, but at least 214000 is needed'
        self.assertTrue(version > 21400, message)

    def test_humanize_seconds(self):
        """Test that humanise seconds works."""
        self.assertEqual(humanise_seconds(5), '5 seconds')
        self.assertEqual(humanise_seconds(65), 'a minute')
        self.assertEqual(humanise_seconds(3605), 'over an hour')
        self.assertEqual(humanise_seconds(9000), '2 hours and 30 minutes')
        self.assertEqual(humanise_seconds(432232),
                         '5 days, 0 hours and 3 minutes')

    def test_accentuated_characters(self):
        """Test that accentuated characters has been replaced."""
        self.assertEqual(
            replace_accentuated_characters('áéíóúýÁÉÍÓÚÝ'), 'aeiouyAEIOUY')

    def test_is_keyword_version_supported(self):
        """Test for is_keyword_version_supported."""
        self.assertTrue(is_keyword_version_supported('3.2', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2', '3.3'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1-alpha', '3.2'))
        self.assertTrue(is_keyword_version_supported('3.2.1', '3.3'))
        self.assertFalse(is_keyword_version_supported('3.02.1', '3.2'))

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'The plugin is not installed under the same directory in Travis.')
    def test_if_plugin_is_installed(self):
        """Test if we can know if a plugin is installed."""
        self.assertTrue(is_plugin_installed('inasafe'))
        self.assertFalse(is_plugin_installed('inasafeZ'))


    def test_get_help_html(self):
        """Test that get_help_html works"""

        # no message: default to dock_help
        text = get_help_html()
        self.assertTrue(html_help_header() in text)
        self.assertTrue(html_footer() in text)
        self.assertTrue(dock_help().to_html() in text)

        # custom message
        message = Message("A text message")
        text = get_help_html(message)
        self.assertTrue(message.to_html() in text)




if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
