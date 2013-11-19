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

import os
import shutil
import unittest
import logging
import difflib

import ogr
import PyQt4

# pylint: disable=E0611
# pylint: disable=W0611
from qgis.core import QgsFeatureRequest
# pylint: enable=E0611
# pylint: enable=W0611
from safe.api import unique_filename, temp_dir
from safe_qgis.utilities.utilities_for_testing import get_qgis_app
from realtime.utils import shakemapExtractDir, shakemapZipDir, dataDir
from realtime.shake_event import ShakeEvent
# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""

    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir"""
        myOutFile = '20120726022003.out.zip'
        myInpFile = '20120726022003.inp.zip'
        myOutPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '../fixtures',
                                                 myOutFile))
        myInpPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 '../fixtures',
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
time_zone: WIB
x_minimum: 122.45
x_maximum: 126.45
y_minimum: -2.21
y_maximum: 1.79
rows: 161.0
columns: 161.0
mmi_data: Populated
populationRasterPath: None
impact_file: None
impact_keywords_file: None
fatality_counts: None
displaced_counts: None
affected_counts: None
extent_with_cities: Not set
zoom_factor: 1.25
search_boxes: None
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

        myExpectedFeatureCount = 6
        self.assertEquals(myProvider.featureCount(), myExpectedFeatureCount)
        myStrings = []
        myRequest = QgsFeatureRequest()
        for myFeature in myCitiesLayer.getFeatures(myRequest):
            # fetch map of attributes
            myAttributes = myCitiesLayer.dataProvider().attributeIndexes()
            for myKey in myAttributes:
                myStrings.append("%d: %s\n" % (
                    myKey, myFeature[myKey].toString()))
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

        myDiff = difflib.unified_diff(myExpectedString, myStrings)
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
        LOGGER.debug(QGIS_APP.showSettings())
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myResult, myFatalitiesHtml = myShakeEvent.calculateImpacts()

        myExpectedResult = (
            '/tmp/inasafe/realtime/shakemaps-extracted'
            '/20120726022003/impact-nearest.tif')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedResult)
        assert myResult == myExpectedResult, myMessage

        myExpectedResult = (
            '/tmp/inasafe/realtime/shakemaps-extracted'
            '/20120726022003/impacts.html')

        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (
            myFatalitiesHtml,
            myExpectedResult)
        assert myFatalitiesHtml == myExpectedResult, myMessage

        myExpectedFatalities = {2: 0.0,  # rounded from 0.47386375223673427,
                                3: 0.0,  # rounded from 0.024892573693488258,
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
        myExpectedResult = (
            '122.4500000000000028,-2.2100000000000000 : '
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

    def testSortedImpactedCities(self):
        """Test getting impacted cities sorted by mmi then population."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myTable = myShakeEvent.sortedImpactedCities()

        myFilePath = unique_filename(
            prefix='testSortedImpactedCities',
            suffix='.txt',
            dir=temp_dir('test'))
        myFile = file(myFilePath, 'wt')
        myFile.writelines(str(myTable))
        myFile.close()
        myTable = str(myTable).replace(', \'', ',\n\'')
        myTable += '\n'

        myFixturePath = os.path.join(
            dataDir(), 'tests', 'testSortedImpactedCities.txt')
        myFile = file(myFixturePath, 'rt')
        myExpectedString = myFile.read()
        myFile.close()
        myExpectedString = myExpectedString.replace(', \'', ',\n\'')

        self.maxDiff = None
        self.assertEqual(myExpectedString, myTable)

    def testImpactedCitiesTable(self):
        """Test getting impacted cities table."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myTable, myPath = myShakeEvent.impacted_cities_table()
        myExpectedStrings = [
            '<td>Tondano</td><td>33</td><td>I</td>',
            '<td>Luwuk</td><td>47</td><td>I</td>',
            '<td>Bitung</td><td>137</td><td>I</td>',
            '<td>Manado</td><td>451</td><td>I</td>',
            '<td>Gorontalo</td><td>144</td><td>II</td>']
        myTable = myTable.toNewlineFreeString().replace('   ', '')
        for myString in myExpectedStrings:
            self.assertIn(myString, myTable)

        self.maxDiff = None
        myExpectedPath = (
            '/tmp/inasafe/realtime/shakemaps-extracted/'
            '20120726022003/affected-cities.html')
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myPath, myExpectedPath)
        assert myPath == myExpectedPath, myMessage

    def testFatalitiesTable(self):
        """Test rendering a fatalities table."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId)
        myShakeEvent.calculateImpacts()
        myResult = myShakeEvent.impact_table()
        # TODO compare actual content of impact table...
        myExpectedResult = (
            '/tmp/inasafe/realtime/shakemaps-extracted/'
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
                          'legend-name': PyQt4.QtCore.QString(
                              u'Population density'),
                          'fatalities-range': '0 - 100',
                          'longitude-name': PyQt4.QtCore.QString(u'Longitude'),
                          'located-label': PyQt4.QtCore.QString(u'Located'),
                          'distance-unit': PyQt4.QtCore.QString(u'km'),
                          'bearing-compass': u'n/a',
                          'elapsed-time-name': PyQt4.QtCore.QString(
                              u'Elapsed time since event'),
                          'exposure-table-name': PyQt4.QtCore.QString(
                              u'Estimated number of people affected by each '
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
                              u'sources. The fatality calculation assumes '
                              u'that no fatalities occur for shake levels '
                              u'below MMI 4. Fatality counts of less than 50 '
                              u'are disregarded.'),
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
                              u' for Disaster Reduction, Geoscience Australia '
                              u'and the World Bank-GFDRR.'),
                          'latitude-value': u'0\xb012\'36.00"S',
                          'time': '2:15:35', 'depth-value': '11.0'}
        myResult['elapsed-time'] = u''
        myMessage = 'Got:\n%s\nExpected:\n%s\n' % (myResult, myExpectedDict)
        self.maxDiff = None
        myDifference = DictDiffer(myResult, myExpectedDict)
        print myDifference.all()
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
        myShaking = myShakeEvent.mmi_shaking(5)
        myExpectedShaking = 'Sedang'
        self.assertEqual(myExpectedShaking, myShaking)

    def test_extractDateTime(self):
        """Check that we extract date and time correctly."""
        myShakeId = '20120726022003'
        myShakeEvent = ShakeEvent(myShakeId, theLocale='en')
        myShakeEvent.extractDateTime('2012-08-07T01:55:12WIB')
        self.assertEqual(1, myShakeEvent.hour)
        self.assertEqual(55, myShakeEvent.minute)
        self.assertEqual(12, myShakeEvent.second)
        myShakeEvent.extractDateTime('2013-02-07T22:22:37WIB')
        self.assertEqual(22, myShakeEvent.hour)
        self.assertEqual(22, myShakeEvent.minute)
        self.assertEqual(37, myShakeEvent.second)


class DictDiffer(object):
    """
    Taken from
    http://stackoverflow.com/questions/1165352/
                  fast-comparison-between-two-python-dictionary
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(
            past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if
                   self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if
                   self.past_dict[o] == self.current_dict[o])

    def all(self):
        string = 'Added: %s\n' % self.added()
        string += 'Removed: %s\n' % self.removed()
        string += 'changed: %s\n' % self.changed()
        return string
if __name__ == '__main__':
    suite = unittest.makeSuite(TestShakeEvent, 'testLocalCities')
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main()
