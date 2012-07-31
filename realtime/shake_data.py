"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import os

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '30/07/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from realtime.exceptions import (EventUndefinedError,
                                 NetworkError,
                                 EventValidationError)
from realtime.ftp_client import FtpClient
from realtime.utils import shakemapDataDir


class ShakeData:
    """A class for retrieving, reading, converting and extracting
       data from shakefiles.

    Shake files are provided on an ftp server. There are two files for every
    event:
       * an 'inp' file
       * an 'out' file

    These files are provided on the ftp server as zip files. For example:
        * `ftp://118.97.83.243/20110413170148.inp.zip`_
        * `ftp://118.97.83.243/20110413170148.out.zip`_

    There are numerous files provided within these two zip files, but there
    are only really two that we are interested in:

        * grid.xyz - which contains all the metadata pertaining to the event
        * mi.grd - which contains the GMT formatted raster shake MMI data.

    This class provides a high level interface for retrieving this data and
    then extracting various by products from it.
    """

    def __init__(self, theEvent=None, theHost='118.97.83.243'):
        """Constructor for the ShakeData class

            Args:
                * theEvent - (Optional) a string representing the event id
                  that this raster is associated with. e.g. 20110413170148.
                  **If no event id is supplied, a query will be made to the
                  ftp server, and the latest event id assigned.**
                * theData - (Optional) a string representing the ip address
                  or host name of the server from which the data should be
                  retrieved. It assumes that the data is in the root directory.
                  Defaults to 118.97.83.243

            Returns:
                None

            Raises:
                None

            """
        self.eventId = theEvent
        self.host = theHost
        if self.eventId is None:
            try:
                self.eventId = self.getLatestEventId()
            except NetworkError:
                raise
        else:
            # If we fetched it above using getLatestEventId we assume it is
            # already validated.
            try:
                self.validateEvent()
            except EventValidationError:
                raise

    def getLatestEventId(self):
        """Query the ftp server and determine the latest event id.

        Args: None

        Returns: A string containing a valid event id.

        Raises: NetworkError
        """
        myFtpClient = FtpClient()
        try:
            myList = myFtpClient.getListing()
        except NetworkError:
            raise
        self.eventId = myList[-1].split('.')[0]

    def validateEvent(self):
        """Check that the event associated with this instance exists either
        in the local event cache, or on the remote ftp site.

        Args: None

        Returns: True if valid, False if not

        Raises: NetworkError
        """
        # First check local cache
        myInpFileName = self.eventId + 'inp.zip'
        myOutFileName = self.eventId + 'out.zip'
        myInpFilePath = os.path.join(shakemapDataDir(),
                                     myInpFileName)
        myOutFileName = os.path.join(shakemapDataDir(),
                                     myOutFileName)
        if (os.path.exists(myInpFilePath) and
            os.path.exists(myOutFilePath)):
            # TODO: we should actually try to unpack them for deeper validation
            return True

        myFtpClient = FtpClient()
        myList = myFtpClient.getListing()
        if (myInpFileName in myList and myOutFileName in myList):
            return True

    def _fetchFile(self, theEventFile):
        """Private helper to fetch a file from the ftp site.

          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        Args: None

        Returns: A string for the dataset path on the local storage system.

        Raises: EventUndefinedError, NetworkError
        """
        if self.eventId is None:
            raise EventUndefinedError('Event is none')
        try:
            myClient = FtpClient()
            myLocalPath = os.path.join(shakemapDataDir, theEventFile)
            myClient.getFile(theEventFile, myLocalPath)
        except:
            # TODO: differentiate between file not found and networ errors.
            raise NetworkError('Message failed to retrieve '
                               'file. %s' % theEventFile)
        return myLocalPath

    def fetchInput(self):
        """Fetch the input file for the event id associated with this class
           e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.inp.zip

          and this local file created::

              /tmp/realtime/20110413170148.inp.zip

        Args: None

        Returns: A string for the 'inp' dataset path on the local storage
            system.

        Raises: EventUndefinedError, NetworkError
        """
        myEventFile = self.eventId + '.inp.zip'
        try:
            self._fetchFile(myEventFile)
        except (EventUndefinedError, NetworkError):
            raise
        return myEventFile

    def fetchOutput(self):
        """Fetch the output file for the event id associated with this class.
          e.g. for event 20110413170148 this file would be fetched::

              ftp://118.97.83.243/20110413170148.out.zip

          and this local file created::

              /tmp/realtime/20110413170148.out.zip

        Args: None

        Returns: A string for the 'out' dataset path on the local storage
            system.

        Raises: EventUndefinedError, NetworkError
        """
        myEventFile = self.eventId + '.out.zip'
        try:
            self._fetchFile(myEventFile)
        except (EventUndefinedError, NetworkError):
            raise
        return myEventFile


    def fetchEvent(self):
        """Fetch both the input and output shake data from the server for
        the event id associated with this class.

        Args: None

        Returns: A two tuple where the first item is the inp dataset path and
        the second the out dataset path on the local storage system.

        Raises: EventUndefinedError, NetworkError
        """
        try:
            myInpFile = self.fetchInput()
            myOutFile = self.fetchOutput()
        except (EventUndefinedError, NetworkError):
            raise
        return (myInpFile, myOutFile)

