# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Event Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
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
import difflib
import PyQt4
from qgis.core import QgsFeature
from safe.api import unique_filename, temp_dir
from safe_qgis.utilities_test import getQgisTestApp
from utils import shakemapExtractDir, shakemapZipDir, dataDir
from shake_event import ShakeEvent
# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')
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
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.gridFilePath()
        self.assertEquals(myExpectedPath, myPath)

    def test_eventParser(self):
        """Test eventFilePath works (using cached data)"""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
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
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.mmiDataToDelimitedFile(theForceFlag=True)
        myFile = file(myPath, 'rt')
        myString = myFile.readlines()
        myFile.close()
        self.assertEqual(25922, len(myString))

    def testEventToRaster(self):
        """Check we can convert the shake event to a raster"""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
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
displacedCounts: None
affectedCounts: None
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
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.mmiDataToShapefile(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('shp', 'qml')
        myMessage = '%s not found' % myExpectedQml
        assert os.path.exists(myExpectedQml), myMessage

    def checkFeatureCount(self, thePath, theCount):
        myDataSource = ogr.Open(thePath)
        myBaseName = os.path.splitext(os.path.basename(thePath))[0]
        # do a little query to make sure we got some results...
        mySQL = 'select * from \'%s\' order by MMI asc' % myBaseName
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
        myShakeEvent = ShakeEvent(myShakeId)
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
        myShakeEvent = ShakeEvent(myShakeId)
        # Get teh mem layer
        myCitiesLayer = myShakeEvent.localCitiesMemoryLayer()
        myProvider = myCitiesLayer.dataProvider()

        myFeature = QgsFeature()
        myAttributes = myProvider.attributeIndexes()
        myProvider.select(myAttributes)
        myExpectedFeatureCount = 6
        self.assertEquals(myProvider.featureCount(), myExpectedFeatureCount)
        myStrings = []
        while myProvider.nextFeature(myFeature):
            # fetch map of attributes
            myAttributes = myFeature.attributeMap()
            for (myKey, myValue) in myAttributes.iteritems():
                myStrings.append("%d: %s\n" % (myKey, myValue.toString()))
            myStrings.append('------------------\n')
        LOGGER.debug('Mem table:\n %s' % myStrings)
        myFilePath = unique_filename(prefix='testLocalCities',
                                     suffix='.txt',
                                     dir=temp_dir('test'))
        myFile = file(myFilePath, 'wt')
        myFile.writelines(myStrings)
        myFile.close()

        myFixturePath = os.path.join(dataDir(), 'tests', 'testLocalCities.txt')
        myFile = file(myFixturePath, 'rt')
        myExpectedString = myFile.readlines()
        myFile.close()

        myDiff = difflib.unified_diff(myStrings, myExpectedString)
        myDiffList = list(myDiff)
        myDiffString = ''
        for _, myLine in enumerate(myDiffList):
            myDiffString += myLine

        myMessage = ('Diff is not zero length:\n'
                     'Control file: %s\n'
                     'Test file: %s\n'
                     'Diff:\n%s'
                     % (myFixturePath,
                        myFilePath,
                        myDiffString))
        self.assertEqual(myDiffString, '', myMessage)

    def testCitiesToShape(self):
        """Test that we can retrieve the cities local to the event"""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.citiesToShapefile()
        assert os.path.exists(myPath)

    def testCitiesSearchBoxesToShape(self):
        """Test that we can retrieve the search boxes used to find cities."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.citySearchBoxesToShapefile()
        assert os.path.exists(myPath)

    def testCalculateFatalities(self):
        """Test that we can calculate fatalities."""
        LOGGER.debug(QGISAPP.showSettings())
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myResult, myFatalitiesHtml = myShakeEvent.calculateImpacts()

        myExpectedResult = ('/tmp/inasafe/realtime/shakemaps-extracted'
                           '/20120726022003/impact-nearest.tif')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

        myExpectedResult = ('/tmp/inasafe/realtime/shakemaps-extracted'
                            '/20120726022003/impacts.html')

        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myFatalitiesHtml,
            myExpectedResult)
        assert myFatalitiesHtml == myExpectedResult, myMessage

        myExpectedFatalities = {2: 0.47386375223673427,
                                3: 0.024892573693488258,
                                4: 0.0,
                                5: 0.0,
                                6: 0.0,
                                7: 0.0,
                                8: 0.0,
                                9: 0.0}

        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (
                myShakeEvent.fatalityCounts, myExpectedFatalities)
        assert myShakeEvent.fatalityCounts == myExpectedFatalities, myMessage

    def testBoundsToRect(self):
        """Test that we can calculate the event bounds properly"""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myBounds = myShakeEvent.boundsToRectangle().toString()
        myExpectedResult = ('122.4500000000000028,-2.2100000000000000 : '
                           '126.4500000000000028,1.7900000000000000')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myBounds, myExpectedResult)
        assert myBounds == myExpectedResult, myMessage

    def testRomanize(self):
        """Test we can convert MMI values to float."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)

        myValues = range(2, 10)
        myExpectedResult = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        myResult = []
        for myValue in myValues:
            myResult.append(myShakeEvent.romanize(myValue))
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

    def testMmiColour(self):
        """Test that we can get a colour given an mmi number."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)

        myValues = range(0, 12)
        myExpectedResult = ['#FFFFFF',
                            '#209fff',
                            '#00cfff',
                            '#55ffff',
                            '#aaffff',
                            '#fff000',
                            '#ffa800',
                            '#ff7000',
                            '#ff0000',
                            '#D00',
                            '#800',
                            '#400']
        myResult = []
        for myValue in myValues:
            myResult.append(myShakeEvent.mmiColour(myValue))
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

    def testSortedImpactedCities(self):
        """Test getting impacted cities sorted by mmi then population."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myTable = myShakeEvent.sortedImpactedCities()
        myExpectedResult = [
            {'dir_from': 13.119078636169434, 'dir_to': -166.88092041015625,
             'roman': 'II', 'dist_to': 3.036229133605957, 'mmi-int': 2.0,
             'name': 'Manado', 'mmi': 1.809999942779541, 'id': 207,
             'population': 451893},
            {'dir_from': -61.620426177978516, 'dir_to': 118.37957000732422,
             'roman': 'II', 'dist_to': 2.4977917671203613, 'mmi-int': 2.0,
             'name': 'Gorontalo', 'mmi': 2.25, 'id': 282,
             'population': 144195},
            {'dir_from': -114.04046630859375, 'dir_to': 65.95953369140625,
             'roman': 'II', 'dist_to': 3.3138768672943115, 'mmi-int': 2.0,
             'name': 'Luwuk', 'mmi': 1.5299999713897705, 'id': 215,
             'population': 47778},
            {'dir_from': 16.94407844543457, 'dir_to': -163.05592346191406,
             'roman': 'II', 'dist_to': 2.504295825958252, 'mmi-int': 2.0,
             'name': 'Tondano', 'mmi': 1.909999966621399, 'id': 57,
             'population': 33317},
            {'dir_from': 14.14267635345459, 'dir_to': -165.85733032226562,
             'roman': 'II', 'dist_to': 2.5372657775878906, 'mmi-int': 2.0,
             'name': 'Tomohon', 'mmi': 1.690000057220459, 'id': 58,
             'population': 27624}]
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myTable, myExpectedResult)
        assert myTable == myExpectedResult, myMessage

    def testImpactedCitiesTable(self):
        """Test getting impacted cities table."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myTable, myPath = myShakeEvent.impactedCitiesTable()
        myExpectedResult = 906
        myTable = myTable.toNewlineFreeString()
        myResult = len(myTable)
        myMessage = ('Got:\n%s\nExpected:\n%s\nFor rendered table:\n%s' %
                    (myResult, myExpectedResult, myTable))
        assert myResult == myExpectedResult, myMessage

        myExpectedPath = ('/tmp/inasafe/realtime/shakemaps-extracted/'
                         '20120726022003/affected-cities.html')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myPath, myExpectedPath)
        assert myPath == myExpectedPath, myMessage

    def testFatalitiesTable(self):
        """Test rendering a fatalities table."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myShakeEvent.calculateImpacts()
        myResult = myShakeEvent.impactTable()
        # TODO compare actual content of impact table...
        myExpectedResult = ('/tmp/inasafe/realtime/shakemaps-extracted/'
                           '20120726022003/impacts.html')
        myMessage = ('Got:\n%s\nExpected:\n%s' %
                    (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def testEventInfoDict(self):
        """Test we can get a dictionary of location info nicely."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myResult = myShakeEvent.eventDict()
        myExpectedDict = {'place-name': PyQt4.QtCore.QString(u'n/a'),
                          'depth-name': PyQt4.QtCore.QString(u'Depth'),
                          'fatalities-name': PyQt4.QtCore.QString(
                              u'Estimated fatalities'),
                          'fatalities-count': u'0',  # 44 only after render
                          'elapsed-time': u'',  # empty as it will change
                          'legend-name': 'Population density',
                          'longitude-name': PyQt4.QtCore.QString(u'Longitude'),
                          'located-label': PyQt4.QtCore.QString(u'Located'),
                          'distance-unit': PyQt4.QtCore.QString(u'km'),
                          'bearing-compass': u'n/a',
                          'elapsed-time-name': PyQt4.QtCore.QString(
                              u'Elapsed time since event'),
                          'exposure-table-name': PyQt4.QtCore.QString(
                              u'Estimated number of people exposed to each '
                              u'MMI level'),
                          'longitude-value': u'124\xb027\'0.00"E',
                          'city-table-name': PyQt4.QtCore.QString(
                              u'Places Affected'),
                          'bearing-text': PyQt4.QtCore.QString(u'bearing'),
                          'limitations': PyQt4.QtCore.QString(
                              u'This impact estimation is automatically '
                              u'generated and only takes into account the '
                              u'population and cities affected by different '
                              u'levels of ground shaking. The estimate is '
                              u'based on ground shaking data from BMKG, '
                              u'population density data from asiapop.org, '
                              u'place information from geonames.org and '
                              u'software developed by BNPB. Limitations in '
                              u'the estimates of ground shaking, '
                              u'population  data and place names datasets may'
                              u' result in significant misrepresentation of '
                              u'the on-the-ground situation in the figures '
                              u'shown here. Consequently decisions should not'
                              u' be made solely on the information presented '
                              u'here and should always be verified by ground '
                              u'truthing and other reliable information '
                              u'sources.'),
                          'depth-unit': PyQt4.QtCore.QString(u'km'),
                          'latitude-name': PyQt4.QtCore.QString(u'Latitude'),
                          'mmi': '5.0', 'map-name': PyQt4.QtCore.QString(
                          u'Estimated Earthquake Impact'), 'date': '26-7-2012',
                          'bearing-degrees': '0.00\xb0',
                          'formatted-date-time': '26-Jul-12 02:15:35 ',
                          'distance': '0.00',
                          'direction-relation': PyQt4.QtCore.QString(u'of'),
                          'credits': PyQt4.QtCore.QString(
                              u'Supported by the Australia-Indonesia Facility'
                              u' for Disaster Reduction, '
                              u'Geoscience Australia and the GFDRR.'),
                          'latitude-value': u'0\xb012\'36.00"S',
                          'time': '2:15:35', 'depth-value': '11.0'}
        myResult['elapsed-time'] = u''
        myMessage = ('Got:\n%s\nExpected:\n%s\n' %
             (myResult, myExpectedDict))
        self.maxDiff = None
        self.assertDictEqual(myExpectedDict, myResult, myMessage)

    def testEventInfoString(self):
        """Test we can get a location info string nicely."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myDegreeSymbol = unichr(176)
        myExpectedResult = (
            'M 5.0 26-7-2012 2:15:35 Latitude: 0%s12\'36.00"S Longitude: '
            '124%s27\'0.00"E Depth: 11.0km Located 0.00km n/a of n/a'
            % (myDegreeSymbol, myDegreeSymbol))
        myResult = myShakeEvent.eventInfo()
        myMessage = ('Got:\n%s\nExpected:\n%s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def testBearingToCardinal(self):
        """Test we can convert a bearing to a cardinal direction."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)

        # Ints should work
        myExpectedResult = 'SSE'
        myResult = myShakeEvent.bearingToCardinal(160)
        myMessage = ('Got:\n%s\nExpected:\n%s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

        # Floats should work
        myExpectedResult = 'SW'
        myResult = myShakeEvent.bearingToCardinal(225.4)
        myMessage = ('Got:\n%s\nExpected:\n%s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

        # non numeric data as input should return None
        myExpectedResult = None
        myResult = myShakeEvent.bearingToCardinal('foo')
        myMessage = ('Got:\n%s\nExpected:\n%s\n' %
                     (myResult, myExpectedResult))
        assert myResult == myExpectedResult, myMessage

    def testI18n(self):
        """See if internationalisation is working."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId, theLocale='id')
        myShaking = myShakeEvent.mmiShaking(5)
        myExpectedShaking = 'Sedang'
        self.assertEqual(myExpectedShaking, myShaking)

    def test_extractDateTime(self):
        """Check that we extract date and time correctly."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId, theLocale='en')
        myShakeEvent.extractDateTime('2012-08-07T01:55:12WIB')
        self.assertEqual('01', myShakeEvent.hour)
        self.assertEqual('55', myShakeEvent.minute)
        self.assertEqual('12', myShakeEvent.second)
        myShakeEvent.extractDateTime('2013-02-07T22:22:37WIB')
        self.assertEqual('22', myShakeEvent.hour)
        self.assertEqual('22', myShakeEvent.minute)
        self.assertEqual('37', myShakeEvent.second)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestShakeEvent, 'testLocalCities')
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main()
