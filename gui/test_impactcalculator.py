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
from gui.impactcalculator import ImpactCalculator
#from riabexceptions import TestNotImplementedException
from gui.riabexceptions import (InsufficientParametersException,
                                KeywordNotFoundException,
                                StyleInfoNotFoundException)


class ImpactCalculatorTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ImpactCalculator()
        myRoot = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        self.vectorPath = os.path.join(myRoot, 'riab_test_data',
                                       'Padang_WGS84.shp')
        self.rasterShakePath = os.path.join(myRoot, 'riab_test_data',
                                       'Shakemap_Padang_2009.asc')
        # UTM projected layer
        self.rasterTsunamiBBPath = os.path.join(myRoot, 'riab_test_data',
                                'tsunami_max_inundation_depth_BB_utm.asc')
        self.rasterExposureBBPath = os.path.join(myRoot, 'riab_test_data',
                                                'tsunami_exposure_BB.shp')

        self.rasterPopulationPath = os.path.join(myRoot, 'riab_test_data',
                                                 'glp10ag.asc')
        self.calculator.setHazardLayer(self.rasterShakePath)
        self.calculator.setExposureLayer(self.vectorPath)
        self.calculator.setFunction('Earthquake Guidelines Function')

    def tearDown(self):
        """Tear down - destroy the QGIS app"""
        pass

    def test_properties(self):
        """Test if the properties work as expected."""

        msg = 'Vector property incorrect.'
        assert (self.calculator.getExposureLayer() ==
                self.vectorPath), msg

        msg = 'Raster property incorrect.'
        assert (self.calculator.getHazardLayer() ==
                self.rasterShakePath), msg

        msg = 'Function property incorrect.'
        assert (self.calculator.getFunction() ==
                'Earthquake Guidelines Function'), msg

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
        except Exception, e:
            msg = 'Calculator run failed. %s' % str(e)
            assert(), msg

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
        except Exception, e:
            msg = 'Calculator run failed:\n' + str(e)
            assert(), msg

    def test_startWithNoParameters(self):
        """Test that run raises an error properly
           when no parameters are defined."""
        try:
            self.calculator.setExposureLayer(None)
            self.calculator.setHazardLayer(None)
            #next line should raise an error
            myRunner = self.calculator.getRunner()
            myRunner.start()
        except InsufficientParametersException:
            return  # expected outcome
        except:
            msg = 'Missing parameters not raised as error.'
            assert(), msg
        msg = 'Expected an error, none encountered.'
        assert(), msg

    def test_availableFunctions(self):
        """Check we can get the available functions from the impactcalculator.
        """
        myList = self.calculator.availableFunctions()
        assert myList > 1
        # also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        myKeywords1 = self.calculator.getKeywordFromFile(self.rasterShakePath)
        myKeywords2 = self.calculator.getKeywordFromFile(self.vectorPath)
        myList = [myKeywords1, myKeywords2]
        myList = self.calculator.availableFunctions(myList)
        assert myList > 1

    def test_getKeywordFromLayer(self):
        """Test that we can get keyword data from a riab layer with
        a .keyword metadata file associated with it."""
        myRunner = self.calculator.getRunner()
        myRunner.start()
        myRunner.join()
        myImpactLayer = myRunner.impactLayer()
        myKeyword = self.calculator.getKeywordFromLayer(
                                        myImpactLayer, 'caption')
        msg = 'Keyword request returned an empty string'
        assert(myKeyword is not ''), msg
        # Test we get an exception if keyword is not found
        try:
            myKeyword = self.calculator.getKeywordFromLayer(
                            myImpactLayer, 'boguskeyword')
        except KeywordNotFoundException:
            pass  # this is good
        except Exception, e:
            msg = ('Request for bogus keyword raised incorrect exception' +
                    ' type: \n %s') % str(e)
            assert(), msg

    def test_getKeywordFromFile(self):
        """Test that we can get keyword data from a file with
        a .keyword metadata file associated with it."""

        myKeyword = self.calculator.getKeywordFromFile(
                                    self.rasterShakePath, 'category')
        msg = 'Keyword request did not return expected value'
        assert myKeyword == 'hazard', msg

        # Test we get an exception if keyword is not found
        try:
            myKeyword = self.calculator.getKeywordFromFile(
                            self.rasterShakePath, 'boguskeyword')
        except KeywordNotFoundException:
            pass  # this is good
        except Exception, e:
            msg = ('Request for bogus keyword raised incorrect exception' +
                    ' type: \n %s') % str(e)
            assert(), msg

        myKeywords = self.calculator.getKeywordFromFile(self.rasterShakePath)
        assert myKeywords == {'category': 'hazard',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}

        myKeywords = self.calculator.getKeywordFromFile(
            self.rasterPopulationPath)
        assert myKeywords == {'category': 'exposure', 'density': 'yes',
                              'subcategory': 'population',
                              'title': 'Population Density Estimate (5kmx5km)'}

        myKeywords = self.calculator.getKeywordFromFile(self.vectorPath)
        assert myKeywords == {'category': 'exposure', 'datatype': 'itb',
                              'subcategory': 'building'}

        # BB tsunami example (one layer is UTM)
        myKeywords = self.calculator.getKeywordFromFile(
            self.rasterTsunamiBBPath)
        assert myKeywords == {'category': 'hazard',
                              'subcategory': 'tsunami', 'unit': 'm'}
        myKeywords = self.calculator.getKeywordFromFile(
            self.rasterExposureBBPath)
        print myKeywords == {'category': 'exposure',
                             'subcategory': 'building'}

    def test_getStyleInfo(self):
        """Test that we can get styleInfo data from a vector
        file with a .keyword metadata file associated with it."""

        myRunner = self.calculator.getRunner()
        myRunner.start()
        myRunner.join()
        myImpactLayer = myRunner.impactLayer()

        msg = ('Incorrect type returned from '
               'myRunner.impactlayer(). Expected an impactlayer'
               'but received a %s' % type(myImpactLayer))
        assert hasattr(myImpactLayer, 'get_style_info'), msg

        myStyleInfo = self.calculator.getStyleInfo(myImpactLayer)
        msg = 'Style inforrequest returned an empty string'
        assert myStyleInfo is not '', msg
        #print myStyleInfo

        # Test we get an exception if style info is not found
        try:
            myStyleInfo = self.calculator.getStyleInfo('boguspath')
        except StyleInfoNotFoundException:
            pass  # This is good
        except Exception, e:
            msg = ('StyleInfo request for bogus file raised incorrect' +
                   ' exception type: \n %s') % str(e)
            raise StyleInfoNotFoundException(msg)

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactCalculatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
