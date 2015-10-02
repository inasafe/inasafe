# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Christian Christelis <christian@kartoza.com>'

__date__ = '02/04/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_reports.report_mixin_base import ReportMixin


# noinspection PyArgumentList
class ReportMixinTest(unittest.TestCase):
    """Test the ReportMixin.

    .. versionadded:: 3.1
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests"""
        self.mixin = ReportMixin()

    def tearDown(self):
        """Run after each test."""
        del self.mixin

    def test_0001_interface(self):
        """Test all interface methods give default blanks."""
        blank_table = ''
        self.assertEqual(self.mixin.html_report(), blank_table)

if __name__ == '__main__':
    suite = unittest.makeSuite(ReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
