# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Table Tests implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from past.builtins import cmp

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
    """Test the SAFE Table."""
    tmp_dir = None

    def setUp(self):
        """Fixture run before all tests."""
        self.minimum_needs = MinimumNeeds()
        self.minimum_needs.update_minimum_needs({
            'resources': [
                {
                    'Resource name': 'Test Resource 1',
                    'Default': 100,
                    'Unit abbreviation': 'kg',
                    'Frequency': 'weekly'
                },
                {
                    'Resource name': 'Test Resource 2',
                    'Default': 0.1,
                    'Unit abbreviation': 'l',
                    'Frequency': 'weekly'
                },
            ],
            'provenance': 'Test',
            'profile': 'Test'
        })

    def tearDown(self):
        """Fixture run after each test."""
        pass

    def test_02_needs(self):
        """Test the interaction with needs."""
        self.assertEqual(
            self.minimum_needs.get_minimum_needs(),
            OrderedDict([
                ['Test Resource 1 [kg]', 100],
                ['Test Resource 2 [l]', 0.1]
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
                ['Test Resource 1 [kg]', 100],
                ['Test Resource 2 [l]', 0.1],
                ['Test Resource 3 [kg]', 10]
            ])
        )
        last_added = self.minimum_needs.get_full_needs()['resources'][-1]
        self.assertEqual(
            cmp(
                last_added,
                {
                    'Resource name': 'Test Resource 3',
                    'Default': 10,
                    'Unit abbreviation': 'kg',
                    'Frequency': 'weekly'
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
            '{"provenance": "TEST FILE WRITE", "profile": "Test Read",'
            '"resources": [{"Default": 1, "Frequency": "weekly", '
            '"Resource name": "Test Resource File", '
            '"Unit abbreviation": "T"}]}')
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
    suite = unittest.makeSuite(MinimumNeedsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
