"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Inasafe Lightmaps Widget.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '5/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4.QtGui import QPushButton, QWidget
from third_party.lightmaps import LightMaps, SlippyMap, tdim


ZOOM_LEVEL_DEGREE = [
    360,
    180,
    90,
    45,
    22.5,
    11.25,
    5.625,
    2.813,
    1.406,
    0.703,
    0.352,
    0.176,
    0.088,
    0.044,
    0.022,
    0.011,
    0.005,
    0.003,
    0.001
]


class InasafeSlippyMap(SlippyMap):
    """
    Class that implement map widget based on tile osm api.
    """

    def __init__(self, theParent=None):
        SlippyMap.__init__(self, theParent)
        self.brLat, self.brLng, self.tlLat, self.tlLng = 0, 0, 0, 0

    def invalidate(self, theEmitSignal=True):
        """ Function that called every time the widget is updated
        Params:
            * theEmitSignal : bool - if true then the widget will
                                     emit signal "updated"
        """
        SlippyMap.invalidate(self, theEmitSignal)
        self.calculateExtent()

    def flipLatitude(self, theNumber):
        """
        This function will return a number which always in range of
        -90 and +90. When the number is out of range, the number
        will wrap around.
        Params:
            * theNumber - the number in degree
        Return:
            a number in range of -90 and +90
        """
        if theNumber > 90:
            theNumber = 180 - theNumber
        if theNumber < -90:
            theNumber = -180 - theNumber

        return theNumber

    def flipLongitude(self, theNumber):
        """
        This function will return a number which always in range of
        -180 and +180. When the number is out of range, the number
        will wrap around.
        Params:
            * theNumber - the number in degree
        Return:
            a number in range of -180 and +180
        """
        while theNumber > 180:
            theNumber = theNumber - 360

        while theNumber < -180:
            theNumber = theNumber + 360

        return theNumber

    def calculateExtent(self):
        """
        Calculate top left & bottom right coordinate position
        of widget in mercator projection.

        The function will fill self.trLat (top left latitude),
        self.trLng (top left longitude),
        self.brLat (bottom right latitude)
        self.brLng (bottom right longitude)
        """
        myDegree = ZOOM_LEVEL_DEGREE[self.zoom]
        myTileCountX = float(self.width) / tdim
        myWidthInDegree = myTileCountX * myDegree
        myTileCountY = float(self.height) / tdim
        myHeightInDegree = myTileCountY * myDegree
        myOffsetX = myWidthInDegree / 2
        myOffsetY = myHeightInDegree / 2

        myMinY = self.latitude - myOffsetY
        myMinX = self.longitude - myOffsetX

        myMaxY = self.latitude + myOffsetY
        myMaxX = self.longitude + myOffsetX

        self.tlLat = self.flipLatitude(myMinY)
        self.brLat = self.flipLatitude(myMaxY)
        self.tlLng = self.flipLongitude(myMinX)
        self.brLng = self.flipLongitude(myMaxX)


class InasafeLightMaps(LightMaps):
    """
    Widget that contain slippy map
    """
    def __init__(self, parent):
        LightMaps.__init__(self, parent, InasafeSlippyMap)

        self.setupUi()

    def setupUi(self):

        ## the stylesheet for zoom level is taken from leaflet.js

        self.grpZoom = QWidget(self)
        self.grpZoom .setGeometry(15, 15, 22, 45)
        self.grpZoom .setStyleSheet("""QWidget {
            border: 1px solid #888888;
            border-radius: 5px 5px 5px 5px;
        }
        """)

        ## zoom button
        self.btnZoomIn = QPushButton(self.grpZoom)
        self.btnZoomIn.setText('+')
        self.btnZoomIn.setGeometry(0, 0, 22, 22)
        self.btnZoomIn.setStyleSheet("""QPushButton {
            color: black;
            font: bold 18px/24px Arial,Helvetica,sans-serif;
            border-radius: 4px 4px 0 0;
            background-color: rgba(255, 255, 255, 0.8);
            border-bottom: 1px solid #AAAAAA;
        }
        """)

        self.btnZoomOut = QPushButton(self.grpZoom)
        self.btnZoomOut.setText('-')
        self.btnZoomOut.setGeometry(0, 24, 22, 22)
        self.btnZoomOut.setStyleSheet("""QPushButton {
            color: black;
            border-bottom: medium none;
            border-radius: 0 0 4px 4px;
            font: bold 23px/20px Tahoma,Verdana,sans-serif;
            background-color: rgba(255, 255, 255, 0.8);
        }
        """)

        self.btnZoomIn.clicked.connect(self.m_normalMap.zoomIn)
        self.btnZoomOut.clicked.connect(self.m_normalMap.zoomOut)

    def getExtent(self):
        """
        Get extent of widget in mercator projection.
        Return:
         A tuple with format like this
        (top left latitude, top left longitude,
         bottom right latitude, bottom right longitude)
        """

        return (self.m_normalMap.tlLat, self.m_normalMap.tlLng,
                self.m_normalMap.brLat, self.m_normalMap.brLng)

    #pylint: disable=W0221
    def setCenter(self, theLat, theLng, theZoom=None):
        """
        Set the center coordinate of map.
        Params:
            * theLat - latitude
            * theLng - longitude
            * theZoom - Zoom Level
        """
        self.m_normalMap.latitude = theLat
        self.m_normalMap.longitude = theLng

        if theZoom:
            self.m_normalMap.zoom = theZoom

        self.m_normalMap.invalidate()
        self.m_largeMap.invalidate()
    #pylint: enable=W0221

    def getZoomLevel(self):
        """ Get zoom level of map. """
        return self.m_normalMap.zoom

    def getCenter(self):
        """ Get center coordinate of map.
        Returns:
            A tuple of (latitude, longitude)
        """
        return (self.m_normalMap.latitude, self.m_normalMap.longitude)
