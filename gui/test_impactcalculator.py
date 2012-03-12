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
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import numpy
import unittest
from gui.impactcalculator import (ImpactCalculator,
                                  getOptimalExtent,
                                  getStyleInfo,
                                  availableFunctions,
                                  getKeywordFromLayer,
                                  getKeywordFromFile)
#from riabexceptions import TestNotImplementedException
from gui.riabexceptions import (InsufficientParametersException,
                                KeywordNotFoundException,
                                StyleInfoNotFoundException)
from storage.core import read_layer
from storage.utilities_test import TESTDATA


class ImpactCalculatorTest(unittest.TestCase):
    """Test the risk in a box plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ImpactCalculator()
        self.vectorPath = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.rasterShakePath = os.path.join(TESTDATA,
                                            'Shakemap_Padang_2009.asc')
        # UTM projected layer

        fn = 'tsunami_max_inundation_depth_BB_utm.asc'
        self.rasterTsunamiBBPath = os.path.join(TESTDATA, fn)
        self.rasterExposureBBPath = os.path.join(TESTDATA,
                                                'tsunami_exposure_BB.shp')

        self.rasterPopulationPath = os.path.join(TESTDATA, 'glp10ag.asc')
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
        myList = availableFunctions()
        assert myList > 1

        # Also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        myKeywords1 = getKeywordFromFile(self.rasterShakePath)
        myKeywords2 = getKeywordFromFile(self.vectorPath)
        myList = [myKeywords1, myKeywords2]
        myList = availableFunctions(myList)
        assert myList > 1

    def test_getKeywordFromLayer(self):
        """Test that we can get keyword data from a riab layer with
        a .keyword metadata file associated with it."""
        myRunner = self.calculator.getRunner()
        myRunner.run()
        myImpactLayer = myRunner.impactLayer()
        myKeyword = getKeywordFromLayer(
                                        myImpactLayer, 'impact_summary')
        msg = 'Keyword request returned an empty string'
        assert(myKeyword is not ''), msg
        # Test we get an exception if keyword is not found
        try:
            myKeyword = getKeywordFromLayer(
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

        myKeyword = getKeywordFromFile(
                                    self.rasterShakePath, 'category')
        msg = 'Keyword request did not return expected value'
        assert myKeyword == 'hazard', msg

        # Test we get an exception if keyword is not found
        try:
            myKeyword = getKeywordFromFile(
                            self.rasterShakePath, 'boguskeyword')
        except KeywordNotFoundException:
            pass  # this is good
        except Exception, e:
            msg = ('Request for bogus keyword raised incorrect exception' +
                    ' type: \n %s') % str(e)
            assert(), msg

        myKeywords = getKeywordFromFile(self.rasterShakePath)
        assert myKeywords == {'category': 'hazard',
                              'subcategory': 'earthquake',
                              'unit': 'MMI'}

        myKeywords = getKeywordFromFile(self.rasterPopulationPath)
        assert myKeywords == {'category': 'exposure',
                              'subcategory': 'population',
                              'datatype': 'density',
                              'title': 'Population Density Estimate (5kmx5km)'}

        myKeywords = getKeywordFromFile(self.vectorPath)
        assert myKeywords == {'category': 'exposure',
                              'datatype': 'itb',
                              'subcategory': 'building'}

        # BB tsunami example (one layer is UTM)
        myKeywords = getKeywordFromFile(self.rasterTsunamiBBPath)
        assert myKeywords == {'category': 'hazard',
                              'subcategory': 'tsunami', 'unit': 'm'}
        myKeywords = getKeywordFromFile(self.rasterExposureBBPath)
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

        myStyleInfo = getStyleInfo(myImpactLayer)
        msg = 'Style inforrequest returned an empty string'
        assert myStyleInfo is not '', msg
        #print myStyleInfo

        # Test we get an exception if style info is not found
        try:
            myStyleInfo = getStyleInfo('boguspath')
        except StyleInfoNotFoundException:
            pass  # This is good
        except Exception, e:
            msg = ('StyleInfo request for bogus file raised incorrect' +
                   ' exception type: \n %s') % str(e)
            raise StyleInfoNotFoundException(msg)

    def test_getOptimalExtent(self):
        """Optimal extent is calculated correctly
        """

        exposure_path = os.path.join(TESTDATA, 'Population_2010.asc')
        hazard_path = os.path.join(TESTDATA,
                                   'Lembang_Earthquake_Scenario.asc')

        # Expected data
        haz_metadata = {'bounding_box': (105.3000035,
                                         -8.3749994999999995,
                                         110.2914705,
                                         -5.5667784999999999),
                        'resolution': (0.0083330000000000001,
                                       0.0083330000000000001)}

        exp_metadata = {'bounding_box': (94.972335000000001,
                                         -11.009721000000001,
                                         141.0140016666665,
                                         6.0736123333332639),
                        'resolution': (0.0083333333333333003,
                                       0.0083333333333333003)}

        # Verify relevant metada is ok
        H = read_layer(hazard_path)
        E = read_layer(exposure_path)

        hazard_bbox = H.get_bounding_box()
        assert numpy.allclose(hazard_bbox, haz_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_bbox = E.get_bounding_box()
        assert numpy.allclose(exposure_bbox, exp_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        hazard_res = H.get_resolution()
        assert numpy.allclose(hazard_res, haz_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_res = E.get_resolution()
        assert numpy.allclose(exposure_res, exp_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        # First, do some examples that produce valid results
        ref_res = [105.3000035, -8.3749995, 110.2914705, -5.5667785]
        view_port = [94.972335, -11.009721, 141.014002, 6.073612]

        bbox = getOptimalExtent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_res, rtol=1.0e-12, atol=1.0e-12)

        bbox = getOptimalExtent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_res, rtol=1.0e-12, atol=1.0e-12)

        view_port = [105.3000035,
                     -8.3749994999999995,
                     110.2914705,
                     -5.5667784999999999]
        bbox = getOptimalExtent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_res,
                              rtol=1.0e-12, atol=1.0e-12)

        # Then one where boxes don't overlap
        view_port = [105.3, -4.3, 110.29, -2.5]
        try:
            getOptimalExtent(hazard_bbox, exposure_bbox, view_port)
        except Exception, e:
            msg = 'Did not find expected error message in %s' % str(e)
            assert 'did not overlap' in str(e), msg
        else:
            msg = ('Non ovelapping bounding boxes should have raised '
                   'an exception')
            raise Exception(msg)

        # Try with wrong input data
        try:
            getOptimalExtent(haz_metadata, exp_metadata, view_port)
        except Exception, e:
            msg = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), msg
        else:
            msg = ('Wrong input data should have raised an exception')
            raise Exception(msg)

        try:
            getOptimalExtent(None, None, view_port)
        except Exception, e:
            msg = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), msg
        else:
            msg = ('Wrong input data should have raised an exception')
            raise Exception(msg)

        try:
            getOptimalExtent('aoeush', 'oeuuoe', view_port)
        except Exception, e:
            msg = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), msg
        else:
            msg = ('Wrong input data should have raised an exception')
            raise Exception(msg)

    def test_issue100(self):
        """Test for issue 100: unhashable type dict"""
        exposure_path = os.path.join(TESTDATA,
                            'OSM_building_polygons_20110905.shp')
        hazard_path = os.path.join(TESTDATA,
                            'Flood_Current_Depth_Jakarta_geographic.asc')
        # Verify relevant metada is ok
        #H = read_layer(hazard_path)
        #E = read_layer(exposure_path)
        self.calculator.setHazardLayer(hazard_path)
        self.calculator.setExposureLayer(exposure_path)
        self.calculator.setFunction('Temporarily Closed')
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

if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactCalculatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
