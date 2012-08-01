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
from realtime.utils import (shakemapZipDir,
                            shakemapDataDir,
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
        myInpPath =  os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  'fixtures',
                                                  myInpFile))
        shutil.copyfile(myOutPath, os.path.join(shakemapZipDir(), myOutFile))
        shutil.copyfile(myInpPath, os.path.join(shakemapZipDir(), myInpFile))

        #TODO Downloaded data should be removed before each test

    def test_getShakeMapInput(self):
        """Check that we can retrieve a shakemap 'inp' input file"""
        myShakeEvent = '20110413170148'
        myShakeData = ShakeData(myShakeEvent)
        myShakemapFile =  myShakeData.fetchInput()
        myExpectedFile = os.path.join(shakemapZipDir(),
                                      myShakeEvent + '.inp.zip')
        myMessage = 'Expected path for downloaded shakemap INP not received'
        self.assertEqual(myShakemapFile, myExpectedFile, myMessage)

    def test_getShakeMapOutput(self):
        """Check that we can retrieve a shakemap 'out' input file"""
        myEventId = '20110413170148'
        myShakeData = ShakeData(myEventId)
        myShakemapFile =  myShakeData.fetchOutput()
        myExpectedFile = os.path.join(shakemapZipDir(),
                                      myEventId + '.out.zip')
        myMessage = 'Expected path for downloaded shakemap OUT not received'
        self.assertEqual(myShakemapFile, myExpectedFile, myMessage)

    def test_getRemoteShakeMap(self):
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

        myInpFile, myOutFile =  myShakeData.fetchEvent()
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

    def test_getCachedShakeMap(self):
        """Check that we can retrieve both input and output from ftp at once"""
        myShakeEvent = '20120726022003'

        myExpectedInpFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.inp.zip')
        myExpectedOutFile = os.path.join(shakemapZipDir(),
                                         myShakeEvent + '.out.zip')
        myShakeData = ShakeData(myShakeEvent)
        myInpFile, myOutFile =  myShakeData.fetchEvent()
        myMessage = ('Expected path for downloaded shakemap INP not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myInpFile, myExpectedInpFile, myMessage)
        myMessage = ('Expected path for downloaded shakemap OUT not received'
             '\nExpected: %s\nGot: %s' %
             (myExpectedOutFile, myOutFile))
        self.assertEqual(myOutFile, myExpectedOutFile, myMessage)

    def test_getLatestShakeMap(self):
        """Check that we can retrieve the latest shake event"""
        # Simply dont set the event id in the ctor to get the latest
        myShakeData = ShakeData()
        myInpFile, myOutFile =  myShakeData.fetchEvent()
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

    def test_ExtractShakeMap(self):
        """Test that we can extract the shakemap inp and out files"""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        myEvent, myGrd = myShakeData.extract(theForceFlag=True)

        myExtractDir = shakemapExtractDir()
        myExpectedEvent = (os.path.join(myExtractDir,
                           '20120726022003/event.xml'))
        myExpectedGrid = (os.path.join(myExtractDir,
                           '20120726022003/mi.grd'))
        myMessage = 'Expected: %s\nGot: %s\n' % (myExpectedEvent, myEvent)
        assert myEvent in myExpectedEvent, myMessage
        assert os.path.exists(myEvent)

        myMessage = 'Expected: %s\nGot: %s\n' % (myExpectedGrid, myGrd)
        assert myExpectedGrid in myExpectedGrid, myMessage
        assert os.path.exists(myGrd)

    def test_convertGrdToTif(self):
        """Test that we can convert the grid file to a tif file"""
        myShakeEvent = '20120726022003'
        myShakeData = ShakeData(myShakeEvent)
        # Postprocess the event.xml and the mi.grd into a ShakeEvent object
        # and a .tif file respectively.
        myEvent, myGrd = myShakeData.postProcess(theForceFlag=True)
        assert os.path.exists(myGrd)


if __name__ == '__main__':
    unittest.main()
