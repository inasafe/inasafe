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
                       QgsComposerScaleBar,
                       QgsMapLayer)
import utilities
from riabexceptions import LegendLayerException
from PyQt4 import QtCore, QtGui, QtWebKit
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
        self.header = None
        self.footer = None
        # how high each row of the legend should be
        self.legendIncrement = 30

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
            getKeywordFromFile(str(self.layer.source()), 'impact_summary')
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
        myShader = self.layer.rasterShader().rasterShaderFunction()
        myRampItems = myShader.colorRampItemList()
        myLastValue = 0  # Making an assumption here...
        print 'Source: %s' % self.layer.source()
        for myItem in myRampItems:
            myValue = myItem.value
            myLabel = myItem.label
            myColor = myItem.color
            print 'Value: %s Label %s' % (myValue, myLabel)
            self.addClassToLegend(myColor,
                      theMin=myLastValue,
                      theMax=myValue,
                      theLabel=myLabel)
            myLastValue = myValue

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
        myPainter.setPen(theColour)
        myWhitespace = 0  # white space above and below each class itcon
        mySquareSize = self.legendIncrement - (myWhitespace * 2)
        myLeftIndent = 10
        myPainter.drawRect(QtCore.QRectF(myLeftIndent,
                                         myOffset + myWhitespace,
                                         mySquareSize, mySquareSize))
        myPainter.setPen(QtGui.QColor(0, 0, 0))  # outline colour
        myLabelX = myLeftIndent + mySquareSize + 10
        myPainter.drawText(myLabelX, myOffset + 25, theLabel)

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
            self.legend = QtGui.QPixmap(300, 80)
            self.legend.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(self.legend)
            myFontSize = 12
            myFontWeight = QtGui.QFont.Bold
            myItalicsFlag = False
            myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
            myPainter.setFont(myFont)
            myPainter.drawText(10, 25, self.tr('Legend'))
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
        myShowFrameFlag = False
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
        # Keep track of our vertical positioning as we work our way down
        # the page placing elements on it.
        #
        myTopOffset = myMargin
        #
        # Add a picture - riab logo on right
        #
        myLogo = QgsComposerPicture(myComposition)
        myLogo.setPictureFile(':/plugins/riab/bnpb_logo.png')
        myLogo.setItemPosition(myMargin,
                                   myTopOffset,
                                   10,
                                   10)
        myLogo.setFrame(myShowFrameFlag)
        myComposition.addItem(myLogo)
        #
        # Add the title
        #
        myFontSize = 14
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(myComposition)
        myLabel.setFont(myFont)
        myHeading = self.tr('S.A.F.E. - Scenario Assement For Emergencies')
        myLabel.setText(myHeading)
        myLabel.adjustSizeToText()
        myLabelHeight = 10  # determined using qgis map composer
        myLabelWidth = 131.412   # item - position and size...option
        myLabel.setItemPosition(myPageWidth - myMargin - myLabelWidth,
                                myTopOffset,
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(myShowFrameFlag)
        myComposition.addItem(myLabel)
        #
        # Update the map offset for the next row of content
        #
        myTopOffset += myLabelHeight + myBuffer
        #
        # Add a map to the composition
        #
        # make a square map where width = height = page width
        myMapHeight = myPageWidth - (myMargin * 2)
        myMapWidth = myMapHeight
        myComposerMap = QgsComposerMap(myComposition,
                                       myMargin,
                                       myTopOffset,
                                       myMapWidth,
                                       myMapHeight)
        #myExtent = self.iface.mapCanvas().extent()
        # The dimensions of the map canvas and the print compser map may
        # differ. So we set the map composer extent using the canvas and
        # then defer to the map canvas's map extents thereafter
        #myComposerMap.setNewExtent(myExtent)
        myComposerExtent = myComposerMap.extent()
        myComposerMap.setGridEnabled(True)
        myXInterval = myComposerExtent.width() / 5
        myComposerMap.setGridIntervalX(myXInterval)
        myYInterval = myComposerExtent.height() / 5
        myComposerMap.setGridIntervalY(myYInterval)
        myComposerMap.setGridStyle(QgsComposerMap.Cross)
        myFontSize = 8
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myComposerMap.setGridAnnotationFont(myFont)
        myComposerMap.setGridAnnotationPrecision(3)
        myComposerMap.setShowGridAnnotation(True)
        myComposerMap.setGridAnnotationDirection(
                                        QgsComposerMap.BoundaryDirection)
        myComposition.addItem(myComposerMap)
                #
        # Add a numeric scale to the bottom left of the map
        #
        myScaleBar = QgsComposerScaleBar(myComposition)
        myScaleBar.setStyle('Numeric')  # optionally modify the style
        myScaleBar.setComposerMap(myComposerMap)
        myScaleBar.applyDefaultSize()
        myScaleBarHeight = myScaleBar.boundingRect().height()
        myScaleBarWidth = myScaleBar.boundingRect().width()
        # -1 to avoid overlapping the map border
        myScaleBar.setItemPosition(myMargin + 1,
                                   myTopOffset + myMapHeight -
                                     myScaleBarHeight - 1,
                                   myScaleBarWidth,
                                   myScaleBarHeight)
        myScaleBar.setFrame(myShowFrameFlag)
        myComposition.addItem(myScaleBar)
        #
        # Update the top offset for the next horizontal row of items
        #
        myTopOffset += myMapHeight + myBuffer
        #
        # Add the map title
        #
        myTitle = self.getMapTitle()
        if myTitle is not None:
            myFontSize = 20
            myFontWeight = QtGui.QFont.Bold
            myItalicsFlag = False
            myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
            myLabel = QgsComposerLabel(myComposition)
            myLabel.setFont(myFont)
            myHeading = myTitle
            myLabel.setText(myHeading)
            myLabel.adjustSizeToText()
            myLabelHeight = 12
            myLabel.setItemPosition(myMargin,
                                myTopOffset,
                                myMapHeight,  # height is == width for the map
                                myLabelHeight,
                                )
            myLabel.setFrame(myShowFrameFlag)
            myComposition.addItem(myLabel)
            #
            # Update the top offset for the next horizontal row of items
            #
            myTopOffset += myLabelHeight + myBuffer + 2
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
        # Draw the table
        #
        myTable = QgsComposerPicture(myComposition)
        myImage = self.renderTable()
        if myImage is not None:
            myTableFile = '/tmp/table.png'
            myImage.save(myTableFile, 'PNG')
            myTable.setPictureFile(myTableFile)
            myScaleFactor = 1
            myTableHeight = self.pointsToMM(myImage.height(),
                                             myDpi) * myScaleFactor
            myTableWidth = self.pointsToMM(myImage.width(),
                                           myDpi) * myScaleFactor
            myTable.setItemPosition(myMargin + myMapHeight - myTableWidth,
                                       myTopOffset,
                                       myTableWidth,
                                       myTableHeight)
            myTable.setFrame(False)
            myComposition.addItem(myTable)
        #
        # Render the composition to our pdf printer
        #
        myPainter = QtGui.QPainter(myPrinter)
        myPaperRectMM = myPrinter.pageRect(QtGui.QPrinter.Millimeter)
        myPaperRectPx = myPrinter.pageRect(QtGui.QPrinter.DevicePixel)
        myComposition.render(myPainter, myPaperRectPx, myPaperRectMM)
        myPainter.end()

    def getMapTitle(self):
        """Get the map title from the layer keywords if possible
        Args:
            None
        Returns:
            None on error, otherwise the title
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        try:
            myTitle = getKeywordFromFile(str(self.layer.source()), 'map_title')
            return myTitle
        except Exception, e:
            return None

    def renderTable(self):
        """Render the table in the keywords if present. The table is an
        html table with statistics for the impact layer.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        try:
            myHtml = getKeywordFromFile(str(self.layer.source()),
                                        'impact_table')
            return self.renderHtml(myHtml)
        except Exception, e:
            return None

    def renderHtml(self, theHtml):
        """Render some HTML to a pixmap..

        Args:
            theHtml - HTML to be rendered. It is assumed that the html
            is a snippet only, containing no body element - a standard
            header and footer will be appended.
        Returns:
            A QPixmap
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myPage = QtWebKit.QWebPage()
        myFrame = myPage.mainFrame()
        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        myHeader = self.htmlHeader()
        myFooter = self.htmlFooter()
        myHtml = myHeader + theHtml + myFooter
        myFrame.setHtml(myHtml)
        #file('/tmp/report.html', 'wt').write(myHtml).close()
        #print '\n\n\nPage:\n', myFrame.toHtml()
        #mySize = QtCore.QSize(600, 200)
        mySize = myFrame.contentsSize()
        mySize.setWidth(800)
        myPage.setViewportSize(mySize)
        myQImageFlag = False
        if myQImageFlag:
            myImage = QtGui.QImage(mySize, QtGui.QImage.Format_ARGB32)
            myImage.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myImage)
            myFrame.render(myPainter)
            myPainter.end()
            return myImage
        else:  # render with qpixmap rather
            myPixmap = QtGui.QPixmap(mySize)
            myPixmap.fill(QtGui.QColor(255, 255, 255))
            myPainter = QtGui.QPainter(myPixmap)
            myFrame.render(myPainter)
            myPainter.end()
            return myPixmap

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

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            self.header = utilities.htmlHeader()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            self.footer = utilities.htmlFooter()
        return self.footer
