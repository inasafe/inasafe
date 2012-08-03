"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake events.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '1/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os

from utils import shakemapExtractDir
from rt_exceptions import EventFileNotFoundError
# The logger is intiailsed in utils.py by init
import logging
LOGGER = logging.getLogger('InaSAFE-Realtime')

class ShakeEvent:
    """The ShakeEvent class encapsulates behaviour and data relating to an
    earthquake, including epicenter, magniture etc."""

    def __init__(self, theEventId):
        """Constructor for the shake event class.

        Args:
            theEventId - (Mandatory) Id of the event. Will be used to
                determine the path to an event.xml file that
                will be used to intialise the state of the ShakeEvent instance.

            e.g.

            /tmp/inasafe/realtime/shakemaps-extracted/20120726022003/event.xml

        Returns: Instance

        Raises: EventParseError
        """
        self.latitude = None
        self.longitude = None
        self.eventId = theEventId
        self.magnitude = None
        self.depth = None
        self.description = None
        self.location = None
        self.day = None
        self.month = None
        self.year = None
        self.time = None
        self.timeZone = None

    def eventFilePath(self):
        """A helper to retrieve the path to the event.xml file

        Args: None

        Returns: An absolute filesystem path to the event.xml file.

        Raises: EventFileNotFoundError
        """
        myEventPath = os.path.join(shakemapExtractDir(), 'event.xml')
        #short circuit if the tif is already created.
        if os.path.exists(myEventPath):
            return myEventPath
        else:
            LOGGER.error('Event file not found. %s' % myEventPath)
            raise EventFileNotFoundError('%s not found' % myEventPath)
