'''
Disaster risk assessment tool developed by AusAid -
**Impact calculator test suite.**

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

import os
import unittest
from impactcalculator import ImpactCalculator
#from riabexceptions import TestNotImplementedException


class ImpactCalculatorTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ImpactCalculator()
        myRoot = os.path.dirname(__file__)
        self.vectorPath = os.path.join(myRoot, 'testdata',
                                   'Jakarta_sekolah.shp')
        self.rasterPath = os.path.join(myRoot, 'testdata',
                                    'current_flood_depth_jakarta.asc')
        self.calculator.setHazardLayer(self.rasterPath)
        self.calculator.setExposureLayer(self.vectorPath)

    def tearDown(self):
        '''Tear down - destroy the QGIS app'''
        pass

    def test_properties(self):
        '''Test if the properties work as expected.'''
        msg = 'Vector property incorrect.'
        assert(self.calculator.getExposureLayer() ==
               self.vectorPath), msg
        msg = 'Raster property incorrect.'
        assert(self.calculator.getHazardLayer() ==
               self.rasterPath), msg

    def test_run(self):
        '''Test that run works.'''
        self.calculator.run()


if __name__ == "__main__":
    unittest.main()
