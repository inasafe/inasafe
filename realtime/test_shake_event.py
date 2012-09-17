"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Event Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from qgis.core import QgsFeature

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '2/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import ogr
import os
import shutil
import unittest
import logging
from safe_qgis.utilities_test import getQgisTestApp
from utils import shakemapExtractDir, shakemapZipDir
from shake_data import ShakeData
from shake_event import ShakeEvent
# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE-Realtime')
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""

    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir"""
        myOutFile = '20120726022003.out.zip'
        myInpFile = '20120726022003.inp.zip'
        myOutPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'fixtures',
                                                 myOutFile))
        myInpPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'fixtures',
                                                 myInpFile))
        shutil.copyfile(myOutPath, os.path.join(shakemapZipDir(), myOutFile))
        shutil.copyfile(myInpPath, os.path.join(shakemapZipDir(), myInpFile))

        #TODO Downloaded data should be removed before each test

    def test_gridXmlFilePath(self):
        """Test eventFilePath works(using cached data)"""
        myShakeId = '20120726022003'
        myExpectedPath = os.path.join(shakemapExtractDir(),
                                      myShakeId,
                                      'grid.xml')
        myShakeData = ShakeData(myShakeId)
        myShakeData.extract()
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.gridFilePath()
        self.assertEquals(myExpectedPath, myPath)

    def test_eventParser(self):
        """Test eventFilePath works (using cached data)"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        self.assertEquals(26, myShakeEvent.day)
        self.assertEquals(7, myShakeEvent.month)
        self.assertEquals(2012, myShakeEvent.year)
        self.assertEquals(2, myShakeEvent.hour)
        self.assertEquals(15, myShakeEvent.minute)
        self.assertEquals(35, myShakeEvent.second)
        self.assertEquals('WIB', myShakeEvent.timeZone)
        self.assertEquals(124.45, myShakeEvent.longitude)
        self.assertEquals(-0.21, myShakeEvent.latitude)
        self.assertEquals(11.0, myShakeEvent.depth)
        self.assertEquals('Southern Molucca Sea', myShakeEvent.location)
        self.assertEquals(122.45, myShakeEvent.xMinimum)
        self.assertEquals(126.45, myShakeEvent.xMaximum)
        self.assertEquals(-2.21, myShakeEvent.yMinimum)
        self.assertEquals(1.79, myShakeEvent.yMaximum)

        myGridXmlData = myShakeEvent.mmiData
        self.assertEquals(25921, len(myGridXmlData))

        myDelimitedString = myShakeEvent.mmiDataToDelimitedText()
        self.assertEqual(578234, len(myDelimitedString))

    def test_eventGridToCsv(self):
        """Test grid data can be written to csv"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.mmiDataToDelimitedFile(theForceFlag=True)
        myFile = file(myPath, 'rt')
        myString = myFile.readlines()
        myFile.close()
        self.assertEqual(25922, len(myString))

    def testEventToRaster(self):
        """Check we can convert the shake event to a raster"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myExpectedState = """latitude: -0.21
