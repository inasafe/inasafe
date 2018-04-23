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
from builtins import str

import unittest
import os
import re
from safe.utilities.i18n import tr
from safe.common.utilities import safe_dir

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QCoreApplication, QTranslator

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if 'LANG' in iter(os.environ.keys()):
            os.environ.__delitem__('LANG')

    def tearDown(self):
        """Runs after each test."""
        if 'LANG' in iter(os.environ.keys()):
            os.environ.__delitem__('LANG')

    # Skipped because it's not easy to unload qt translation
    def Xtest_dynamic_translation(self):
        """Test for dynamic translations for a string."""

        # English
        function_title = 'Be affected'
        expected_title = tr('Be affected')
        message = 'Expected %s but got %s' % (expected_title, function_title)
        self.assertEqual(function_title, expected_title, message)

        # Indonesia
        os.environ['LANG'] = 'id'
        function_title = 'Be affected'
        real_title = tr(function_title)
        expected_title = 'Terkena dampak'
        message = 'expected %s but got %s' % (expected_title, real_title)
        self.assertEqual(expected_title, real_title, message)

        # Set back to en
        os.environ['LANG'] = 'en'

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

    # Skipped because it's not easy to unload qt translation
    def Xtest_all_dynamic_translations(self):
        """Test all the phrases defined in dynamic_translations translate."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.abspath(os.path.join(
            dir_path, os.pardir, 'safe', 'common', 'dynamic_translations.py'))
        translations_file = file(file_path)
        failure_list = []
        os.environ['LANG'] = 'id'
        line_count = 0
        # exception_words is a list of words that has the same form in both
        # English and Indonesian. For example hotel, bank
        exception_words = ['hotel', 'bank', 'Area']
        for line in translations_file.readlines():
            line_count += 1
            if 'tr(' in line:
                match = re.search(r'\(\'(.*)\'\)', line, re.M | re.I)
                if match:
                    group = match.group()
                    cleaned_line = group[2:-2]
                    if cleaned_line in exception_words:
                        continue
                    translation = tr(cleaned_line)
                    if cleaned_line == translation:
                        failure_list.append(cleaned_line)

        message = (
            'Translations not found for:\n %s\n%i of %i untranslated\n' % (
                str(failure_list).replace(',', '\n'), len(failure_list),
                line_count))
        message += (
            'If you think the Indonesian word for the failed translations is '
            'the same form in English, i.e. "hotel", you can add it in '
            'exception_words in safe_qgis/test_safe_translations.py')
        self.assertEqual(len(failure_list), 0, message)

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


if __name__ == "__main__":
    suite = unittest.makeSuite(SafeTranslationsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
