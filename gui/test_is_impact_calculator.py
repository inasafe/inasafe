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
__version__ = '0.3.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import tempfile
import unittest
from is_impact_calculator import (ISImpactCalculator,
                                  getHashForDatasource,
                                  writeKeywordsForUri,
                                  readKeywordFromUri,
                                  deleteKeywordsForUri)
#from inasafeexceptions import TestNotImplementedException
from is_exceptions import (InsufficientParametersException,
                                HashNotFoundException)
from is_utilities import getTempDir

from storage.utilities_test import TESTDATA
#Dont change this, not even formatting, you will break tests!
URI = """'dbname=\'osm\' host=localhost port=5432 user=\'foo\'
         password=\'bar\' sslmode=disable key=\'id\' srid=4326
         type=MULTIPOLYGON table="valuations_parcel" (geometry) sql='"""


class ImpactCalculatorTest(unittest.TestCase):
    """Test the InaSAFE plugin stub"""

    def setUp(self):
        """Create shared resources that all tests can use"""
        self.calculator = ISImpactCalculator()
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

        myMessage = 'Vector property incorrect.'
        assert (self.calculator.getExposureLayer() ==
                self.vectorPath), myMessage

        myMessage = 'Raster property incorrect.'
        assert (self.calculator.getHazardLayer() ==
                self.rasterShakePath), myMessage

        myMessage = 'Function property incorrect.'
        assert (self.calculator.getFunction() ==
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
        except Exception, e:
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
        except Exception, e:
            myMessage = 'Calculator run failed:\n' + str(e)
            assert(), myMessage

    def test_startWithNoParameters(self):
        """Test that run raises an error properly when no parameters defined.
        """
        try:
            self.calculator.setExposureLayer(None)
            self.calculator.setHazardLayer(None)
            #next line should raise an error
            myRunner = self.calculator.getRunner()
            myRunner.start()
        except InsufficientParametersException:
            return  # expected outcome
        except:
            myMessage = 'Missing parameters not raised as error.'
            assert(), myMessage
        myMessage = 'Expected an error, none encountered.'
        assert(), myMessage

    def test_getHashForDatasource(self):
        """Test we can reliably get a hash for a uri"""
        myHash = getHashForDatasource(URI)
        myExpectedHash = '7cc153e1b119ca54a91ddb98a56ea95e'
        myMessage = "Got: %s\nExpected: %s" % (myHash, myExpectedHash)
        assert myHash == myExpectedHash, myMessage

    def test_writeReadKeywordFromUri(self):
        """Test we can set and get keywords for a non local datasource"""
        myHandle, myFilename = tempfile.mkstemp('.db', 'keywords_',
                                            getTempDir())

        # Ensure the file is deleted before we try to write to it
        # fixes windows specific issue where you get a message like this
        # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
        # This is because mkstemp creates the file handle and leaves
        # the file open.
        os.close(myHandle)
        os.remove(myFilename)
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'itb',
                              'subcategory': 'building'}
        # SQL insert test
        # On first write schema is empty and there is no matching hash
        writeKeywordsForUri(URI, myExpectedKeywords, myFilename)
        # SQL Update test
        # On second write schema is populated and we update matching hash
        myExpectedKeywords = {'category': 'exposure',
                              'datatype': 'OSM',  # <--note the change here!
                              'subcategory': 'building'}
        writeKeywordsForUri(URI, myExpectedKeywords, myFilename)
        # Test getting all keywords
        myKeywords = readKeywordFromUri(URI, theDatabasePath=myFilename)
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeywords, myExpectedKeywords, myFilename)
        assert myKeywords == myExpectedKeywords, myMessage
        # Test getting just a single keyword
        myKeyword = readKeywordFromUri(URI, 'datatype',
                                        theDatabasePath=myFilename)
        myExpectedKeyword = 'OSM'
        myMessage = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    myKeyword, myExpectedKeyword, myFilename)
        assert myKeyword == myExpectedKeyword, myMessage
        # Test deleting keywords actually does delete
        deleteKeywordsForUri(URI, myFilename)
        try:
            myKeyword = readKeywordFromUri(URI, 'datatype',
                                        theDatabasePath=myFilename)
            #if the above didnt cause an exception then bad
            myMessage = 'Expected a HashNotFoundException to be raised'
            assert myMessage
        except HashNotFoundException:
            #we expect this outcome so good!
            pass


if __name__ == '__main__':
    suite = unittest.makeSuite(ImpactCalculatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
