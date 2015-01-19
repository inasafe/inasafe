# coding=utf-8
import unittest
import os
from safe import TranslationLoadError

from safe.utilities.i18n import (
    tr,
    locale,
    load_translation,
    translation_file)


class TestI18N(unittest.TestCase):

    def setUp(self):
        """Run before each test."""
        os.environ['INASAFE_LANG'] = 'en_US'

    @unittest.expectedFailure
    def test_tr(self):
        """Test tr function works.

        It would be nice to test like this but Qt unload/reload of
        translations is pretty awkward (read: not doable) at run time.

        """
        untranslated = 'Hello'
        translated = 'Halo'
        result = tr(untranslated)
        self.assertEqual(result, translated)

    def test_locale(self):
        """Test locale function works."""
        expected = 'en_US'
        result = locale()
        self.assertEqual(result, expected)
        os.environ['INASAFE_LANG'] = 'id'
        expected = 'id'
        result = locale()
        self.assertEqual(result, expected)

    def test_translation_file(self):
        """Test translation file works."""
        os.environ['INASAFE_LANG'] = 'id'
        expected = 'inasafe_id.qm'
        result = translation_file()
        self.assertIn(expected, result)
        self.assertTrue(os.path.exists(result))

    def test_load_translation(self):
        """Test load translation works."""
        os.environ['INASAFE_LANG'] = 'XX'
        self.assertRaises(TranslationLoadError, load_translation)


if __name__ == '__main__':
    unittest.main()
