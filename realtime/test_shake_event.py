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
import unittest
from utils import shakemapExtractDir
from shake_data import ShakeData
from shake_event import ShakeEvent


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""

    def test_eventFilePath(self):
        """Test eventFilePath works(using cached data)"""
        myShakeId = '20120726022003'
        myExpectedPath = os.path.join(shakemapExtractDir(),
                                      myShakeId,
                                      'event.xml')
        myShakeData = ShakeData(myShakeId)
        myShakeData.extract()
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.eventFilePath()
        self.assertEquals(myExpectedPath, myPath)

    def test_eventFilePath(self):
        """Test eventFilePath works(using cached data)"""
        myShakeId = '20120726022003'
        myExpectedPath = os.path.join(shakemapExtractDir(),
                                      myShakeId,
                                      'event.xml')
        myShakeData = ShakeData(myShakeId)
        myShakeData.extract()
        myShakeEvent = ShakeEvent(myShakeId)
        myPath = myShakeEvent.eventFilePath()
        self.assertEquals(myExpectedPath, myPath)

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
        # These are retrieved from event.xml
        self.assertEquals(26, myShakeEvent.day)
        self.assertEquals(7, myShakeEvent.month)
        self.assertEquals(2012, myShakeEvent.year)
        self.assertEquals(2, myShakeEvent.hour)
        self.assertEquals(15, myShakeEvent.minute)
        self.assertEquals(35, myShakeEvent.second)
        # We really want GMT time here...
        self.assertEquals('WIB', myShakeEvent.timeZone)
        self.assertEquals(124.45, myShakeEvent.longitude)
        self.assertEquals(-0.21, myShakeEvent.latitude)
        self.assertEquals(11.0, myShakeEvent.depth)
        self.assertEquals('Southern Molucca Sea', myShakeEvent.location)
        # And these from grid.xml
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
        myFile = file(myPath,'rt')
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
mmiData: Populated"""
        myState = str(myShakeEvent)
        myMessage = (('Expected:\n----------------\n%s'
                     '\n\nGot\n------------------\n%s\n') %
                     (myExpectedState, myState))
        assert myState == myExpectedState, myMessage
        myPath = myShakeEvent.mmiDataToRaster(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('tif','qml')
        assert os.path.exists(myExpectedQml)

    def testEventToShapefile(self):
        """Check we can convert the shake event to a raster"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.mmiDataToShapefile(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('shp','qml')
        myMessage = '%s not found' % myExpectedQml
        assert os.path.exists(myExpectedQml), myMessage

    def testEventToContours(self):
        """Check we can extract contours from the event"""
        myShakeId = '20120726022003'
        myShakeData = ShakeData(myShakeId)
        myShakeEvent = myShakeData.shakeEvent()
        myPath = myShakeEvent.mmiDataToContours(theForceFlag=True)
        assert os.path.exists(myPath)
        myExpectedQml = myPath.replace('shp','qml')
        myMessage = '%s not found' % myExpectedQml
        assert os.path.exists(myExpectedQml), myMessage

if __name__ == '__main__':
    unittest.main()
