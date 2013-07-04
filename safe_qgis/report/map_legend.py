"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **InaSAFE map legend module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from PyQt4 import QtCore, QtGui
from qgis.core import QgsMapLayer
from safe_qgis.exceptions import LegendLayerError, KeywordNotFoundError
from safe_qgis.utilities.utilities import qgisVersion, dpiToMeters
from safe_qgis.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger('InaSAFE')


class MapLegend():
    """A class for creating a map legend."""
    def __init__(self, theLayer, theDpi=300, theLegendTitle=None,
                 theLegendNotes=None, theLegendUnits=None):
        """Constructor for the Map Legend class.

        Args:
            * theLayer: QgsMapLayer object that the legend should be generated
                for.
            * theDpi: Optional DPI for generated legend image. Defaults to
                300 if not specified.
        Returns:
            None
        Raises:
            Any exceptions raised will be propagated.
        """
        LOGGER.debug('InaSAFE Map class initialised')
        self.legendImage = None
        self.layer = theLayer
        # how high each row of the legend should be
        self.legendIncrement = 42
        self.keywordIO = KeywordIO()
        self.legendFontSize = 8
        self.legendWidth = 900
        self.dpi = theDpi
        if theLegendTitle is None:
            self.legendTitle = self.tr('Legend')
        else:
            self.legendTitle = theLegendTitle
        self.legendNotes = theLegendNotes
        self.legendUnits = theLegendUnits

    def tr(self, theString):
        """We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        # noinspection PyCallByClass,PyTypeChecker
        return QtCore.QCoreApplication.translate('MapLegend', theString)

    def getLegend(self):
        """Examine the classes of the impact layer associated with this print
        job.

        .. note: This is a wrapper for the rasterLegend and vectorLegend
           methods.

        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map Legend getLegend called')
        if self.layer is None:
            myMessage = self.tr('Unable to make a legend when map generator '
                                'has no layer set.')
            raise LegendLayerError(myMessage)
        try:
            self.keywordIO.readKeywords(self.layer, 'impact_summary')
        except KeywordNotFoundError, e:
            myMessage = self.tr('This layer does not appear to be an impact '
                                'layer. Try selecting an impact layer in the '
                                'QGIS layers list or creating a new impact '
                                'scenario before using the print tool.'
                                '\nMessage: %s' % str(e))
            raise Exception(myMessage)
        if self.layer.type() == QgsMapLayer.VectorLayer:
            return self.getVectorLegend()
        else:
            return self.getRasterLegend()

    def getVectorLegend(self):
        """Get the legend for this layer as a graphic.

        Args:
            None
        Returns:
            A QImage object.
            self.legend is also populated with the image.
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map getVectorLegend called')
        if not self.layer.isUsingRendererV2():
            myMessage = self.tr('A legend can only be generated for '
                                'vector layers that use the "new symbology" '
                                'implementation in QGIS.')
            raise LegendLayerError(myMessage)
            # new symbology - subclass of QgsFeatureRendererV2 class
        self.legendImage = None
        myRenderer = self.layer.rendererV2()
        myType = myRenderer.type()
        LOGGER.debug('myType' + str(myType))
        if myType == "singleSymbol":
            LOGGER.debug('singleSymbol')
            mySymbol = myRenderer.symbol()
            self.addSymbolToLegend(theLabel=self.layer.name(),
                                   theSymbol=mySymbol,
                                   theType=myType)
        elif myType == "categorizedSymbol":
            LOGGER.debug('categorizedSymbol')
            for myCategory in myRenderer.categories():
                mySymbol = myCategory.symbol()
                LOGGER.debug('theCategory' + myCategory.value().toString())
                self.addSymbolToLegend(
                    theCategory=myCategory.value().toString(),
                    theLabel=myCategory.label(),
                    theSymbol=mySymbol,
                    theType=myType)
        elif myType == "graduatedSymbol":
            LOGGER.debug('graduatedSymbol')
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol()
                self.addSymbolToLegend(theMin=myRange.lowerValue(),
                                       theMax=myRange.upperValue(),
                                       theLabel=myRange.label(),
                                       theSymbol=mySymbol,
                                       theType=myType)
        else:
            LOGGER.debug('else')
            #type unknown
            myMessage = self.tr('Unrecognised renderer type found for the '
                                'impact layer. Please use one of these: '
                                'single symbol, categorised symbol or '
                                'graduated symbol and then try again.')
            raise LegendLayerError(myMessage)
        self.addLegendNotes()
        return self.legendImage

    def getRasterLegend(self):
        """Get the legend for a raster layer as an image.

        Args:
            None
        Returns:
            An image representing the layer's legend.
            self.legend is also populated
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map Legend getRasterLegend called')
        # test if QGIS 1.8.0 or older
        # see issue #259
        if qgisVersion() <= 10800:
            myShader = self.layer.rasterShader().rasterShaderFunction()
            myRampItems = myShader.colorRampItemList()
            myLastValue = 0  # Making an assumption here...
            LOGGER.debug('Source: %s' % self.layer.source())
            for myItem in myRampItems:
                myValue = myItem.value
                myLabel = myItem.label
                myColor = myItem.color
                self.addClassToLegend(myColor,
                                      theMin=myLastValue,
                                      theMax=myValue,
                                      theLabel=myLabel,
                                      theType='rasterStyle')
                myLastValue = myValue
        else:
            #TODO implement QGIS2.0 variant
            #In master branch, use QgsRasterRenderer::rasterRenderer() to
            # get/set how a raster is displayed.
            pass
        self.addLegendNotes()
        return self.legendImage

    def addSymbolToLegend(self,
                          theSymbol,
                          theMin=None,
                          theMax=None,
                          theCategory=None,
                          theLabel=None,
                          theType=None):
        """Add a class to the current legend. If the legend is not defined,
        a new one will be created. A legend is just an image file with nicely
        rendered classes in it.

        .. note:: This method just extracts the colour from the symbol and then
           delegates to the addClassToLegend function.

        Args:

            * theSymbol - **Required** symbol for the class as a QgsSymbol
            * theMin - Optional minimum value for the class
            * theMax - Optional maximum value for the class\
            * theCategory - Optional category name (will be used in lieu of
                       min/max)
            * theLabel - Optional text label for the class

        Returns:
            None
        Raises:
            Throws an exception if the class could not be added for
            some reason..
        """
        LOGGER.debug('InaSAFE Map Legend addSymbolToLegend called')
        myColour = theSymbol.color()
        self.addClassToLegend(myColour,
                              theMin=theMin,
                              theMax=theMax,
                              theCategory=theCategory,
                              theLabel=theLabel,
                              theType=theType)

    def addClassToLegend(self,
                         theColour,
                         theMin=None,
                         theMax=None,
                         theCategory=None,
                         theLabel='',
                         theType=None):
        """Add a class to the current legend. If the legend is not defined,
        a new one will be created. A legend is just an image file with nicely
        rendered classes in it.

        Args:

            * theColour - **Required** colour for the class as a QColor
            * theMin - Optional minimum value for the class
            * theMax - Optional maximum value for the class\
            * theCategory - Optional category name (will be used in lieu of
                       min/max)
            * theLabel - Optional text label for the class

        Returns:
            None
        Raises:
            Throws an exception if the class could not be added for
            some reason..
        """
        LOGGER.debug('InaSAFE Map Legend addClassToLegend called')
        self.extendLegend()
        myOffset = self.legendImage.height() - self.legendIncrement
        myPainter = QtGui.QPainter(self.legendImage)
        myBrush = QtGui.QBrush(theColour)
        myPainter.setBrush(myBrush)
        myPainter.setPen(theColour)
        myWhitespace = 2  # white space above and below each class icon
        mySquareSize = self.legendIncrement - (myWhitespace * 2)
        myLeftIndent = 10
        myPainter.drawRect(QtCore.QRectF(myLeftIndent,
                                         myOffset + myWhitespace,
                                         mySquareSize, mySquareSize))
        myPainter.setPen(QtGui.QColor(0, 0, 0))  # outline colour
        myLabelX = myLeftIndent + mySquareSize + 10
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             self.legendFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myFontMetrics = QtGui.QFontMetricsF(myFont, self.legendImage)
        myFontHeight = myFontMetrics.height()
        myCenterVerticalPadding = (self.legendIncrement - myFontHeight) / 2
        myExtraVerticalSpace = 8  # hack to get label centered on graphic
        myOffset += myCenterVerticalPadding + myExtraVerticalSpace
        myPainter.setFont(myFont)
        LOGGER.debug('theLabel' + str(theLabel))
        LOGGER.debug('theMin ' + str(theMin))
        LOGGER.debug('theMax ' + str(theMax))
        LOGGER.debug('theCategory ' + str(theCategory))
        if theLabel is not None and theLabel != '':
            pass
        else:
        # branches for each style type
            if theType == 'singleSymbol':
                LOGGER.debug('singleSymbol is not impelemented yet')
            elif theType == 'categorizedSymbol':
                if theCategory is not None or theCategory == '':
                    theLabel = str(theCategory)
            elif theType == 'graduatedSymbol' or theType == 'rasterStyle':
                # can be a problem if the min and theMax is not found
                if theMin is None or theMax is None:
                    LOGGER.debug('Problem caused theMin or theMax is not '
                                 'found')
                    return
                else:
                    if float(theMin) - int(theMin) == 0.0:
                        myMinString = '%i' % theMin
                    else:
                        myMinString = str(theMin)
                    if float(theMax) - int(theMax) == 0.0:
                        myMaxString = '%i' % theMax
                    else:
                        myMaxString = str(theMax)
                    theLabel += '[' + myMinString + ', ' + myMaxString + ']'
                if float(str(theMin)) == float(str(theMax)):
                    # pass because it's not needed
                    return

        myPainter.drawText(myLabelX, myOffset + 25, theLabel)

    def addLegendNotes(self):
        """Add legend notes to the legend
        """
        LOGGER.debug('InaSAFE Map Legend addLegendNotes called')
        if self.legendNotes is not None:
            self.extendLegend()
            myOffset = self.legendImage.height() - 15
            myPainter = QtGui.QPainter(self.legendImage)
            myFontWeight = QtGui.QFont.StyleNormal
            myItalicsFlag = True
            legendNotesFontSize = self.legendFontSize / 2
            myFont = QtGui.QFont(
                'verdana',
                legendNotesFontSize,
                myFontWeight,
                myItalicsFlag)
            myPainter.setFont(myFont)
            myPainter.drawText(10, myOffset, self.legendNotes)
        else:
            LOGGER.debug('No notes')

    def extendLegend(self):
        """Grow the legend pixmap enough to accommodate one more legend entry.

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propogated.
        """
        LOGGER.debug('InaSAFE Map Legend extendLegend called')
        if self.legendImage is None:

            self.legendImage = QtGui.QImage(self.legendWidth, 95,
                                            QtGui.QImage.Format_RGB32)
            self.legendImage.setDotsPerMeterX(dpiToMeters(self.dpi))
            self.legendImage.setDotsPerMeterY(dpiToMeters(self.dpi))

            # Only works in Qt4.8
            #self.legendImage.fill(QtGui.QColor(255, 255, 255))
            # Works in older Qt4 versions
            self.legendImage.fill(255 + 255 * 256 + 255 * 256 * 256)
            myPainter = QtGui.QPainter(self.legendImage)
            myFontWeight = QtGui.QFont.Bold
            myItalicsFlag = False
            myFont = QtGui.QFont('verdana',
                                 self.legendFontSize,
                                 myFontWeight,
                                 myItalicsFlag)
            myPainter.setFont(myFont)
            myPainter.drawText(10, 25, self.legendTitle)

            if self.legendUnits is not None:
                myFontWeight = QtGui.QFont.StyleNormal
                myItalicsFlag = True
                legendUnitsFontSize = self.legendFontSize / 2
                myFont = QtGui.QFont(
                    'verdana',
                    legendUnitsFontSize,
                    myFontWeight,
                    myItalicsFlag)
                myPainter.setFont(myFont)
                myPainter.drawText(10, 45, self.legendUnits)

        else:
            # extend the existing legend down for the next class
            myImage = QtGui.QImage(
                self.legendWidth,
                self.legendImage.height() + self.legendIncrement,
                QtGui.QImage.Format_RGB32)
            myImage.setDotsPerMeterX(dpiToMeters(self.dpi))
            myImage.setDotsPerMeterY(dpiToMeters(self.dpi))
            # Only works in Qt4.8
            #myImage.fill(QtGui.qRgb(255, 255, 255))
            # Works in older Qt4 versions
            myImage.fill(255 + 255 * 256 + 255 * 256 * 256)
            myPainter = QtGui.QPainter(myImage)

            myRect = QtCore.QRectF(0, 0,
                                   self.legendImage.width(),
                                   self.legendImage.height())
            myPainter.drawImage(myRect, self.legendImage, myRect)
            self.legendImage = myImage
