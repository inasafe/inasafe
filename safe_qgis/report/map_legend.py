# coding=utf-8
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
from safe_qgis.utilities.utilities import dpi_to_meters
from safe_qgis.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger('InaSAFE')


class MapLegend():
    """A class for creating a map legend."""
    def __init__(
            self,
            layer,
            dpi=300,
            legend_title=None,
            legend_notes=None,
            legend_units=None):
        """Constructor for the Map Legend class.

        :param layer: Layer that the legend should be generated for.
        :type layer: QgsMapLayer, QgsVectorLayer

        :param dpi: DPI for the generated legend image. Defaults to 300 if
            not specified.
        :type dpi: int

        :param legend_title: Title for the legend.
        :type legend_title: str

        :param legend_notes: Notes to display under the title.
        :type legend_notes: str

        :param legend_units: Units for the legend.
        :type legend_units: str
        """
        LOGGER.debug('InaSAFE Map class initialised')
        self.legendImage = None
        self.layer = layer
        # how high each row of the legend should be
        self.legendIncrement = 42
        self.keywordIO = KeywordIO()
        self.legendFontSize = 8
        self.legendWidth = 900
        self.dpi = dpi
        if legend_title is None:
            self.legendTitle = self.tr('Legend')
        else:
            self.legendTitle = legend_title
        self.legendNotes = legend_notes
        self.legendUnits = legend_units

    def tr(self, string):
        """We implement this ourself since we do not inherit QObject.

        :param string: String for translation.
        :type string: QString, str

        :returns: Translated version of string.
        :rtype: QString
        """
        # noinspection PyCallByClass,PyTypeChecker
        return QtCore.QCoreApplication.translate('MapLegend', string)

    def get_legend(self):
        """Create a legend for the classes in the layer.

        .. note: This is a wrapper for raster_legend and vector_legend.

        :raises: InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map Legend getLegend called')
        if self.layer is None:
            message = self.tr('Unable to make a legend when map generator '
                                'has no layer set.')
            raise LegendLayerError(message)
        try:
            self.keywordIO.read_keywords(self.layer, 'impact_summary')
        except KeywordNotFoundError, e:
            message = self.tr('This layer does not appear to be an impact '
                                'layer. Try selecting an impact layer in the '
                                'QGIS layers list or creating a new impact '
                                'scenario before using the print tool.'
                                '\nMessage: %s' % str(e))
            raise Exception(message)
        if self.layer.type() == QgsMapLayer.VectorLayer:
            return self.vector_legend()
        else:
            return self.raster_legend()

    def vector_legend(self):
        """Get the legend for this layer as a graphic.

        :returns: An image of the legend. self.legend is also populated
            with the image.
        :rtype: QImage

        :raises: InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map getVectorLegend called')
        # new symbology - subclass of QgsFeatureRendererV2 class
        self.legendImage = None
        myRenderer = self.layer.rendererV2()
        myType = myRenderer.type()
        LOGGER.debug('myType' + str(myType))
        if myType == "singleSymbol":
            LOGGER.debug('singleSymbol')
            mySymbol = myRenderer.symbol()
            self.add_symbol(
                label=self.layer.name(),
                symbol=mySymbol,
                symbol_type=myType)
        elif myType == "categorizedSymbol":
            LOGGER.debug('categorizedSymbol')
            for myCategory in myRenderer.categories():
                mySymbol = myCategory.symbol()
                LOGGER.debug('theCategory' + myCategory.value())
                self.add_symbol(
                    category=myCategory.value(),
                    label=myCategory.label(),
                    symbol=mySymbol,
                    symbol_type=myType)
        elif myType == "graduatedSymbol":
            LOGGER.debug('graduatedSymbol')
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol()
                self.add_symbol(
                    minimum=myRange.lowerValue(),
                    maximum=myRange.upperValue(),
                    label=myRange.label(),
                    symbol=mySymbol,
                    symbol_type=myType)
        else:
            LOGGER.debug('else')
            # type unknown
            message = self.tr('Unrecognised renderer type found for the '
                                'impact layer. Please use one of these: '
                                'single symbol, categorised symbol or '
                                'graduated symbol and then try again.')
            raise LegendLayerError(message)
        self.add_notes()
        return self.legendImage

    def raster_legend(self):
        """Get the legend for a raster layer as an image.

        :returns: An image representing the layer's legend. self.legend is
            also populated.
        :rtype: QImage

        :Raises: InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map Legend getRasterLegend called')
        myShader = self.layer.renderer().shader().rasterShaderFunction()
        myRampItems = myShader.colorRampItemList()
        myLastValue = 0  # Making an assumption here...
        LOGGER.debug('Source: %s' % self.layer.source())
        for myItem in myRampItems:
            value = myItem.value
            myLabel = myItem.label
            myColor = myItem.color
            self.add_class(
                myColor,
                minimum=myLastValue,
                maximum=value,
                label=myLabel,
                class_type='rasterStyle')
            myLastValue = value
        self.add_notes()
        return self.legendImage

    def add_symbol(
            self,
            symbol,
            minimum=None,
            maximum=None,
            category=None,
            label=None,
            symbol_type=None):
        """Add a symbol to the current legend.

        If the legend is not defined, a new one will be created. A legend is
        just an image file with nicely rendered classes in it.

        :param symbol: Symbol for the class as a QgsSymbolV2
        :type symbol: QgsSymbolV2

        :param minimum: Minimum value for the class.
        :type minimum: float, int

        :param maximum: Maximum value for the class.
        :type maximum: float, int

        :param category: Category name (will be used in lieu of min/max)
        :type category: str

        :param label: Text label for the class.
        :type label: str

        :param symbol_type: One of 'singleSymbol', 'categorizedSymbol',
            'graduatedSymbol' or 'rasterStyle'
        :type symbol_type: str


        .. note:: This method just extracts the colour from the symbol and then
           delegates to the addClassToLegend function.
        """
        LOGGER.debug('InaSAFE Map Legend addSymbolToLegend called')
        myColour = symbol.color()
        self.add_class(
            myColour,
            minimum=minimum,
            maximum=maximum,
            category=category,
            label=label,
            class_type=symbol_type)

    def add_class(
            self,
            colour,
            minimum=None,
            maximum=None,
            category=None,
            label='',
            class_type=None):
        """Add a class to the current legend.

        If the legend is not defined, a new one will be created. A legend is
        just an image file with nicely rendered classes in it.

        :param colour: Colour for the class.
        :type colour: QColor

        :param minimum: Minimum value for the class.
        :type minimum: float, int

        :param maximum: Maximum value for the class.
        :type maximum: float, int

        :param category: Category name (will be used in lieu of min/max)
        :type category: str

        :param label: Text label for the class.
        :type label: str

        :param class_type: One of 'singleSymbol', 'categorizedSymbol',
            'graduatedSymbol' or 'rasterStyle'
        :type class_type: str

        """
        LOGGER.debug('InaSAFE Map Legend addClassToLegend called')
        self.grow_legend()
        myOffset = self.legendImage.height() - self.legendIncrement
        myPainter = QtGui.QPainter(self.legendImage)
        myBrush = QtGui.QBrush(colour)
        myPainter.setBrush(myBrush)
        myPainter.setPen(colour)
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
        LOGGER.debug('label' + str(label))
        LOGGER.debug('minimum ' + str(minimum))
        LOGGER.debug('maximum ' + str(maximum))
        LOGGER.debug('category ' + str(category))
        if label is not None and label != '':
            pass
        else:
        # branches for each style type
            if class_type == 'singleSymbol':
                LOGGER.debug('singleSymbol is not impelemented yet')
            elif class_type == 'categorizedSymbol':
                if category is not None or category == '':
                    label = str(category)
            elif (class_type == 'graduatedSymbol'
                  or class_type == 'rasterStyle'):
                # can be a problem if the min and maximum is not found
                if minimum is None or maximum is None:
                    LOGGER.debug('Problem caused minimum or maximum is not '
                                 'found')
                    return
                else:
                    if float(minimum) - int(minimum) == 0.0:
                        myMinString = '%i' % minimum
                    else:
                        myMinString = str(minimum)
                    if float(maximum) - int(maximum) == 0.0:
                        myMaxString = '%i' % maximum
                    else:
                        myMaxString = str(maximum)
                    label += '[' + myMinString + ', ' + myMaxString + ']'
                if float(str(minimum)) == float(str(maximum)):
                    # pass because it's not needed
                    return

        myPainter.drawText(myLabelX, myOffset + 25, label)

    def add_notes(self):
        """Add legend notes to the legend.
        """
        LOGGER.debug('InaSAFE Map Legend addLegendNotes called')
        if self.legendNotes is not None:
            self.grow_legend()
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

    def grow_legend(self):
        """Grow the legend pixmap enough to accommodate one more legend entry.
        """
        LOGGER.debug('InaSAFE Map Legend extendLegend called')
        if self.legendImage is None:

            self.legendImage = QtGui.QImage(self.legendWidth, 95,
                                            QtGui.QImage.Format_RGB32)
            self.legendImage.setDotsPerMeterX(dpi_to_meters(self.dpi))
            self.legendImage.setDotsPerMeterY(dpi_to_meters(self.dpi))

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
            myImage.setDotsPerMeterX(dpi_to_meters(self.dpi))
            myImage.setDotsPerMeterY(dpi_to_meters(self.dpi))
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
