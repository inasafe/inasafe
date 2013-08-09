# coding=utf-8
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
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import logging

from PyQt4 import QtCore, QtGui, QtXml
from qgis.core import (
    QgsComposition,
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
from safe_qgis.exceptions import KeywordNotFoundError
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.report.map_legend import MapLegend
from safe_qgis.utilities.utilities import (
    setup_printer,
    points_to_mm,
    mm_to_points,
    dpi_to_meters)

# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
LOGGER = logging.getLogger('InaSAFE')


class Map():
    """A class for creating a map."""
    def __init__(self, iface):
        """Constructor for the Map class.

        :param iface: Reference to the QGIS iface object.
        :type iface: QgsAppInterface
        """
        LOGGER.debug('InaSAFE Map class initialised')
        self.iface = iface
        self.layer = iface.activeLayer()
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

    def tr(self, string):
        """We implement this since we do not inherit QObject.

        :param string: String for translation.
        :type string: QString, str

        :returns: Translated version of theString.
        :rtype: QString
        """
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        return QtCore.QCoreApplication.translate('Map', string)

    def set_impact_layer(self, layer):
        """Set the layer that will be used for stats, legend and reporting.

        :param layer: Layer that will be used for stats, legend and reporting.
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer
        """
        self.layer = layer

    def setup_composition(self):
        """Set up the composition ready for drawing elements onto it."""
        LOGGER.debug('InaSAFE Map setupComposition called')
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        self.composition = QgsComposition(myRenderer)
        self.composition.setPlotStyle(QgsComposition.Print)  # or preview
        self.composition.setPaperSize(self.pageWidth, self.pageHeight)
        self.composition.setPrintResolution(self.pageDpi)
        self.composition.setPrintAsRaster(True)

    def compose_map(self):
        """Place all elements on the map ready for printing."""
        self.setup_composition()
        # Keep track of our vertical positioning as we work our way down
        # the page placing elements on it.
        myTopOffset = self.pageMargin
        self.draw_logo(myTopOffset)
        myLabelHeight = self.draw_title(myTopOffset)
        # Update the map offset for the next row of content
        myTopOffset += myLabelHeight + self.verticalSpacing
        myComposerMap = self.draw_map(myTopOffset)
        self.draw_scalebar(myComposerMap, myTopOffset)
        # Update the top offset for the next horizontal row of items
        myTopOffset += self.mapHeight + self.verticalSpacing - 1
        myImpactTitleHeight = self.draw_impact_title(myTopOffset)
        # Update the top offset for the next horizontal row of items
        if myImpactTitleHeight:
            myTopOffset += myImpactTitleHeight + self.verticalSpacing + 2
        self.draw_legend(myTopOffset)
        self.draw_host_and_time(myTopOffset)
        self.draw_disclaimer()

    def render(self):
        """Render the map composition to an image and save that to disk.

        :returns: A three-tuple of:
            * str: myImagePath - absolute path to png of rendered map
            * QImage: myImage - in memory copy of rendered map
            * QRectF: myTargetArea - dimensions of rendered map
        :rtype: tuple
        """
        LOGGER.debug('InaSAFE Map renderComposition called')
        # NOTE: we ignore self.composition.printAsRaster() and always rasterise
        myWidth = int(self.pageDpi * self.pageWidth / 25.4)
        myHeight = int(self.pageDpi * self.pageHeight / 25.4)
        myImage = QtGui.QImage(QtCore.QSize(myWidth, myHeight),
                               QtGui.QImage.Format_ARGB32)
        myImage.setDotsPerMeterX(dpi_to_meters(self.pageDpi))
        myImage.setDotsPerMeterY(dpi_to_meters(self.pageDpi))

        # Only works in Qt4.8
        #myImage.fill(QtGui.qRgb(255, 255, 255))
        # Works in older Qt4 versions
        myImage.fill(55 + 255 * 256 + 255 * 256 * 256)
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

    def make_pdf(self, filename):
        """Generate the printout for our final map.

        :param filename: Path on the file system to which the pdf should be
            saved. If None, a generated file name will be used.
        :type filename: str

        :returns: File name of the output file (equivalent to filename if
                provided).
        :rtype: str
        """
        LOGGER.debug('InaSAFE Map printToPdf called')
        if filename is None:
            myMapPdfPath = unique_filename(
                prefix='report', suffix='.pdf', dir=temp_dir('work'))
        else:
            # We need to cast to python string in case we receive a QString
            myMapPdfPath = str(filename)

        self.compose_map()
        self.printer = setup_printer(myMapPdfPath)
        _, myImage, myRectangle = self.render()
        myPainter = QtGui.QPainter(self.printer)
        myPainter.drawImage(myRectangle, myImage, myRectangle)
        myPainter.end()
        return myMapPdfPath

    def draw_logo(self, top_offset):
        """Add a picture containing the logo to the map top left corner

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        myLogo = QgsComposerPicture(self.composition)
        myLogo.setPictureFile(':/plugins/inasafe/bnpb_logo.png')
        myLogo.setItemPosition(self.pageMargin, top_offset, 10, 10)
        myLogo.setFrameEnabled(self.showFramesFlag)
        myLogo.setZValue(1)  # To ensure it overlays graticule markers
        self.composition.addItem(myLogo)

    def draw_title(self, top_offset):
        """Add a title to the composition.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The height of the label as rendered.
        :rtype: float
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
                                top_offset - 2,  # -2 to push it up a little
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrameEnabled(self.showFramesFlag)
        self.composition.addItem(myLabel)
        return myLabelHeight

    def draw_map(self, top_offset):
        """Add a map to the composition and return the composer map instance.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The composer map.
        :rtype: QgsComposerMap
        """
        LOGGER.debug('InaSAFE Map drawMap called')
        myMapWidth = self.mapWidth
        myComposerMap = QgsComposerMap(
            self.composition,
            self.pageMargin,
            top_offset,
            myMapWidth,
            self.mapHeight)
        #myExtent = self.iface.mapCanvas().extent()
        # The dimensions of the map canvas and the print composer map may
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
        # .. todo:: Write logic to adjust precision so that adjacent tick marks
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
        myFont = QtGui.QFont(
            'verdana',
            myFontSize,
            myFontWeight,
            myItalicsFlag)
        myComposerMap.setGridAnnotationFont(myFont)
        myComposerMap.setGridAnnotationPrecision(myPrecision)
        myComposerMap.setShowGridAnnotation(True)
        myComposerMap.setGridAnnotationDirection(
            QgsComposerMap.BoundaryDirection, QgsComposerMap.Top)
        self.composition.addItem(myComposerMap)
        self.draw_graticule_mask(top_offset)
        return myComposerMap

    def draw_graticule_mask(self, top_offset):
        """A helper function to mask out graticule labels.

         It will hide labels on the right side by over painting a white
         rectangle with white border on them. **kludge**

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawGraticuleMask called')
        myLeftOffset = self.pageMargin + self.mapWidth
        myRect = QgsComposerShape(myLeftOffset + 0.5,
                                  top_offset,
                                  self.pageWidth - myLeftOffset,
                                  self.mapHeight + 1,
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myPen = QtGui.QPen()
        myPen.setColor(QtGui.QColor(0, 0, 0))
        myPen.setWidthF(0.1)
        myRect.setPen(myPen)
        myRect.setBackgroundColor(QtGui.QColor(255, 255, 255))
        myRect.setTransparency(100)
        #myRect.setLineWidth(0.1)
        #myRect.setFrameEnabled(False)
        #myRect.setOutlineColor(QtGui.QColor(255, 255, 255))
        #myRect.setFillColor(QtGui.QColor(255, 255, 255))
        #myRect.setOpacity(100)
        # These two lines seem superfluous but are needed
        myBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        myRect.setBrush(myBrush)
        self.composition.addItem(myRect)

    def draw_native_scalebar(self, composer_map, top_offset):
        """Draw a scale bar using QGIS' native drawing.

        In the case of geographic maps, scale will be in degrees, not km.

        :param composer_map: Composer map on which to draw the scalebar.
        :type composer_map: QgsComposerMap

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawNativeScaleBar called')
        myScaleBar = QgsComposerScaleBar(self.composition)
        myScaleBar.setStyle('Numeric')  # optionally modify the style
        myScaleBar.setComposerMap(composer_map)
        myScaleBar.applyDefaultSize()
        myScaleBarHeight = myScaleBar.boundingRect().height()
        myScaleBarWidth = myScaleBar.boundingRect().width()
        # -1 to avoid overlapping the map border
        myScaleBar.setItemPosition(
            self.pageMargin + 1,
            top_offset + self.mapHeight - (myScaleBarHeight * 2),
            myScaleBarWidth,
            myScaleBarHeight)
        myScaleBar.setFrameEnabled(self.showFramesFlag)
        # Disabled for now
        #self.composition.addItem(myScaleBar)

    def draw_scalebar(self, composer_map, top_offset):
        """Add a numeric scale to the bottom left of the map.

        We draw the scale bar manually because QGIS does not yet support
        rendering a scale bar for a geographic map in km.

        .. seealso:: :meth:`drawNativeScaleBar`

        :param composer_map: Composer map on which to draw the scalebar.
        :type composer_map: QgsComposerMap

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawScaleBar called')
        myCanvas = self.iface.mapCanvas()
        myRenderer = myCanvas.mapRenderer()
        #
        # Add a linear map scale
        #
        myDistanceArea = QgsDistanceArea()
        myDistanceArea.setSourceCrs(myRenderer.destinationCrs().srsid())
        myDistanceArea.setEllipsoidalMode(True)
        # Determine how wide our map is in km/m
        # Starting point at BL corner
        myComposerExtent = composer_map.extent()
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
        myScaleBarY = (
            top_offset + self.mapHeight - myInsetDistance -
            myScaleBarHeight)  # mm

        # Draw an outer background box - shamelessly hardcoded buffer
        myRect = QgsComposerShape(myScaleBarX - 4,  # left edge
                                  myScaleBarY - 3,  # top edge
                                  myScaleBarWidthMM + 13,  # right edge
                                  myScaleBarHeight + 6,  # bottom edge
                                  self.composition)

        myRect.setShapeType(QgsComposerShape.Rectangle)
        myPen = QtGui.QPen()
        myPen.setColor(QtGui.QColor(255, 255, 255))
        myPen.setWidthF(myLineWidth)
        myRect.setPen(myPen)
        #myRect.setLineWidth(myLineWidth)
        myRect.setFrameEnabled(False)
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
        myPen = QtGui.QPen()
        myPen.setColor(QtGui.QColor(255, 255, 255))
        myPen.setWidthF(myLineWidth)
        myRect.setPen(myPen)
        #myRect.setLineWidth(myLineWidth)
        myRect.setFrameEnabled(False)
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
            myUpTickLine = QgsComposerShape(
                myMMOffset,
                myScaleBarY + myScaleBarHeight - myTickHeight,
                myTickWidth,
                myTickHeight,
                self.composition)

            myUpTickLine.setShapeType(QgsComposerShape.Rectangle)
            myPen = QtGui.QPen()
            myPen.setWidthF(myLineWidth)
            myUpTickLine.setPen(myPen)
            #myUpTickLine.setLineWidth(myLineWidth)
            myUpTickLine.setFrameEnabled(False)
            self.composition.addItem(myUpTickLine)
            #
            # Add a tick label
            #
            myLabel = QgsComposerLabel(self.composition)
            myLabel.setFont(myFont)
            myLabel.setText(myRealWorldDistance)
            myLabel.adjustSizeToText()
            myLabel.setItemPosition(
                myMMOffset - 3,
                myScaleBarY - myTickHeight)
            myLabel.setFrameEnabled(self.showFramesFlag)
            self.composition.addItem(myLabel)

    def draw_impact_title(self, top_offset):
        """Draw the map subtitle - obtained from the impact layer keywords.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The height of the label as rendered.
        :rtype: float
        """
        LOGGER.debug('InaSAFE Map drawImpactTitle called')
        myTitle = self.map_title()
        if myTitle is None:
            myTitle = ''
        myFontSize = 20
        myFontWeight = QtGui.QFont.Bold
        myItalicsFlag = False
        myFont = QtGui.QFont(
            'verdana', myFontSize, myFontWeight, myItalicsFlag)
        myLabel = QgsComposerLabel(self.composition)
        myLabel.setFont(myFont)
        myHeading = myTitle
        myLabel.setText(myHeading)
        myLabelWidth = self.pageWidth - (self.pageMargin * 2)
        myLabelHeight = 12
        myLabel.setItemPosition(
            self.pageMargin, top_offset, myLabelWidth, myLabelHeight)
        myLabel.setFrameEnabled(self.showFramesFlag)
        self.composition.addItem(myLabel)
        return myLabelHeight

    def draw_legend(self, top_offset):
        """Add a legend to the map using our custom legend renderer.

        .. note:: getLegend generates a pixmap in 150dpi so if you set
           the map to a higher dpi it will appear undersized.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawLegend called')
        mapLegendAttributes = self.map_legend_attributes()
        legendNotes = mapLegendAttributes.get('legend_notes', None)
        legendUnits = mapLegendAttributes.get('legend_units', None)
        legendTitle = mapLegendAttributes.get('legend_title', None)
        LOGGER.debug(mapLegendAttributes)
        myLegend = MapLegend(self.layer, self.pageDpi, legendTitle,
                             legendNotes, legendUnits)
        self.legend = myLegend.get_legend()
        myPicture1 = QgsComposerPicture(self.composition)
        myLegendFilePath = unique_filename(
            prefix='legend', suffix='.png', dir='work')
        self.legend.save(myLegendFilePath, 'PNG')
        myPicture1.setPictureFile(myLegendFilePath)
        myLegendHeight = points_to_mm(self.legend.height(), self.pageDpi)
        myLegendWidth = points_to_mm(self.legend.width(), self.pageDpi)
        myPicture1.setItemPosition(self.pageMargin,
                                   top_offset,
                                   myLegendWidth,
                                   myLegendHeight)
        myPicture1.setFrameEnabled(False)
        self.composition.addItem(myPicture1)
        os.remove(myLegendFilePath)

    def draw_image(self, theImage, theWidthMM, theLeftOffset, theTopOffset):
        """Helper to draw an image directly onto the QGraphicsScene.
        This is an alternative to using QgsComposerPicture which in
        some cases leaves artifacts under windows.

        The Pixmap will have a transform applied to it so that
        it is rendered with the same resolution as the composition.

        :param theImage: Image that will be rendered to the layout.
        :type theImage: QImage

        :param theWidthMM: Desired width in mm of output on page.
        :type theWidthMM: int

        :param theLeftOffset: Offset from left of page.
        :type theLeftOffset: int

        :param theTopOffset: Offset from top of page.
        :type theTopOffset: int

        :returns: Graphics scene item.
        :rtype: QGraphicsSceneItem
        """
        LOGGER.debug('InaSAFE Map drawImage called')
        myDesiredWidthMM = theWidthMM  # mm
        myDesiredWidthPX = mm_to_points(myDesiredWidthMM, self.pageDpi)
        myActualWidthPX = theImage.width()
        myScaleFactor = myDesiredWidthPX / myActualWidthPX

        LOGGER.debug('%s %s %s' % (
            myScaleFactor, myActualWidthPX, myDesiredWidthPX))
        myTransform = QtGui.QTransform()
        myTransform.scale(myScaleFactor, myScaleFactor)
        myTransform.rotate(0.5)
        # noinspection PyArgumentList
        myItem = self.composition.addPixmap(QtGui.QPixmap.fromImage(theImage))
        myItem.setTransform(myTransform)
        myItem.setOffset(theLeftOffset / myScaleFactor,
                         theTopOffset / myScaleFactor)
        return myItem

    def draw_host_and_time(self, top_offset):
        """Add a note with hostname and time to the composition.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawDisclaimer called')
        #elapsed_time: 11.612545
        #user: timlinux
        #host_name: ultrabook
        #time_stamp: 2012-10-13_23:10:31
        #myUser = self.keywordIO.readKeywords(self.layer, 'user')
        #myHost = self.keywordIO.readKeywords(self.layer, 'host_name')
        myDateTime = self.keywordIO.read_keywords(self.layer, 'time_stamp')
        myTokens = myDateTime.split('_')
        myDate = myTokens[0]
        myTime = myTokens[1]
        #myElapsedTime = self.keywordIO.readKeywords(self.layer,
        #                                            'elapsed_time')
        #myElapsedTime = humaniseSeconds(myElapsedTime)
        myLongVersion = get_version()
        myTokens = myLongVersion.split('.')
        myVersion = '%s.%s.%s' % (myTokens[0], myTokens[1], myTokens[2])
        myLabelText = self.tr(
            'Date and time of assessment: %s %s\n'
            'Special note: This assessment is a guide - we strongly recommend '
            'that you ground truth the results shown here before deploying '
            'resources and / or personnel.\n'
            'Assessment carried out using InaSAFE release %s (QGIS '
            'plugin version).') % (myDate, myTime, myVersion)
        myFontSize = 6
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
                                top_offset,
                                myLabelWidth,
                                myLabelHeight,
                                )
        myLabel.setFrameEnabled(self.showFramesFlag)
        self.composition.addItem(myLabel)

    def draw_disclaimer(self):
        """Add a disclaimer to the composition."""
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
        myLabel.setFrameEnabled(self.showFramesFlag)
        self.composition.addItem(myLabel)

    def map_title(self):
        """Get the map title from the layer keywords if possible.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        LOGGER.debug('InaSAFE Map getMapTitle called')
        try:
            myTitle = self.keywordIO.read_keywords(self.layer, 'map_title')
            return myTitle
        except KeywordNotFoundError:
            return None
        except Exception:
            return None

    def map_legend_attributes(self):
        """Get the map legend attribute from the layer keywords if possible.

        :returns: None on error, otherwise the attributes (notes and units).
        :rtype: None, str
        """
        LOGGER.debug('InaSAFE Map getMapLegendAtributes called')
        legendAttributes = ['legend_notes',
                            'legend_units',
                            'legend_title']
        dictLegendAttributes = {}
        for myLegendAttribute in legendAttributes:
            try:
                dictLegendAttributes[myLegendAttribute] = \
                    self.keywordIO.read_keywords(self.layer, myLegendAttribute)
            except KeywordNotFoundError:
                pass
            except Exception:
                pass
        return dictLegendAttributes

    def showComposer(self):
        """Show the composition in a composer view so the user can tweak it.
        """
        myView = QgsComposerView(self.iface.mainWindow())
        myView.show()

    def write_template(self, template_path):
        """Write current composition as a template that can be re-used in QGIS.

        :param template_path: Path to which template should be written.
        :type template_path: str
        """
        myDocument = QtXml.QDomDocument()
        myElement = myDocument.createElement('Composer')
        myDocument.appendChild(myElement)
        self.composition.writeXML(myElement, myDocument)
        myXml = myDocument.toByteArray()
        myFile = file(template_path, 'wb')
        myFile.write(myXml)
        myFile.close()

    def render_template(self, template_path, output_path):
        """Load a QgsComposer map from a template and render it.

        .. note:: THIS METHOD IS EXPERIMENTAL AND CURRENTLY NON FUNCTIONAL

        :param template_path:  Path to the template that should be loaded.
        :type template_path: str

        :param output_path: Path for the output pdf.
        :type output_path: str
        """
        self.setup_composition()

        myResolution = self.composition.printResolution()
        self.printer = setup_printer(
            output_path, resolution=myResolution)
        if self.composition:
            myFile = QtCore.QFile(template_path)
            myDocument = QtXml.QDomDocument()
            myDocument.setContent(myFile, False)  # .. todo:: fix magic param
            myNodeList = myDocument.elementsByTagName('Composer')
            if myNodeList.size() > 0:
                myElement = myNodeList.at(0).toElement()
                self.composition.readXML(myElement, myDocument)
        self.make_pdf(output_path)
