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
from xml.dom import minidom
from utils import shakemapExtractDir
from rt_exceptions import (EventFileNotFoundError,
                           EventXmlParseError,
                           GridXmlFileNotFoundError,
                           GridXmlParseError)
# The logger is intialised in utils.py by init
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

        Raises: EventXmlParseError
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
        self.xMinimum = None
        self.xMaximum = None
        self.yMinimum = None
        self.yMaximum = None
        self.mmiData = None
        self.parseEvent()
        self.parseGridXml()

    def eventFilePath(self):
        """A helper to retrieve the path to the event.xml file

        Args: None

        Returns: An absolute filesystem path to the event.xml file.

        Raises: EventFileNotFoundError
        """
        LOGGER.debug('Event path requested.')
        myEventPath = os.path.join(shakemapExtractDir(),
                                   self.eventId,
                                   'event.xml')
        #short circuit if the tif is already created.
        if os.path.exists(myEventPath):
            return myEventPath
        else:
            LOGGER.error('Event file not found. %s' % myEventPath)
            raise EventFileNotFoundError('%s not found' % myEventPath)

    def gridFilePath(self):
        """A helper to retrieve the path to the grid.xml file

        Args: None

        Returns: An absolute filesystem path to the grid.xml file.

        Raises: GridXmlFileNotFoundError
        """
        LOGGER.debug('Event path requested.')
        myGridXmlPath = os.path.join(shakemapExtractDir(),
                                   self.eventId,
                                   'grid.xml')
        #short circuit if the tif is already created.
        if os.path.exists(myGridXmlPath):
            return myGridXmlPath
        else:
            LOGGER.error('Event file not found. %s' % myGridXmlPath)
            raise GridXmlFileNotFoundError('%s not found' % myGridXmlPath)

    def parseEvent(self):
        """Parse the event.xml and extract whatever info we can from it.

        The event is parsed and class members are populated with whatever
        data could be obtained from the event.

        Args: None

        Returns : None

        Raises: EventXmlParseError
        """
        LOGGER.debug('ParseEvent requested.')
        myPath = self.eventFilePath()
        try:
            myDocument = minidom.parse(myPath)
            myEventElement = myDocument.getElementsByTagName('earthquake')
            myEventElement = myEventElement[0]
            self.magnitude = float(myEventElement.attributes['mag'].nodeValue)
            self.longitude = float(myEventElement.attributes['lon'].nodeValue)
            self.latitude = float(myEventElement.attributes['lat'].nodeValue)
            self.location = myEventElement.attributes[
                            'locstring'].nodeValue.strip()
            self.depth = float(myEventElement.attributes['depth'].nodeValue)
            self.year = int(myEventElement.attributes['year'].nodeValue)
            self.month = int(myEventElement.attributes['month'].nodeValue)
            self.day = int(myEventElement.attributes['day'].nodeValue)
            self.hour = int(myEventElement.attributes['hour'].nodeValue)
            self.minute = int(myEventElement.attributes['minute'].nodeValue)
            self.second = int(myEventElement.attributes['second'].nodeValue)
            # Note teh timezone here is inconsistent with YZ from grid.xml
            # use the latter
            self.timeZone = myEventElement.attributes['timezone'].nodeValue

        except Exception, e:
            LOGGER.exception('Event parse failed')
            raise EventXmlParseError('Failed to parse event file.\n%s\n%s'
                % (e.__class__, str(e)))

    def parseGridXml(self):
        """Parse the grid xyz and calculate the bounding box of the event.

        The grid xyz dataset looks like this::

           <?xml version="1.0" encoding="US-ASCII" standalone="yes"?>
           <shakemap_grid xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns="http://earthquake.usgs.gov/eqcenter/shakemap"
           xsi:schemaLocation="http://earthquake.usgs.gov
           http://earthquake.usgs.gov/eqcenter/shakemap/xml/schemas/
           shakemap.xsd" event_id="20120807015938" shakemap_id="20120807015938"
           shakemap_version="1" code_version="3.5"
           process_timestamp="2012-08-06T18:28:37Z" shakemap_originator="us"
           map_status="RELEASED" shakemap_event_type="ACTUAL">
           <event magnitude="5.1" depth="206" lat="2.800000"
               lon="128.290000" event_timestamp="2012-08-07T01:55:12WIB"
               event_network="" event_description="Halmahera, Indonesia    " />
           <grid_specification lon_min="126.290000" lat_min="0.802000"
               lon_max="130.290000" lat_max="4.798000"
               nominal_lon_spacing="0.025000" nominal_lat_spacing="0.024975"
               nlon="161" nlat="161" />
           <grid_field index="1" name="LON" units="dd" />
           <grid_field index="2" name="LAT" units="dd" />
           <grid_field index="3" name="PGA" units="pctg" />
           <grid_field index="4" name="PGV" units="cms" />
           <grid_field index="5" name="MMI" units="intensity" />
           <grid_field index="6" name="PSA03" units="pctg" />
           <grid_field index="7" name="PSA10" units="pctg" />
           <grid_field index="8" name="PSA30" units="pctg" />
           <grid_field index="9" name="STDPGA" units="pctg" />
           <grid_field index="10" name="URAT" units="" />
           <grid_field index="11" name="SVEL" units="ms" />
           <grid_data>
           126.2900 04.7980 0.01 0.02 1.16 0.05 0.02 0 0.5 1 600
           126.3150 04.7980 0.01 0.02 1.16 0.05 0.02 0 0.5 1 600
           126.3400 04.7980 0.01 0.02 1.17 0.05 0.02 0 0.5 1 600
           126.3650 04.7980 0.01 0.02 1.17 0.05 0.02 0 0.5 1 600
           ...
           ... etc

        .. note:: We could have also obtained this data from the grid.xml
           but the **grid.xml** is preferred because it contains clear and
           unequivical metadata describing the various fields and attributes.

        We already have most of the event details from event.xml so we are
        primarily interested in event_specification (in order to compute the
        bounding box) and grid_data (in order to obtain an MMI raster).

        Args: None

        Returns: None

        Raises: GridXmlParseError
        """
        LOGGER.debug('ParseGridXml requested.')
        myPath = self.gridFilePath()
        try:
            myDocument = minidom.parse(myPath)
            mySpecificationElement = myDocument.getElementsByTagName(
                'grid_specification')
            mySpecificationElement = mySpecificationElement[0]
            self.xMinimum = float(mySpecificationElement.attributes[
                                  'lon_min'].nodeValue)
            self.xMaximum = float(mySpecificationElement.attributes[
                                  'lon_max'].nodeValue)
            self.yMinimum = float(mySpecificationElement.attributes[
                                  'lat_min'].nodeValue)
            self.yMaximum = float(mySpecificationElement.attributes[
                                  'lat_max'].nodeValue)
            myDataElement = myDocument.getElementsByTagName(
                'grid_data')
            myDataElement = myDataElement[0]
            myData = myDataElement.firstChild.nodeValue

            # Extract the 1,2 and 5th (MMI) columns and populate mmiData
            myLonColumn = 1
            myLatColumn = 2
            myMMIColumn = 5
            self.mmiData = []
            for myLine in myData.split('\n'):
                myTokens = myLine.split(' ')
                print myTokens
                myLon = myTokens[myLonColumn]
                myLat = myTokens[myLatColumn]
                myMMI = myTokens[myMMIColumn]
                myTuple= (myLon, myLat, myMMI)
                self.mmiData.append(myTuple)

        except Exception, e:
            LOGGER.exception('Event parse failed')
            raise GridXmlParseError('Failed to parse grid file.\n%s\n%s'
                % (e.__class__, str(e)))
