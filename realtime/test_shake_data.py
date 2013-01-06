"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Tests Shake Data functionality related to shakemaps.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import unittest

from shake_data import ShakeData
from utils import (shakemapZipDir,
                   shakemapExtractDir,
                   purgeWorkingData)

# Clear away working dirs so we can be sure they are
# actually created
purgeWorkingData()


class TestShakeMap(unittest.TestCase):
    """Testing for the shakemap class"""

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

    def testGetShakeMapInput(self):
        """Check that we can retrieve a shakemap 'inp' input file"""
        myShakeEvent = '20110413170148'
        myShakeData = ShakeData(myShakeEvent)
        myShakemapFile = myShakeData.fetchInput()
        myExpectedFile = os.path.join(shakemapZipDir(),
                                      myShakeEvent + '.inp.zip')
        myMessage = 'Expected path for downloaded shakemap INP not received'
        self.assertEqual(myShakemapFile, myExpectedFile, myMessage)

    def testGetShakeMapOutput(self):
        """Check that we can retrieve a shakemap 'out' input file"""
        myEventId = '20110413170148'
        myShakeData = ShakeData(myEventId)
        myShakemapFile = myShakeData.fetchOutput()
        myExpectedFile = os.path.join(shakemapZipDir(),
                                      myEventId + '.out.zip')
        myMessage = 'Expected path for downloaded shakemap OUT not received'
        self.assertEqual(myShakemapFile, myExpectedFile, myMessage)

    def testGetRemoteShakeMap(self):
        """Check that we can retrieve both input and output from ftp at once"""
        myShakeEvent = '20110413170148'
        myShakeData = ShakeData(myShakeEvent)

        myExpectedInpFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.inp.zip')
        myExpectedOutFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.out.zip')

        if os.path.exists(myExpectedInpFile):
            os.remove(myExpectedInpFile)
        if os.path.exists(myExpectedOutFile):
            os.remove(myExpectedOutFile)

        myInpFile, myOutFile = myShakeData.fetchEvent()
        myMessage = ('Expected path for downloaded shakemap INP not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myInpFile, myExpectedInpFile, myMessage)
        myMessage = ('Expected path for downloaded shakemap OUT not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myOutFile, myExpectedOutFile, myMessage)

        assert os.path.exists(myExpectedInpFile)
        assert os.path.exists(myExpectedOutFile)

    def testGetCachedShakeMap(self):
        """Check that we can retrieve both input and output from ftp at once"""
        myShakeEvent = '20120726022003'

        myExpectedInpFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.inp.zip')
        myExpectedOutFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.out.zip')
        myShakeData = ShakeData(myShakeEvent)
        myInpFile, myOutFile = myShakeData.fetchEvent()
        myMessage = ('Expected path for downloaded shakemap INP not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myInpFile, myExpectedInpFile, myMessage)
        myMessage = ('Expected path for downloaded shakemap OUT not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myOutFile, myExpectedOutFile, myMessage)

    def testGetLatestShakeMap(self):
        """Check that we can retrieve the latest shake event"""
        # Simply dont set the event id in the ctor to get the latest
        myShakeData = ShakeData()
        myInpFile, myOutFile = myShakeData.fetchEvent()
        myEventId = myShakeData.eventId
        myExpectedInpFile = os.path.join(shakemapZipDir(),
                                         myEventId + '.inp.zip')
        myExpectedOutFile = os.path.join(shakemapZipDir(),
                                         myEventId + '.out.zip')
        myMessage = ('Expected path for downloaded shakemap INP not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myInpFile, myExpectedInpFile, myMessage)
        myMessage = ('Expected path for downloaded shakemap OUT not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myOutFile, myExpectedOutFile, myMessage)

    def testExtractShakeMap(self):
        """Test that we can extract the shakemap inp and out files"""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        myGridXml = myShakeData.extract(theForceFlag=True)

        myExtractDir = shakemapExtractDir()

        myExpectedGridXml = (os.path.join(myExtractDir,
                           '20120726022003/grid.xml'))
        myMessage = 'Expected: %s\nGot: %s\n' % (myExpectedGridXml, myGridXml)
        assert myExpectedGridXml in myExpectedGridXml, myMessage
        assert os.path.exists(myGridXml)

    def testCheckEventIsOnServer(self):
        """Test that we can check if an event is on the server."""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        self.assertTrue(myShakeData.isOnServer(),
                        ('Data for %s is on server' % myShakeEvent))

    def testCachePaths(self):
        """Check we compute local cache paths properly."""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        myExpectedInpPath = ('/tmp/inasafe/realtime/shakemaps-zipped/'
                             '20120726022003.inp.zip')
        myExpectedOutPath = ('/tmp/inasafe/realtime/shakemaps-zipped/'
                             '20120726022003.out.zip')
        myInpPath, myOutPath = myShakeData.cachePaths()
        myMessage = 'Expected: %s\nGot: %s' % (myExpectedInpPath, myInpPath)
        assert myInpPath == myExpectedInpPath, myMessage
        myMessage = 'Expected: %s\nGot: %s' % (myExpectedOutPath, myOutPath)
        assert myOutPath == myExpectedOutPath, myMessage

    def testFileNames(self):
        """Check we compute file names properly."""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        myExpectedInpFileName = '20120726022003.inp.zip'
        myExpectedOutFileName = '20120726022003.out.zip'
        myInpFileName, myOutFileName = myShakeData.fileNames()
        myMessage = 'Expected: %s\nGot: %s' % (
            myExpectedInpFileName, myInpFileName)
        assert myInpFileName == myExpectedInpFileName, myMessage
        myMessage = 'Expected: %s\nGot: %s' % (
            myExpectedOutFileName, myOutFileName)
        assert myOutFileName == myExpectedOutFileName, myMessage

if __name__ == '__main__':
    unittest.main()