longitude: 124.45
eventId: 20120726022003
magnitude: 5.0
depth: 11.0
description: None
location: Southern Molucca Sea
day: 26
month: 7
year: 2012
time: None
timeZone: WIB
xMinimum: 122.45
xMaximum: 126.45
yMinimum: -2.21
yMaximum: 1.79
rows: 161.0
columns: 161.0
mmiData: Populated
populationRasterPath: None
impactFile: None
impactKeywordsFile: None
fatalityCounts: None
extentWithCities: Not set
zoomFactor: 1.25
searchBoxes: None
"""
        myState = str(myShakeEvent)
        myMessage = (('Expected:\n----------------\n%s'
                     '\n\nGot\n------------------\n%s\n') %
                     (myExpectedState, myState))
        assert myState == myExpectedState, myMessage
        myPath = myShakeEvent.mmiDataToRaster(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('tif', 'qml')
        assert os.path.exists(myExpectedQml)
        myExpectedKeywords = myPath.replace('tif', 'keywords')
        assert os.path.exists(myExpectedKeywords)

    def testEventToShapefile(self):
        """Check we can convert the shake event to a raster"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.mmiDataToShapefile(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('shp', 'qml')
        myMessage = '%s not found' % myExpectedQml
        assert os.path.exists(myExpectedQml), myMessage

    def checkFeatureCount(self, thePath, theCount):
        myDataSource = ogr.Open(thePath)
        myBasename = os.path.splitext(os.path.basename(thePath))[0]
        # do a little query to make sure we got some results...
        mySQL = 'select * from \'%s\' order by MMI asc' % myBasename
        #print mySQL
        myLayer = myDataSource.ExecuteSQL(mySQL)
        myCount = myLayer.GetFeatureCount()
        myFlag = myCount == theCount
        myMessage = ''
        if not myFlag:
            myMessage = 'Expected %s features, got %s' % (theCount, myCount)
        myDataSource.ReleaseResultSet(myLayer)
        myDataSource.Destroy()
        return myFlag, myMessage

    def testEventToContours(self):
        """Check we can extract contours from the event"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.mmiDataToContours(theForceFlag=True,
                                                theAlgorithm='invdist')
        assert self.checkFeatureCount(myPath, 16)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('shp', 'qml')
        myMessage = '%s not found' % myExpectedQml
        assert os.path.exists(myExpectedQml), myMessage

        myPath = myShakeEvent.mmiDataToContours(theForceFlag=True,
                                                theAlgorithm='nearest')
        assert self.checkFeatureCount(myPath, 132)
        myPath = myShakeEvent.mmiDataToContours(theForceFlag=True,
                                                theAlgorithm='average')
        assert self.checkFeatureCount(myPath, 132)




    def testLocalCities(self):
        """Test that we can retrieve the cities local to the event"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        # Get teh mem layer
        myCitiesLayer = myShakeEvent.localCitiesMemoryLayer()
        myProvider = myCitiesLayer.dataProvider()

        myFeature = QgsFeature()
        myAttributes = myProvider.attributeIndexes()
        myProvider.select(myAttributes)
        myExpectedFeatureCount = 7
        self.assertEquals(myProvider.featureCount(), myExpectedFeatureCount)
        myString = ''
        while myProvider.nextFeature(myFeature):
            # fetch map of attributes
            myAttributes = myFeature.attributeMap()
            for (myKey, myValue) in myAttributes.iteritems():
                myString += ("%d: %s\n" % (myKey, myValue.toString()))
            myString += '------------------\n'
        LOGGER.debug('Mem table:\n %s' % myString)
        myExpectedLength = 874
        myLength = len(myString)
        myMessage = 'Expected: %s Got %s' % (myExpectedLength, myLength)
        self.assertEquals(myExpectedLength, myLength, myMessage)

    def testCitiesToShape(self):
        """Test that we can retrieve the cities local to the event"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.citiesToShapefile()
        assert os.path.exists(myPath)

    def testCitiesSearchBoxesToShape(self):
        """Test that we can retrieve the search boxes used to find cities."""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.citySearchBoxesToShapefile()
        assert os.path.exists(myPath)

    def testCalculateFatalities(self):
        """Test that we can calculate fatalities."""
        LOGGER.debug(QGISAPP.showSettings())
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myResult = myShakeEvent.calculateFatalities()
        myExpectedResult = ('/tmp/inasafe/realtime/shakemaps-extracted'
                           '/20120726022003/impact-nearest.tif')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

    def testBoundsToRect(self):
        """Test that we can calculate the event bounds properly"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myBounds = myShakeEvent.boundsToRectangle().toString()
        myExpectedResult = ('122.4500000000000028,-2.2100000000000000 : '
                           '126.4500000000000028,1.7900000000000000')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myBounds, myExpectedResult)
        assert myBounds == myExpectedResult, myMessage

    def testRomanize(self):
        """Test we can convert MMI values to float."""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()

        myValues = range(1,9)
        myExpectedResult = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        myResult = []
        for myValue in myValues:
            myResult.append(myShakeEvent.romanize(myValue))
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

    def testMmiColour(self):
        """Test that we can get a colour given an mmi number."""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()

        myValues = range(0,12)
        myExpectedResult = ['#FFFFFF', '#BFCCFF', '#99F', '#8FF', '#7df894',
         '#FF0', '#FD0', '#ff9100', '#F00', '#D00', '#800',
         '#400']
        myResult = []
        for myValue in myValues:
            myResult.append(myShakeEvent.mmiColour(myValue))
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

    def testSortedImpactedCities(self):
        """Test getting impacted cities sorted by mmi then population."""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myTable = myShakeEvent.sortedImpactedCities()
        myExpectedResult = [
            {'roman': 'III', 'mmi': 1.909999966621399,
             'name': 'Tondano', 'population': 33317},
            {'roman': 'III', 'mmi': 1.809999942779541,
             'name': 'Manado', 'population': 451893},
            {'roman': 'III', 'mmi': 1.75,
             'name': 'Provinsi Sulawesi Utara', 'population': 2146600},
            {'roman': 'III', 'mmi': 1.690000057220459,
             'name': 'Tomohon', 'population': 27624},
            {'roman': 'III', 'mmi': 1.5299999713897705,
             'name': 'Luwuk', 'population': 47778}]
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myTable, myExpectedResult)
        assert myTable == myExpectedResult, myMessage

    def testImpactedCitiesTable(self):
        """Test getting impacted cities table."""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myTable, myPath = myShakeEvent.impactedCitiesTable()
        myExpectedResult = 938
        myTable = myTable.toNewlineFreeString()
        myResult = len(myTable)
        myMessage = ('Got:\n%s\nExpected:\n%s\nFor rendered table:\n%s' %
                    (myTable, myExpectedResult, myResult))
        assert myTable == myExpectedResult, myMessage

        myExpectedPath = ''
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myPath, myExpectedPath)
        assert myPath == myExpectedPath, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(TestShakeEvent, 'testLocalCities')
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main()
