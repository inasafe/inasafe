# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Test class for version.py.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
__author__ = 'ismail@kartoza.com'
__version__ = '2.2.0'
__revision__ = '$Format:%H$'
__date__ = '11/13/14'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import unittest
import sys
from safe.common.version import get_version, current_git_hash


class TestVersion(unittest.TestCase):
    def test_get_version(self):
        """Test for get_version."""
        version_tuple = ('2', '2', '0', 'alpha', '0')
        version = get_version(version_tuple)
        if 'win32' in sys.platform or 'darwin' in sys.platform:
            expected_version = '2.2.0.dev-master'
            message = 'It should be %s but got %s' % (
                expected_version, version)
            self.assertEqual(expected_version, version, message)
        else:
            expected_version = '2.2.0.dev-ABCDEFG'
            message = 'It should be %s but got %s' % (
                expected_version[:9], version[:9])
            self.assertEqual(expected_version[:9], version[:9], message)
            message = 'Expected version that has length %d, got %d' % (
                len(expected_version), len(version))
            self.assertEqual(len(expected_version), len(version), message)

        # Version tuple doesn't have length == 5
        version_tuple = ('2', '2', '0', 'alpha')
        self.assertRaises(RuntimeError, get_version, version_tuple)

        # Version tuple item 4th is not alpha, beta, rc, final
        version_tuple = ('2', '2', '0', 'avocado', '0')
        self.assertRaises(RuntimeError, get_version, version_tuple)

        # Final version
        version_tuple = ('2', '2', '0', 'final', '0')
        version = get_version(version_tuple)
        self.assertEqual(version, '2.2.0', 'The version should be 2.2.0')

    def test_get_current_hash(self):
        """Test for get_current_hash."""
        git_hash = current_git_hash()
        if sys.platform in ['win32', 'darwin']:
            # On windows we get 9 chars of the git hash back
            # On MacOS also (IS - 27 Apr 2017)
            self.assertEqual(len(git_hash), 9)
        else:
            self.assertEqual(len(git_hash), 7)

if __name__ == '__main__':
    unittest.main()
