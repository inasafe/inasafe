# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Table Tests implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import tempfile
import unittest
import json
from collections import OrderedDict
from safe.common.minimum_needs import MinimumNeeds


class MinimumNeedsTest(unittest.TestCase):
    """Test the SAFE Table"""
    tmp_dir = None

    def setUp(self):
        """Fixture run before all tests"""
        self.minimum_needs = MinimumNeeds()
        self.minimum_needs .update_minimum_needs([
            {'resource': 'Test Resource 1', 'amount': 100, 'unit': 'kg',
                'frequency': 'weekly', 'provenance': 'TEST'},
            {'resource': 'Test Resource 2', 'amount': 0.1, 'unit': 'l',
                'frequency': 'weekly', 'provenance': 'TEST'},
        ])

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_01_metadata(self):
        """Test the metadata."""
        self.assertEqual(
            len(self.minimum_needs._full_category_descriptions()),
            len(self.minimum_needs.categories))
        self.assertEqual(
            len(self.minimum_needs._full_category_descriptions()),
            len(self.minimum_needs.headings))
        self.assertEqual(
            len(self.minimum_needs._full_category_descriptions()),
            len(self.minimum_needs.category_types))

    def test_02_needs(self):
        """Test the interaction with needs."""
        self.assertEqual(
            self.minimum_needs.get_minimum_needs(),
            OrderedDict([
                ['Test Resource 1', 100],
                ['Test Resource 2', 0.1]
            ])
        )
        # Adding new
        self.minimum_needs.set_need(
            'Test Resource 3',
            10,
            'kg',
        )
        self.assertEqual(
            self.minimum_needs.get_minimum_needs(),
            OrderedDict([
                ['Test Resource 1', 100],
                ['Test Resource 2', 0.1],
                ['Test Resource 3', 10]
            ])
        )
        last_added = self.minimum_needs.get_full_needs()[-1]
        self.assertEqual(
            cmp(
                last_added,
                {
                    'resource': 'Test Resource 3',
                    'amount': 10,
                    'unit': 'kg',
                    'frequency': 'weekly',
                    'provenance': ''
                }
            ),
            0
        )

    def test_03_file_write(self):
        """Test the writing to files."""
        (fd, file_name) = tempfile.mkstemp()
        os.close(fd)
        self.minimum_needs.write_to_file(file_name)
        fd = open(file_name)
        needs_file = json.loads(fd.read())
        self.assertEqual(
            cmp(
                self.minimum_needs.get_full_needs(),
                needs_file
            ), 0
        )
        fd.close()
        os.remove(file_name)

    def test_04_file_read(self):
        """Test reading from a file."""
        json_needs = (
            '[{"provenance": "TEST FILE WRITE", "amount": 1,'
            '"frequency": "weekly", "resource": "Test Resource File",'
            '"unit": "tonne"}]')
        (fd, file_name) = tempfile.mkstemp()
        os.write(fd, json_needs)
        os.close(fd)
        self.minimum_needs.read_from_file(file_name)
        loaded_needs = self.minimum_needs.get_full_needs()
        self.assertEqual(
            cmp(
                loaded_needs,
                json.loads(json_needs)
            ), 0
        )
        os.remove(file_name)

if __name__ == '__main__':
    suite = unittest.makeSuite(MinimumNeedsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
