"""
Disaster risk assessment tool developed by AusAid -
**Impact calculator test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
from impactcalculator import ImpactCalculator
#from riabexceptions import TestNotImplementedException
from riabexceptions import InsufficientParametersException


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
        self.calculator.setFunction('Flood Building Impact Function')

    def tearDown(self):
        """Tear down - destroy the QGIS app"""
        pass

    def test_properties(self):
        """Test if the properties work as expected."""
        msg = 'Vector property incorrect.'
        assert(self.calculator.getExposureLayer() ==
               self.vectorPath), msg
        msg = 'Raster property incorrect.'
        assert(self.calculator.getHazardLayer() ==
               self.rasterPath), msg
        msg = 'Function property incorrect.'
        assert(self.calculator.getFunction() ==
               'Flood Building Impact Function'), msg

    def test_run(self):
        """Test that run works as expected."""
        try:
            self.calculator.run()
        except:
            msg = 'Calculator run failed.'
            assert(), msg

    def test_runWithNoParameters(self):
        """Test that run raises an error properly
           when no parameters are defined."""
        try:
            self.calculator.setExposureLayer(None)
            self.calculator.setHazardLayer(None)
            self.calculator.run()
        except InsufficientParametersException:
            return  # expected outcome
        except:
            msg = 'Missing parameters not raised as error.'
            assert(), msg
        msg = 'Expected an error, none encountered.'
        assert(), msg

    def test_availableFunctions(self):
        """Test that we can get the available functions from
        the impactcalculator."""
        myList = self.calculator.availableFunctions()
        print myList
        assert(myList > 1)

if __name__ == "__main__":
    unittest.main()
