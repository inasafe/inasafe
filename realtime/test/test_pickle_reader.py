# coding=utf-8
"""Module for testing generating static html file from shake pickles.

InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Event Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '22/10/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
import shutil
from glob import glob

#from safe.api import temp_dir

from realtime.pickle_reader import create_index, generate_pages


class TestPickleReader(unittest.TestCase):
    """Tests relating to shake events"""

    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir"""
        self.shakemap_dir_en = '/tmp/en/'
        self.shakemap_dir_id = '/tmp/id/'

        pickle_path_list = glob(os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'fixtures',
            'tests',
            '*.pickle'))

        for pickle_path in pickle_path_list:
            shutil.copy(pickle_path, self.shakemap_dir_en)
            shutil.copy(pickle_path, self.shakemap_dir_id)

    def test_create_index(self):
        """Test we can generate index.html file."""
        result = create_index(shakemap_dir=self.shakemap_dir_en, locale='en')
        index_file = file(result, 'r')
        result = index_file.read()
        index_file.close()
        self.assertIn('Banda Aceh', result)

        # Test if locale is other than en or id:
        with self.assertRaises(BaseException):
            create_index(shakemap_dir=self.shakemap_dir_en,
                         locale='ens')

    def test_generate_pages(self):
        """Test we can generate index.html for both en and id."""
        en_path, id_path = generate_pages(
            shakemap_dir_en=self.shakemap_dir_en,
            shakemap_dir_id=self.shakemap_dir_id)
        expected_en_path = self.shakemap_dir_en + 'index.html'
        expected_id_path = self.shakemap_dir_id + 'index.html'
        self.assertEqual(expected_id_path, id_path)
        self.assertEqual(expected_en_path, en_path)
