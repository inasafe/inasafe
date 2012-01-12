'''
Disaster risk assessment tool developed by AusAid - **Impact calculator test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

'''

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from impactcalculator import ImpactCalculator
from riabexceptions import TestNotImplementedException


class ImpactCalculatorTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ImpactCalculator()

    def tearDown(self):
        '''Tear down - destroy the QGIS app'''
        self.app.exitQgis()

    def test_run(self):
        raise TestNotImplementedException()


if __name__ == "__main__":
    unittest.main()
