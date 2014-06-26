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
__author__ = 'ismailsunni@yahoo.co.id'
__date__ = '12/10/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import os
import re

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.safe_interface import safeTr, get_function_title, get_plugins
from PyQt4.QtCore import QCoreApplication, QTranslator


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

    def test_dynamic_translation_function_title(self):
        """Test for dynamic translations for function title."""
        plugins_dict = get_plugins()
        plugin_name = 'Volcano Building Impact'
        message = '%s not found in %s' % (plugin_name, str(plugins_dict))
        self.assertIn(plugin_name, plugins_dict, message)
        function = plugins_dict[plugin_name]

        # English
        function_title = get_function_title(function)
        expected_title = 'Be affected'
        message = 'Expected %s but I got %s' % (expected_title, function_title)
        self.assertEqual(expected_title, function_title, message)

        # Indonesia
        os.environ['LANG'] = 'id'
        function_title = get_function_title(function)
        expected_title = 'Terkena dampak'
        message = ('expected %s but got %s, in lang = %s' % (
            expected_title, function_title, os.environ['LANG']))
        self.assertEqual(expected_title, function_title, message)

    def test_dynamic_translation(self):
        """Test for dynamic translations for a string."""

        # English
        function_title = 'Be affected'
        expected_title = safeTr('Be affected')
        message = 'Expected %s but got %s' % (expected_title, function_title)
        self.assertEqual(function_title, expected_title, message)

        # Indonesia
        os.environ['LANG'] = 'id'
        function_title = 'Be affected'
        real_title = safeTr(function_title)
        expected_title = 'Terkena dampak'
        message = 'expected %s but got %s' % (expected_title, real_title)
        self.assertEqual(expected_title, real_title, message)

    def test_impact_summary_words(self):
        """Test specific words from impact summary info shown in doc see #348.
        """
        os.environ['LANG'] = 'id'
        phrase_list = []
        message = 'Specific words checked for translation:\n'
        for phrase in phrase_list:
            if phrase == safeTr(phrase):
                message += 'FAIL: %s' % phrase
            else:
                message += 'PASS: %s' % phrase
        self.assertNotIn('FAIL', message, message)

    def test_all_dynamic_translations(self):
        """Test all the phrases defined in dynamic_translations translate."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(
            dir_path, '../safe', 'common', 'dynamic_translations.py')
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
                    translation = safeTr(cleaned_line)
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

    def test_qgis_translations(self):
        """Test for qgis translations."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(dir_path, 'i18n', 'inasafe_id.qm')
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = (
            'Tidak ada informasi gaya yang ditemukan pada lapisan %s')
        real_message = QCoreApplication.translate(
            "@default", 'No styleInfo was found for layer %s')
        message = 'expected %s but got %s' % (expected_message, real_message)
        self.assertEqual(expected_message, real_message, message)


if __name__ == "__main__":
    suite = unittest.makeSuite(SafeTranslationsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
