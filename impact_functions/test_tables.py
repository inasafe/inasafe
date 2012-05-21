"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Table Tests implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.4.0'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
from tables import Table


class TablesTest(unittest.TestCase):
    """Test the SAFE Table"""

    def setUp(self):
        """Fixture run before all tests"""
        pass

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_simple_table(self):
        """Test simple table creation"""
        table = [
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd'],
                   ['a', 'b', 'c', 'd']
                ]
        expected_result = (
                        '<table class="table table-striped condensed">\n'
                        ' <tr>\n'
                        '  <td>a</td>\n'
                        '  <td>b</td>\n'
                        '  <td>c</td>\n'
                        '  <td>d</td>\n'
                        ' </tr>\n'
                        ' <tr>\n'
                        '  <td>a</td>\n'
                        '  <td>b</td>\n'
                        '  <td>c</td>\n'
                        '  <td>d</td>\n'
                        ' </tr>\n'
                        ' <tr>\n'
                        '  <td>a</td>\n'
                        '  <td>b</td>\n'
                        '  <td>c</td>\n'
                        '  <td>d</td>\n'
                        ' </tr>\n'
                        ' <tr>\n'
                        '  <td>a</td>\n'
                        '  <td>b</td>\n'
                        '  <td>c</td>\n'
                        '  <td>d</td>\n'
                        ' </tr>\n'
                        '</table>\n'
                        )
        actual_result = Table(table)
        message = 'Expected: %s\n\nGot: %s' % (expected_result, actual_result)
        assert expected_result.strip() == str(actual_result).strip(), message

