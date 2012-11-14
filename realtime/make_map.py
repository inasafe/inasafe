"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

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
import sys
import logging
from zipfile import BadZipfile

from ftp_client import FtpClient
from safe_qgis.utilities_test import getQgisTestApp
from realtime.utils import setupLogger, dataDir
from realtime.shake_event import ShakeEvent
# Loading from package __init__ not working in this context so manually doing
setupLogger()
LOGGER = logging.getLogger('InaSAFE-Realtime')

def processEvent(theEventId=None):
    # Used cached data where available
    myForceFlag = False
    # Extract the event
    try:
        myShakeEvent = ShakeEvent(theEventId=theEventId,
                                  theForceFlag=myForceFlag)
    except BadZipfile:
        # retry with force flag true
        myShakeEvent = ShakeEvent(theEventId=theEventId,
                                  theForceFlag=True)
    except:
        LOGGER.exception('An error occurred setting up the shake event.')
        return

    logging.info('Event Id: %s', myShakeEvent)
    logging.info('-------------------------------------------')

    # Always regenerate the products
    myForceFlag = True

    myPath = os.path.join(dataDir(),
                          'exposure',
                          'IDN_mosaic',
                          'popmap10_all.tif')
    if os.path.exists(myPath):
        myShakeEvent.populationRasterPath = myPath

    myShakeEvent.renderMap(myForceFlag)

    logging.info('-------------------------------------------')


if len(sys.argv) > 2:
    sys.exit('Usage:\n%s [optional shakeid]\nor\n%s --list' % (
        sys.argv[0], sys.argv[0]))
elif len(sys.argv) == 2:
    print('Processing shakemap %s' % sys.argv[1])
    myEventId = sys.argv[1]
    if myEventId in '--list':
        myFtpClient = FtpClient()
        myListing = myFtpClient.getListing()
        for myEvent in myListing:
            print myEvent
        sys.exit(0)
    elif myEventId in '--run-all':
        myFtpClient = FtpClient()
        myListing = myFtpClient.getListing()
        for myEvent in myListing:
            if 'out' not in myEvent:
                continue
            myEvent = myEvent.replace('ftp://118.97.83.243/', '')
            myEvent = myEvent.replace('.out.zip', '')
            print 'Processing %s' % myEvent
            try:
                processEvent(myEvent)
            except:
                LOGGER.exception('Failed to process %s' % myEvent)
        sys.exit(0)
    else:
        processEvent(myEventId)

else:
    myEventId = None
    print('Processing latest shakemap')
    processEvent()



