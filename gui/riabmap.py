"""
Disaster risk assessment tool developed by AusAid -
  **RIAB map making module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from qgis.core import (QgsComposition,
                       QgsComposerMap,
                       QgsComposerLabel,
                       QgsComposerPicture,
                       QgsMapLayer)
from riabexceptions import LegendLayerException
from PyQt4 import QtCore, QtGui
from impactcalculator import getKeywordFromFile
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class RiabMap():
    """A class for creating a map."""
    def __init__(self, theIface):
        """Constructor for the RiabMap class.
        Args:
            theIface - reference to the QGIS iface object
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.iface = theIface
        self.layer = theIface.activeLayer()
        self.legend = None
        # how high each row of the legend should be
        self.legendIncrement = 40

    def tr(self, theString):
        """We implement this ourself since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QtCore.QCoreApplication.translate('RiabMap', theString)

    def setImpactLayer(self, theLayer):
        """Mutator for the impact layer that will be used for stats,
        legend and reporting.
        Args:
            theLayer - a valid QgsMapLayer
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.layer = theLayer

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
        #settrace()
        if self.layer is None:
            myMessage = self.tr('Unable to make a legend when map generator '
                                'has no layer set.')
            raise LegendLayerException(myMessage)
        try:
            getKeywordFromFile(str(self.layer.source()), 'caption')
        except Exception, e:
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
        return self.legend

    def getVectorLegend(self):
        """
        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        if not self.layer.isUsingRendererV2():
            myMessage = self.tr('A legend can only be generated for '
                                'vector layers that use the "new symbology" '
                                'implementation in QGIS.')
            raise LegendLayerException(myMessage)
        # new symbology - subclass of QgsFeatureRendererV2 class
        self.legend = None
        myRenderer = self.layer.rendererV2()
        myType = myRenderer.type()
        if myType == "singleSymbol":
            mySymbol = myRenderer.symbol()
            self.addSymbolToLegend(theLabel=self.layer.name(),
                                   theSymbol=mySymbol)
        elif myType == "categorizedSymbol":
            for myCategory in myRenderer.categories():
                mySymbol = myCategory.symbol()
                self.addSymbolToLegend(
                                myCategory=myCategory.value().toString(),
                                theLabel=myCategory.label(),
                                theSymbol=mySymbol)
        elif myType == "graduatedSymbol":
            for myRange in myRenderer.ranges():
                mySymbol = myRange.symbol()
                self.addSymbolToLegend(theMin=myRange.lowerValue(),
                                       theMax=myRange.upperValue(),
                                       theLabel=myRange.label(),
                                       theSymbol=mySymbol)
        else:
            #type unknown
            myMessage = self.tr('Unrecognised renderer type found for the '
                                'impact layer. Please use one of these: '
                                'single symbol, categorised symbol or '
                                'graduated symbol and then try again.')
            raise LegendLayerException(myMessage)

    def getRasterLegend(self):
        """
        Args:
            None
        Returns:
            None
        Raises:
            An InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        assert False

    def addSymbolToLegend(self,
                         theSymbol,
                         theMin=None,
                         theMax=None,
                         theCategory=None,
                         theLabel=None):
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
        myColour = theSymbol.color()
        self.addClassToLegend(myColour,
                              theMin=theMin,
                              theMax=theMax,
                              theLabel=theLabel)

    def addClassToLegend(self,
                         theColour,
                         theMin=None,
                         theMax=None,
                         theCategory=None,
                         theLabel=None):
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
        self.extendLegend()
        myOffset = self.legend.height() - self.legendIncrement
        myPainter = QtGui.QPainter(self.legend)
        myBrush = QtGui.QBrush(theColour)
        myPainter.setBrush(myBrush)
        myPainter.drawRect(QtCore.QRectF(10, myOffset + 10, 20, 20))
        myPainter.setPen(QtGui.QColor(0, 0, 0))
        myPainter.drawText(40, myOffset + 25, theLabel)

    def extendLegend(self):
        """Grow the legend pixmap enough to accommodate one more legend entry.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        if self.legend is None:
            self.legend = QtGui.QPixmap(300, 40)
            self.legend.fill(QtGui.QColor(255, 255, 255))
        else:
            # extend the existing legend down for the next class
            myPixmap = QtGui.QPixmap(300, self.legend.height() +
                                          self.legendIncrement)
            myPixmap.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myPixmap)

            myRect = QtCore.QRectF(0, 0,
                                   self.legend.width(),
                                   self.legend.height())
            myPainter.drawPixmap(myRect, self.legend, myRect)
            self.legend = myPixmap

    def makePdf(self, theFilename):
        """Method to createa  nice little pdf map.

        Args:
            theFilename - a string containing a filename path with .pdf
            extension
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myPageWidth = 210  # width in mm
        myPageHeight = 297  # height in mm
        myDpi = 150.0
        myMargin = 10  # margin in mm
        myBuffer = 1  # vertical spacing between elements
        myRenderer = self.iface.mapCanvas().mapRenderer()
        myComposition = QgsComposition(myRenderer)
        myComposition.setPlotStyle(QgsComposition.Print)
        myComposition.setPaperSize(myPageWidth, myPageHeight)
        myComposition.setPrintResolution(myDpi)
        #
        # Create a printer device (we are 'printing' to a pdf
        #
        myPrinter = QtGui.QPrinter()
        myPrinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
        myPrinter.setOutputFileName(theFilename)
        myPrinter.setPaperSize(QtCore.QSizeF(myPageWidth,
                                             myPageHeight),
                                             QtGui.QPrinter.Millimeter)
        myPrinter.setFullPage(True)
        myPrinter.setColorMode(QtGui.QPrinter.Color)
        myResolution = myComposition.printResolution()
        myPrinter.setResolution(myResolution)
        #
        # Add a map to the composition
        #
        # make a square map where width = height = page width
        myMapHeight = myPageWidth - (myMargin * 2)
        myTopOffset = myMargin
        myComposerMap = QgsComposerMap(myComposition,
                                       myMargin,
                                       myTopOffset,
                                       myMapHeight,
                                       myMapHeight)
        myComposition.addItem(myComposerMap)
        #
        # Update the top offset for the next horizontal row of items
        #
        myTopOffset = myMargin + myMapHeight + myBuffer
        #
        # Add the heading
        #
        myFontSize = 24
        myFontWeight = 1
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(myComposition)
        myLabel.setFont(myFont)
        myHeading = self.tr('Risk in a Box')
        myLabel.setText(myHeading)
        myLabel.adjustSizeToText()
        myLabelHeight = 13
        myLabel.setItemPosition(myMargin,
                                myTopOffset,
                                myMapHeight,  # height is == width for the map
                                myLabelHeight,
                                )
        myLabel.setFrame(True)
        myComposition.addItem(myLabel)
        #
        # Update the top offset for the next horizontal row of items
        #
        myTopOffset = myMargin + myMapHeight + myLabelHeight + myBuffer + 2
        #
        # Add a picture - legend
        # .. note:: getLegend generates a pixmap in 150dpi so if you set
        #    the map to a higher dpi it will appear undersized
        #
        myPicture1 = QgsComposerPicture(myComposition)
        self.getLegend()
        myLegendFile = '/tmp/legend.png'
        self.legend.save(myLegendFile, 'PNG')
        myPicture1.setPictureFile(myLegendFile)
        myLegendHeight = self.pointsToMM(self.legend.height(), myDpi)
        myLegendWidth = self.pointsToMM(self.legend.width(), myDpi)
        myPicture1.setItemPosition(myMargin,
                                   myTopOffset,
                                   myLegendWidth,
                                   myLegendHeight)
        myPicture1.setFrame(False)
        myComposition.addItem(myPicture1)
        #
        # Add a picture - riab logo on right
        #
        myPicture2 = QgsComposerPicture(myComposition)
        myPicture2.setPictureFile(':/plugins/riab/icon.png')
        myPicture2.setItemPosition(myPageWidth - myMargin - 30,
                                   myTopOffset,
                                   30,
                                   30)
        myPicture2.setFrame(False)
        myComposition.addItem(myPicture2)
        #
        # Update the top offset for the next horizontal row of items
        #
        myTopOffset = myMargin + myMapHeight + myBuffer
        #
        # Draw the legend
        #

        #
        # Render the composition to our pdf printer
        #
        myPainter = QtGui.QPainter(myPrinter)
        myPaperRectMM = myPrinter.pageRect(QtGui.QPrinter.Millimeter)
        myPaperRectPx = myPrinter.pageRect(QtGui.QPrinter.DevicePixel)
        myComposition.render(myPainter, myPaperRectPx, myPaperRectMM)
        myPainter.end()

    def pointsToMM(self, thePoints, theDpi):
        """Convert measurement in points to one in mm
        Args:
            thePoints - distance in pixels
            theDpi - dots per inch for conversion
        Returns:
            mm converted value
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myMM = (float(thePoints) / theDpi) * 25.4
        return myMM
