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
from urllib2 import URLError
from zipfile import BadZipfile

from ftp_client import FtpClient
from sftp_client import SFtpClient
from utils import setupLogger, dataDir, is_event_id
from shake_event import ShakeEvent
# Loading from package __init__ not working in this context so manually doing
setupLogger()
LOGGER = logging.getLogger('InaSAFE')


def processEvent(theEventId=None, theLocale='en'):
    """Launcher that actually runs the event processing."""
    myPopulationPath = os.path.join(
        dataDir(),
        'exposure',
        'IDN_mosaic',
        'popmap10_all.tif')

    # Use cached data where available
    # Whether we should always regenerate the products
    myForceFlag = False
    if 'INASAFE_FORCE' in os.environ:
        myForceString = os.environ['INASAFE_FORCE']
        if str(myForceString).capitalize() == 'Y':
            myForceFlag = True

    # We always want to generate en products too so we manipulate the locale
    # list and loop through them:
    myLocaleList = [theLocale]
    if 'en' not in myLocaleList:
        myLocaleList.append('en')

    # Now generate the products
    for myLoc in myLocaleList:
        # Extract the event
        # noinspection PyBroadException
        try:
            if os.path.exists(myPopulationPath):
                myShakeEvent = ShakeEvent(
                    theEventId=theEventId,
                    theLocale=myLoc,
                    theForceFlag=myForceFlag,
                    thePopulationRasterPath=myPopulationPath)
            else:
                myShakeEvent = ShakeEvent(
                    theEventId=theEventId,
                    theLocale=myLoc,
                    theForceFlag=myForceFlag)
        except (BadZipfile, URLError):
            # retry with force flag true
            if os.path.exists(myPopulationPath):
                myShakeEvent = ShakeEvent(
                    theEventId=theEventId,
                    theLocale=myLoc,
                    theForceFlag=True,
                    thePopulationRasterPath=myPopulationPath)
            else:
                myShakeEvent = ShakeEvent(
                    theEventId=theEventId,
                    theLocale=myLoc,
                    theForceFlag=True)
        except:
            LOGGER.exception('An error occurred setting up the shake event.')
            return

        LOGGER.info('Event Id: %s', myShakeEvent)
        LOGGER.info('-------------------------------------------')

        myShakeEvent.renderMap(myForceFlag)

LOGGER.info('-------------------------------------------')

if 'INASAFE_LOCALE' in os.environ:
    myLocale = os.environ['INASAFE_LOCALE']
else:
    myLocale = 'en'

if len(sys.argv) > 2:
    sys.exit('Usage:\n%s [optional shakeid]\nor\n%s --list' % (
        sys.argv[0], sys.argv[0]))
elif len(sys.argv) == 2:
    print('Processing shakemap %s' % sys.argv[1])

    myEventId = sys.argv[1]
    if myEventId in '--list':
#        myFtpClient = FtpClient()
        mySftpClient = SFtpClient()
#        myListing = myFtpClient.getListing()
        myListing = mySftpClient.getListing(my_func=is_event_id)
        for myEvent in myListing:
            print myEvent
        sys.exit(0)
    elif myEventId in '--run-all':
        #
        # Caution, this code path gets memory leaks, use the
        # batch file approach rather!
        #
        myFtpClient = FtpClient()
        myListing = myFtpClient.getListing()
        for myEvent in myListing:
            if 'out' not in myEvent:
                continue
            myEvent = myEvent.replace('ftp://118.97.83.243/', '')
            myEvent = myEvent.replace('.out.zip', '')
            print 'Processing %s' % myEvent
            # noinspection PyBroadException
            try:
                processEvent(myEvent, myLocale)
            except:  # pylint: disable=W0702
                LOGGER.exception('Failed to process %s' % myEvent)
        sys.exit(0)
    else:
        processEvent(myEventId, myLocale)

else:
    myEventId = None
    print('Processing latest shakemap')
    # noinspection PyBroadException
    try:
        processEvent(theLocale=myLocale)
    except:  # pylint: disable=W0702
        LOGGER.exception('Process event failed')
