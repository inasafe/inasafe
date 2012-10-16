"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **InaSAFE map making module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging

from PyQt4 import QtCore, QtGui, QtXml
from qgis.core import (QgsComposition,
                       QgsComposerMap,
                       QgsComposerLabel,
                       QgsComposerPicture,
                       QgsComposerScaleBar,
                       QgsComposerShape,
                       QgsDistanceArea,
                       QgsPoint,
                       QgsRectangle)
from qgis.gui import QgsComposerView
from safe_qgis.safe_interface import temp_dir, unique_filename, get_version
from safe_qgis.exceptions import KeywordNotFoundException
from safe_qgis.keyword_io import KeywordIO
from safe_qgis.map_legend import MapLegend
from safe_qgis.utilities import (setupPrinter,
                                 pointsToMM,
                                 mmToPoints,
                                 humaniseSeconds)
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import safe_qgis.resources     # pylint: disable=W0611
LOGGER = logging.getLogger('InaSAFE')


class Map():
    """A class for creating a map."""
    def __init__(self, theIface):
        """Constructor for the Map class.

        Args:
            theIface - reference to the QGIS iface object
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map class initialised')
        self.iface = theIface
        self.layer = theIface.activeLayer()
        self.keywordIO = KeywordIO()
        self.printer = None
        self.composition = None
        self.legend = None
        self.pageWidth = 210  # width in mm
        self.pageHeight = 297  # height in mm
        self.pageDpi = 300.0
        self.pageMargin = 10  # margin in mm
        self.verticalSpacing = 1  # vertical spacing between elements
        self.showFramesFlag = False  # intended for debugging use only
        # make a square map where width = height = page width
        self.mapHeight = self.pageWidth - (self.pageMargin * 2)
        self.mapWidth = self.mapHeight
        self.disclaimer = self.tr('InaSAFE has been jointly developed by'
                                  ' BNPB, AusAid & the World Bank')

    def tr(self, theString):
        """We implement this since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QtCore.QCoreApplication.translate('Map', theString)

    def setImpactLayer(self, theLayer):
        """Mutator for the impact layer that will be used for stats,
        legend and reporting.

        Args:
            theLayer - a valid QgsMapLayer
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        self.layer = theLayer

    def setupComposition(self):
        """Set up the composition ready for drawing elements onto it.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map setupComposition called')
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        self.composition = QgsComposition(myRenderer)
        self.composition.setPlotStyle(QgsComposition.Print)  # or preview
        self.composition.setPaperSize(self.pageWidth, self.pageHeight)
        self.composition.setPrintResolution(self.pageDpi)
        self.composition.setPrintAsRaster(True)

    def composeMap(self):
        """Place all elements on the map ready for printing.

        Args:
            None

        Returns:
            None

        Raises:
            Any exceptions raised will be propagated.
        """
        self.setupComposition()
        # Keep track of our vertical positioning as we work our way down
        # the page placing elements on it.
        myTopOffset = self.pageMargin
        self.drawLogo(myTopOffset)
        myLabelHeight = self.drawTitle(myTopOffset)
        # Update the map offset for the next row of content
        myTopOffset += myLabelHeight + self.verticalSpacing
        myComposerMap = self.drawMap(myTopOffset)
        self.drawScaleBar(myComposerMap, myTopOffset)
        # Update the top offset for the next horizontal row of items
        myTopOffset += self.mapHeight + self.verticalSpacing - 1
        myImpactTitleHeight = self.drawImpactTitle(myTopOffset)
        # Update the top offset for the next horizontal row of items
        if myImpactTitleHeight:
            myTopOffset += myImpactTitleHeight + self.verticalSpacing + 2
        self.drawLegend(myTopOffset)
        self.drawHostAndTime(myTopOffset)
        self.drawDisclaimer()

    def renderComposition(self):
        """Render the map composition to an image and save that to disk.

        Args:
            None

        Returns:
            tuple:
                * str: myImagePath - absolute path to png of rendered map
                * QImage: myImage - in memory copy of rendered map
                * QRectF: myTargetArea - dimensions of rendered map
            str: Absolute file system path to the rendered image.

        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map renderComposition called')
        # NOTE: we ignore self.composition.printAsRaster() and always rasterise
        myWidth = (int)(self.pageDpi * self.pageWidth / 25.4)
        myHeight = (int)(self.pageDpi * self.pageHeight / 25.4)
        myImage = QtGui.QImage(QtCore.QSize(myWidth, myHeight),
                               QtGui.QImage.Format_ARGB32)
        myImage.setDotsPerMeterX(self.pageDpi / 25.4 * 1000)
        myImage.setDotsPerMeterY(self.pageDpi / 25.4 * 1000)
        myImage.fill(0)
        myImagePainter = QtGui.QPainter(myImage)
        mySourceArea = QtCore.QRectF(0, 0, self.pageWidth,
                                     self.pageHeight)
        myTargetArea = QtCore.QRectF(0, 0, myWidth, myHeight)
        self.composition.render(myImagePainter, myTargetArea, mySourceArea)
        myImagePainter.end()
        myImagePath = unique_filename(prefix='mapRender_',
                                      suffix='.png',
                                      dir=temp_dir())
        myImage.save(myImagePath)
        return myImagePath, myImage, myTargetArea

    def printToPdf(self, theFilename):
        """Generate the printout for our final map.

        Args:
            theFilename: str - optional path on the file system to which the
                pdf should be saved. If None, a generated file name will be
                used.
        Returns:
            str: file name of the output file (equivalent to theFilename if
                provided).
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map printToPdf called')
        if theFilename is None:
            myMapPdfPath = unique_filename(prefix='report',
                                     suffix='.pdf',
                                     dir=temp_dir('work'))
        else:
            # We need to cast to python string in case we receive a QString
            myMapPdfPath = str(theFilename)

        self.composeMap()
        self.printer = setupPrinter(myMapPdfPath)
        _, myImage, myRectangle = self.renderComposition()
        myPainter = QtGui.QPainter(self.printer)
        myPainter.drawImage(myRectangle, myImage, myRectangle)
        myPainter.end()
        return myMapPdfPath

    def drawLogo(self, theTopOffset):
        """Add a picture containing the logo to the map top left corner

        Args:
            theTopOffset - vertical offset at which the logo shoudl be drawn
        Returns:
            None
        Raises:
            None
        """
        myLogo = QgsComposerPicture(self.composition)
        myLogo.setPictureFile(':/plugins/inasafe/bnpb_logo.png')
        myLogo.setItemPosition(self.pageMargin,
                                   theTopOffset,
                                   10,
                                   10)
        myLogo.setFrame(self.showFramesFlag)
        myLogo.setZValue(1)  # To ensure it overlays graticule markers
        self.composition.addItem(myLogo)

    def drawTitle(self, theTopOffset):
        """Add a title to the composition.

        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            float - the height of the label as rendered
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawTitle called')
        myFontSize = 14
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myHeading = self.tr('InaSAFE - Indonesia Scenario Assessment'
                            ' for Emergencies')
        myLabel.setText(myHeading)
        myLabel.adjustSizeToText()
        myLabelHeight = 10.0  # determined using qgis map composer
        myLabelWidth = 170.0   # item - position and size...option
        myLeftOffset = self.pageWidth - self.pageMargin - myLabelWidth
        myLabel.setItemPosition(myLeftOffset,
                                theTopOffset - 2,  # -2 to push it up a little
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)
        return myLabelHeight

    def drawMap(self, theTopOffset):
        """Add a map to the composition and return the compsermap instance.

        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            A QgsComposerMap instance is returned
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawMap called')
        myMapWidth = self.mapWidth
        myComposerMap = QgsComposerMap(self.composition,
                                       self.pageMargin,
                                       theTopOffset,
                                       myMapWidth,
                                       self.mapHeight)
        #myExtent = self.iface.mapCanvas().extent()
        # The dimensions of the map canvas and the print compser map may
        # differ. So we set the map composer extent using the canvas and
        # then defer to the map canvas's map extents thereafter
        # Update: disabled as it results in a rectangular rather than
        # square map
        #myComposerMap.setNewExtent(myExtent)
        myComposerExtent = myComposerMap.extent()
        # Recenter the composer map on the center of the canvas
        # Note that since the composer map is square and the canvas may be
        # arbitrarily shaped, we center based on the longest edge
        myCanvasExtent = self.iface.mapCanvas().extent()
        myWidth = myCanvasExtent.width()
        myHeight = myCanvasExtent.height()
        myLongestLength = myWidth
        if myWidth < myHeight:
            myLongestLength = myHeight
        myHalfLength = myLongestLength / 2
        myCenter = myCanvasExtent.center()
        myMinX = myCenter.x() - myHalfLength
        myMaxX = myCenter.x() + myHalfLength
        myMinY = myCenter.y() - myHalfLength
        myMaxY = myCenter.y() + myHalfLength
        mySquareExtent = QgsRectangle(myMinX, myMinY, myMaxX, myMaxY)
        myComposerMap.setNewExtent(mySquareExtent)

        myComposerMap.setGridEnabled(True)
        myNumberOfSplits = 5
        # .. todo:: Write logic to adjust preciosn so that adjacent tick marks
        #    always have different displayed values
        myPrecision = 2
        myXInterval = myComposerExtent.width() / myNumberOfSplits
        myComposerMap.setGridIntervalX(myXInterval)
        myYInterval = myComposerExtent.height() / myNumberOfSplits
        myComposerMap.setGridIntervalY(myYInterval)
        myComposerMap.setGridStyle(QgsComposerMap.Cross)
        myCrossLengthMM = 1
        myComposerMap.setCrossLength(myCrossLengthMM)
        myComposerMap.setZValue(0)  # To ensure it does not overlay logo
        myFontSize = 6
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myComposerMap.setGridAnnotationFont(myFont)
        myComposerMap.setGridAnnotationPrecision(myPrecision)
        myComposerMap.setShowGridAnnotation(True)
        myComposerMap.setGridAnnotationDirection(
                                        QgsComposerMap.BoundaryDirection)
        self.composition.addItem(myComposerMap)
        self.drawGraticuleMask(theTopOffset)
        return myComposerMap

    def drawGraticuleMask(self, theTopOffset):
        """A helper function to mask out graticule labels on the right side
           by over painting a white rectangle with white border on them.

        Args:
            theTopOffset - vertical offset at which the map should be drawn
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawGraticuleMask called')
        myLeftOffset = self.pageMargin + self.mapWidth
        myRect = QgsComposerShape(myLeftOffset + 0.5,
                                  theTopOffset,
                                  self.pageWidth - myLeftOffset,
                                  self.mapHeight + 1,
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myRect.setLineWidth(0.1)
        myRect.setFrame(False)
        myRect.setOutlineColor(QtGui.QColor(255, 255, 255))
        myRect.setFillColor(QtGui.QColor(255, 255, 255))
        myRect.setOpacity(100)
        # These two lines seem superfluous but are needed
        myBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        myRect.setBrush(myBrush)
        self.composition.addItem(myRect)

    def drawNativeScaleBar(self, theComposerMap, theTopOffset):
        """Draw a scale bar using QGIS' native drawing - in the case of
        geographic maps, scale will be in degrees, not km.

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map drawNativeScaleBar called')
        myScaleBar = QgsComposerScaleBar(self.composition)
        myScaleBar.setStyle('Numeric')  # optionally modify the style
        myScaleBar.setComposerMap(theComposerMap)
        myScaleBar.applyDefaultSize()
        myScaleBarHeight = myScaleBar.boundingRect().height()
        myScaleBarWidth = myScaleBar.boundingRect().width()
        # -1 to avoid overlapping the map border
        myScaleBar.setItemPosition(self.pageMargin + 1,
                                   theTopOffset + self.mapHeight -
                                     (myScaleBarHeight * 2),
                                   myScaleBarWidth,
                                   myScaleBarHeight)
        myScaleBar.setFrame(self.showFramesFlag)
        # Disabled for now
        #self.composition.addItem(myScaleBar)

    def drawScaleBar(self, theComposerMap, theTopOffset):
        """Add a numeric scale to the bottom left of the map

        We draw the scale bar manually because QGIS does not yet support
        rendering a scalebar for a geographic map in km.

        .. seealso:: :meth:`drawNativeScaleBar`

        Args:
            * theComposerMap - QgsComposerMap instance used as the basis
              scale calculations.
            * theTopOffset - vertical offset at which the map should be drawn
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map drawScaleBar called')
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        #
        # Add a linear map scale
        #
        myDistanceArea = QgsDistanceArea()
        myDistanceArea.setSourceCrs(myRenderer.destinationCrs().srsid())
        myDistanceArea.setProjectionsEnabled(True)
        # Determine how wide our map is in km/m
        # Starting point at BL corner
        myComposerExtent = theComposerMap.extent()
        myStartPoint = QgsPoint(myComposerExtent.xMinimum(),
                                myComposerExtent.yMinimum())
        # Ending point at BR corner
        myEndPoint = QgsPoint(myComposerExtent.xMaximum(),
                              myComposerExtent.yMinimum())
        myGroundDistance = myDistanceArea.measureLine(myStartPoint, myEndPoint)
        # Get the equivalent map distance per page mm
        myMapWidth = self.mapWidth
        # How far is 1mm on map on the ground in meters?
        myMMToGroundDistance = myGroundDistance / myMapWidth
        #print 'MM:', myMMDistance
        # How long we want the scale bar to be in relation to the map
        myScaleBarToMapRatio = 0.5
        # How many divisions the scale bar should have
        myTickCount = 5
        myScaleBarWidthMM = myMapWidth * myScaleBarToMapRatio
        myPrintSegmentWidthMM = myScaleBarWidthMM / myTickCount
        # Segment width in real world (m)
        # We apply some logic here so that segments are displayed in meters
        # if each segment is less that 1000m otherwise km. Also the segment
        # lengths are rounded down to human looking numbers e.g. 1km not 1.1km
        myUnits = ''
        myGroundSegmentWidth = myPrintSegmentWidthMM * myMMToGroundDistance
        if myGroundSegmentWidth < 1000:
            myUnits = 'm'
            myGroundSegmentWidth = round(myGroundSegmentWidth)
            # adjust the segment width now to account for rounding
            myPrintSegmentWidthMM = myGroundSegmentWidth / myMMToGroundDistance
        else:
            myUnits = 'km'
            # Segment with in real world (km)
            myGroundSegmentWidth = round(myGroundSegmentWidth / 1000)
            myPrintSegmentWidthMM = ((myGroundSegmentWidth * 1000) /
                                    myMMToGroundDistance)
        # Now adjust the scalebar width to account for rounding
        myScaleBarWidthMM = myTickCount * myPrintSegmentWidthMM

        #print "SBWMM:", myScaleBarWidthMM
        #print "SWMM:", myPrintSegmentWidthMM
        #print "SWM:", myGroundSegmentWidthM
        #print "SWKM:", myGroundSegmentWidthKM
        # start drawing in line segments
        myScaleBarHeight = 5  # mm
        myLineWidth = 0.3  # mm
        myInsetDistance = 7  # how much to inset the scalebar into the map by
        myScaleBarX = self.pageMargin + myInsetDistance
        myScaleBarY = (theTopOffset + self.mapHeight -
                      myInsetDistance - myScaleBarHeight)  # mm

        # Draw an outer background box - shamelessly hardcoded buffer
        myRect = QgsComposerShape(myScaleBarX - 4,  # left edge
                                  myScaleBarY - 3,  # top edge
                                  myScaleBarWidthMM + 13,  # right edge
                                  myScaleBarHeight + 6,  # bottom edge
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myRect.setLineWidth(myLineWidth)
        myRect.setFrame(False)
        myBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        # workaround for missing setTransparentFill missing from python api
        myRect.setBrush(myBrush)
        self.composition.addItem(myRect)
        # Set up the tick label font
        myFontWeight = QtGui.QFont.Normal
        myFontSize = 6
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        # Draw the bottom line
        myUpshift = 0.3  # shift the bottom line up for better rendering
        myRect = QgsComposerShape(myScaleBarX,
                                  myScaleBarY + myScaleBarHeight - myUpshift,
                                  myScaleBarWidthMM,
                                  0.1,
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myRect.setLineWidth(myLineWidth)
        myRect.setFrame(False)
        self.composition.addItem(myRect)

        # Now draw the scalebar ticks
        for myTickCountIterator in range(0, myTickCount + 1):
            myDistanceSuffix = ''
            if myTickCountIterator == myTickCount:
                myDistanceSuffix = ' ' + myUnits
            myRealWorldDistance = ('%.0f%s' %
                                   (myTickCountIterator *
                                    myGroundSegmentWidth,
                                    myDistanceSuffix))
            #print 'RW:', myRealWorldDistance
            myMMOffset = myScaleBarX + (myTickCountIterator *
                                        myPrintSegmentWidthMM)
            #print 'MM:', myMMOffset
            myTickHeight = myScaleBarHeight / 2
            # Lines are not exposed by the api yet so we
            # bodge drawing lines using rectangles with 1px height or width
            myTickWidth = 0.1  # width or rectangle to be drawn
            myUpTickLine = QgsComposerShape(myMMOffset,
                                myScaleBarY + myScaleBarHeight - myTickHeight,
                                myTickWidth,
                                myTickHeight,
                                self.composition)

            myUpTickLine.setShapeType(QgsComposerShape.Rectangle)
            myUpTickLine.setLineWidth(myLineWidth)
            myUpTickLine.setFrame(False)
            self.composition.addItem(myUpTickLine)
            #
            # Add a tick label
            #
            myLabel = QgsComposerLabel(self.composition)
            myLabel.setFont(myFont)
            myLabel.setText(myRealWorldDistance)
            myLabel.adjustSizeToText()
            myLabel.setItemPosition(myMMOffset - 3,
                                myScaleBarY - myTickHeight)
            myLabel.setFrame(self.showFramesFlag)
            self.composition.addItem(myLabel)

    def drawImpactTitle(self, theTopOffset):
        """Draw the map subtitle - obtained from the impact layer keywords.

        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            float - the height of the label as rendered
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawImpactTitle called')
        myTitle = self.getMapTitle()
        if myTitle is None:
            myTitle = ''
        myFontSize = 20
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                         myFontSize,
                         myFontWeight,
                         myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myHeading = myTitle
        myLabel.setText(myHeading)
        myLabelWidth = self.pageWidth - (self.pageMargin * 2)
        myLabelHeight = 12
        myLabel.setItemPosition(self.pageMargin,
                            theTopOffset,
                            myLabelWidth,
                            myLabelHeight,
                            )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)
        return myLabelHeight

    def drawLegend(self, theTopOffset):
        """Add a legend to the map using our custom legend renderer.

        .. note:: getLegend generates a pixmap in 150dpi so if you set
           the map to a higher dpi it will appear undersized.

        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawLegend called')
        myLegend = MapLegend(self.layer)
        self.legend = myLegend.getLegend()
        myPicture1 = QgsComposerPicture(self.composition)
        myLegendFile = os.path.join(temp_dir(), 'legend.png')
        self.legend.save(myLegendFile, 'PNG')
        myPicture1.setPictureFile(myLegendFile)
        myLegendHeight = pointsToMM(self.legend.height(), self.pageDpi)
        myLegendWidth = pointsToMM(self.legend.width(), self.pageDpi)
        myPicture1.setItemPosition(self.pageMargin,
                                   theTopOffset,
                                   myLegendWidth,
                                   myLegendHeight)
        myPicture1.setFrame(False)
        self.composition.addItem(myPicture1)
        os.remove(myLegendFile)

    def drawPixmap(self, thePixmap, theWidthMM, theLeftOffset, theTopOffset):
        """Helper to draw a pixmap directly onto the QGraphicsScene.
        This is an alternative to using QgsComposerPicture which in
        some cases leaves artifacts under windows.

        The Pixmap will have a transform applied to it so that
        it is rendered with the same resolution as the composition.

        Args:

            * thePixmap
            * theWidthMM - desired width in mm of output on page
            * theLeftOffset
            * theTopOffset

        Returns:
            QGraphicsSceneItem is returned
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawPixmap called')
        myDesiredWidthMM = theWidthMM  # mm
        myDesiredWidthPX = mmToPoints(myDesiredWidthMM, self.pageDpi)
        myActualWidthPX = thePixmap.width()
        myScaleFactor = myDesiredWidthPX / myActualWidthPX

        LOGGER.debug('%s %s %s' % (
            myScaleFactor, myActualWidthPX, myDesiredWidthPX))
        myTransform = QtGui.QTransform()
        myTransform.scale(myScaleFactor, myScaleFactor)
        myTransform.rotate(0.5)
        myItem = self.composition.addPixmap(thePixmap)
        myItem.setTransform(myTransform)
        myItem.setOffset(theLeftOffset / myScaleFactor,
                         theTopOffset / myScaleFactor)
        return myItem

    def drawHostAndTime(self, theTopOffset):
        """Add a disclaimer to the composition.

        Args:
            theTopOffset - vertical offset at which to begin drawing
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawDisclaimer called')
        #elapsed_time: 11.612545
        #user: timlinux
        #host_name: ultrabook
        #time_stamp: 2012-10-13_23:10:31
        myUser = self.keywordIO.readKeywords(self.layer, 'user')
        myHost = self.keywordIO.readKeywords(self.layer, 'host_name')
        myDateTime = self.keywordIO.readKeywords(self.layer, 'time_stamp')
        myTokens = myDateTime.split('_')
        myDate = myTokens[0]
        myTime = myTokens[1]
        myElapsedTime = self.keywordIO.readKeywords(self.layer, 'elapsed_time')
        myElapsedTime = humaniseSeconds(myElapsedTime)
        myLongVersion = get_version()
        myTokens = myLongVersion.split('.')
        myVersion = '%s.%s.%s' % (myTokens[0], myTokens[1], myTokens[2])
        myLabelText = self.tr('Assessment carried out on host "%s"'
                         'by user "%s" using InaSAFE release %s (QGIS '
                         'plugin version).\n'
                         'Date and time of assessment: %s %s\n'
                         'Elapsed time for assessment calculation: %s\n'
                         'Special note: This assessment is a guide - we '
                         'strongly recommend that you ground truth the '
                         'results shown here before deploying resources '
                         'and / or personnel.' % (
                         myHost,
                         myUser,
                         myVersion,
                         myDate,
                         myTime,
                         myElapsedTime))
        myFontSize = 8
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = True
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myLabel.setText(myLabelText)
        myLabel.adjustSizeToText()
        myLabelHeight = 50.0  # mm determined using qgis map composer
        myLabelWidth = (self.pageWidth / 2) - self.pageMargin
        myLeftOffset = self.pageWidth / 2  # put in right half of page
        myLabel.setItemPosition(myLeftOffset,
                                theTopOffset,
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)

    def drawDisclaimer(self):
        """Add a disclaimer to the composition.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        LOGGER.debug('InaSAFE Map drawDisclaimer called')
        myFontSize = 10
        myFontWeight = QtGui.QFont.Normal
        myItalicsFlag = True
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myLabel.setText(self.disclaimer)
        myLabel.adjustSizeToText()
        myLabelHeight = 7.0  # mm determined using qgis map composer
        myLabelWidth = self.pageWidth   # item - position and size...option
        myLeftOffset = self.pageMargin
        myTopOffset = self.pageHeight - self.pageMargin
        myLabel.setItemPosition(myLeftOffset,
                                myTopOffset,
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrame(self.showFramesFlag)
        self.composition.addItem(myLabel)

    def getMapTitle(self):
        """Get the map title from the layer keywords if possible.

        Args:
            None
        Returns:
            None on error, otherwise the title
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map getMapTitle called')
        try:
            myTitle = self.keywordIO.readKeywords(self.layer, 'map_title')
            return myTitle
        except KeywordNotFoundException:
            return None
        except Exception:
            return None

    def showComposer(self):
        """Show the composition in a composer view so the user can tweak it
        if they want to.

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myView = QgsComposerView(self.iface.mainWindow())
        myView.show()

    def writeTemplate(self, theTemplateFilePath):
        """Write the current composition as a template that can be
        re-used in QGIS."""
        myDocument = QtXml.QDomDocument()
        myElement = myDocument.createElement('Composer')
        myDocument.appendChild(myElement)
        self.composition.writeXML(myElement, myDocument)
        myXml = myDocument.toByteArray()
        myFile = file(theTemplateFilePath, 'wb')
        myFile.write(myXml)
        myFile.close()

    def renderTemplate(self, theTemplateFilePath, theOutputFilePath):
        """Load a QgsComposer map from a template and render it

        .. note:: THIS METHOD IS EXPERIMENTAL AND CURRENTLY NON FUNCTIONAL

        Args:
            theTemplateFilePath - path to the template that should be loaded.
            theOutputFilePath - path for the output pdf
        Returns:
            None
        Raises:
            None
        """
        self.setupComposition()

        myResolution = self.composition.printResolution()
        self.printer = setupPrinter(theOutputFilePath,
                                    theResolution=myResolution)
        if self.composition:
            myFile = QtCore.QFile(theTemplateFilePath)
            myDocument = QtXml.QDomDocument()
            myDocument.setContent(myFile, False)  # .. todo:: fix magic param
            myNodeList = myDocument.elementsByTagName('Composer')
            if myNodeList.size() > 0:
                myElement = myNodeList.at(0).toElement()
                self.composition.readXML(myElement, myDocument)
        self.printToPdf(theOutputFilePath)
