# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Safe Translations Test .**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
import os

from safe.definitions.constants import INASAFE_TEST
from safe.utilities.i18n import tr, locale
from safe.common.utilities import safe_dir

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QCoreApplication, QTranslator

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if 'LANG' in os.environ.iterkeys():
            os.environ.__delitem__('LANG')

    def tearDown(self):
        """Runs after each test."""
        if 'LANG' in os.environ.iterkeys():
            os.environ.__delitem__('LANG')

    def test_impact_summary_words(self):
        """Test specific words from impact summary info shown in doc see #348.
        """
        os.environ['LANG'] = 'id'
        phrase_list = []
        message = 'Specific words checked for translation:\n'
        for phrase in phrase_list:
            if phrase == tr(phrase):
                message += 'FAIL: %s' % phrase
            else:
                message += 'PASS: %s' % phrase
        self.assertNotIn('FAIL', message, message)

        # Set back to en
        os.environ['LANG'] = 'en'

    def test_qgis_translations(self):
        """Test for qgis translations."""
        file_path = safe_dir('i18n/inasafe_id.qm')
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = (
            'Tidak ada informasi gaya yang ditemukan pada lapisan %s')
        real_message = QCoreApplication.translate(
            '@default', 'No styleInfo was found for layer %s')
        message = 'expected %s but got %s' % (expected_message, real_message)
        self.assertEqual(expected_message, real_message, message)

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Travis recognize QgsApplication as a pyqtWrapperType object.')
    def test_qgis_app_locale(self):
        """Test for qgis app locale."""

        from safe.definitions.constants import no_field
        self.assertEqual(no_field, u'No Field')

        # run qgis on bahasa
        _ = get_qgis_app('id', INASAFE_TEST)

        # test if string from inasafe module are translated
        from safe.definitions.constants import no_field
        self.assertNotEqual(no_field, u'No Field')

        expected_locale = 'id'
        self.assertEqual(locale(INASAFE_TEST), expected_locale)

        # check for bahasa translation
        expected_message = (
            'Tidak ada informasi gaya yang ditemukan pada lapisan %s')
        real_message = QCoreApplication.translate(
            '@default', 'No styleInfo was found for layer %s')
        message = 'expected %s but got %s' % (expected_message, real_message)
        self.assertEqual(expected_message, real_message, message)

        # run qgis on english
        _ = get_qgis_app(qsetting=INASAFE_TEST)

        expected_locale = 'en'
        self.assertEqual(locale(INASAFE_TEST), expected_locale)

        # check for english translation
        expected_message = (
            'No styleInfo was found for layer %s')
        real_message = QCoreApplication.translate(
            '@default', 'No styleInfo was found for layer %s')
        message = 'expected %s but got %s' % (expected_message, real_message)
        self.assertEqual(expected_message, real_message, message)

        # Set back to en
        os.environ['LANG'] = 'en'


if __name__ == "__main__":
    suite = unittest.makeSuite(SafeTranslationsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
