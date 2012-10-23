"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact calculator test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

import unittest
from safe_qgis.impact_calculator import ImpactCalculator
from safe_qgis.exceptions import (InsufficientParametersException,
                           KeywordNotFoundException,
                           StyleInfoNotFoundException)

from safe_qgis.safe_interface import (readKeywordsFromLayer, getStyleInfo)

from safe.common.testing import HAZDATA, EXPDATA, TESTDATA

# Retired impact function for characterisation
# (need import here if test is run independently)
# pylint: disable=W0611
from safe.engine.impact_functions_for_testing import BNPB_earthquake_guidelines
# pylint: enable=W0611


class ImpactCalculatorTest(unittest.TestCase):
    """Test the InaSAFE plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ImpactCalculator()
        self.vectorPath = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.rasterShakePath = os.path.join(HAZDATA,
                                            'Shakemap_Padang_2009.asc')
        # UTM projected layer

        fn = 'tsunami_max_inundation_depth_BB_utm.asc'
        self.rasterTsunamiBBPath = os.path.join(TESTDATA, fn)
        self.rasterExposureBBPath = os.path.join(TESTDATA,
                                                'tsunami_building_'
                                                 'exposure.shp')

        self.rasterPopulationPath = os.path.join(EXPDATA, 'glp10ag.asc')
        self.calculator.setHazardLayer(self.rasterShakePath)
        self.calculator.setExposureLayer(self.vectorPath)
        self.calculator.setFunction('Earthquake Guidelines Function')

    def tearDown(self):
        """Tear down - destroy the QGIS app"""
        pass

    def test_properties(self):
        """Test if the properties work as expected."""

        myMessage = 'Vector property incorrect.'
        assert (self.calculator.exposureLayer() ==
                self.vectorPath), myMessage

        myMessage = 'Raster property incorrect.'
        assert (self.calculator.hazardLayer() ==
                self.rasterShakePath), myMessage

        myMessage = 'Function property incorrect.'
        assert (self.calculator.function() ==
                'Earthquake Guidelines Function'), myMessage

    def test_run(self):
        """Test that run works as expected in non threading mode"""
        try:
            myRunner = self.calculator.getRunner()
            # run non threaded
            myRunner.run()
            myMessage = myRunner.result()
            myImpactLayer = myRunner.impactLayer()
            myFilename = myImpactLayer.get_filename()
            assert(myFilename and not myFilename == '')
            assert(myMessage and not myMessage == '')
        except Exception, e:  # pylint: disable=W0703
            myMessage = 'Calculator run failed. %s' % str(e)
            assert(), myMessage

    def test_thread(self):
        """Test that starting it in a thread works as expected."""
        try:
            myRunner = self.calculator.getRunner()
            myRunner.start()
            # wait until the thread is done
            myRunner.join()
            myMessage = myRunner.result()
            myImpactLayer = myRunner.impactLayer()
            myFilename = myImpactLayer.get_filename()
            assert(myFilename and not myFilename == '')
            assert(myMessage and not myMessage == '')
        except Exception, e:  # pylint: disable=W0703
            myMessage = 'Calculator run failed:\n' + str(e)
            assert(), myMessage

    def test_startWithNoParameters(self):
        """Test that run raises an error properly when no parameters defined.
        """
        try:
            self.calculator.setExposureLayer(None)
            self.calculator.setHazardLayer(None)
            # Next line should raise an error
            myRunner = self.calculator.getRunner()
            myRunner.start()
        except RuntimeError, e:
            myMessage = 'Runtime error encountered: %s' % str(e)
            assert(), myMessage
        except InsufficientParametersException:
            return  # expected outcome
        except:
            myMessage = 'Missing parameters not raised as error.'
            assert(), myMessage
        myMessage = 'Expected an error, none encountered.'
        assert(), myMessage

    def test_getKeywordFromImpactLayer(self):
        """Check that we can get keywords from a created impact layer."""
        myRunner = self.calculator.getRunner()
        myRunner.run()
        myImpactLayer = myRunner.impactLayer()
        myKeyword = readKeywordsFromLayer(myImpactLayer,
                                          'impact_summary')
        myMessage = 'Keyword request returned an empty string'
        assert(myKeyword is not ''), myMessage
        # Test we get an exception if keyword is not found
        try:
            myKeyword = readKeywordsFromLayer(
                            myImpactLayer, 'boguskeyword')
        except KeywordNotFoundException:
            pass  # this is good
        except Exception, e:
            myMessage = ('Request for bogus keyword raised incorrect '
                         'exception type: \n %s') % str(e)
            assert(), myMessage

    def test_issue100(self):
        """Test for issue 100: unhashable type dict"""
        exposure_path = os.path.join(TESTDATA,
                            'OSM_building_polygons_20110905.shp')
        hazard_path = os.path.join(HAZDATA,
                            'Flood_Current_Depth_Jakarta_geographic.asc')
        # Verify relevant metada is ok
        #H = readSafeLayer(hazard_path)
        #E = readSafeLayer(exposure_path)
        self.calculator.setHazardLayer(hazard_path)
        self.calculator.setExposureLayer(exposure_path)
        self.calculator.setFunction('Flood Building Impact Function')
        try:
            myRunner = self.calculator.getRunner()
            # Run non threaded
            myRunner.run()
            myMessage = myRunner.result()
            myImpactLayer = myRunner.impactLayer()
            myFilename = myImpactLayer.get_filename()
            assert(myFilename and not myFilename == '')
            assert(myMessage and not myMessage == '')
        except Exception, e:  # pylint: disable=W0703
            myMessage = 'Calculator run failed. %s' % str(e)
            assert(), myMessage

    def test_getStyleInfo(self):
        """Test that we can get styleInfo data from a vector's keyword file
        """

        myRunner = self.calculator.getRunner()
        myRunner.start()
        myRunner.join()
        myImpactLayer = myRunner.impactLayer()

        myMessage = ('Incorrect type returned from '
               'myRunner.impactlayer(). Expected an impactlayer'
               'but received a %s' % type(myImpactLayer))
        assert hasattr(myImpactLayer, 'get_style_info'), myMessage

        myStyleInfo = getStyleInfo(myImpactLayer)
        myMessage = 'Style info request returned an empty string'
        assert myStyleInfo is not '', myMessage
        #print myStyleInfo

        # Test we get an exception if style info is not found
        try:
            myStyleInfo = getStyleInfo('boguspath')
        except StyleInfoNotFoundException:
            pass  # This is good
        except Exception, e:
            myMessage = ('StyleInfo request for bogus file raised incorrect' +
                   ' exception type: \n %s') % str(e)
            raise StyleInfoNotFoundException(myMessage)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactCalculatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
