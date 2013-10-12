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
from safe_qgis.exceptions import KeywordNotFoundError, ReportCreationError
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
        self.keyword_io = KeywordIO()
        self.printer = None
        self.composition = None
        self.legend = None
        self.logo = ':/plugins/inasafe/bnpb_logo.png'
        self.template = ':/plugins/inasafe/inasafe.qpt'
        #self.page_width = 210  # width in mm
        #self.page_height = 297  # height in mm
        self.page_width = 0  # width in mm
        self.page_height = 0  # height in mm
        self.page_dpi = 300.0
        #self.page_margin = 10  # margin in mm
        self.show_frames = False  # intended for debugging use only
        self.page_margin = None
        #vertical spacing between elements
        self.vertical_spacing = None
        self.map_height = None
        self.mapWidth = None
        # make a square map where width = height = page width
        #self.map_height = self.page_width - (self.page_margin * 2)
        #self.mapWidth = self.map_height
        #self.disclaimer = self.tr('InaSAFE has been jointly developed by'
        #                          ' BNPB, AusAid & the World Bank')

    @staticmethod
    def tr(string):
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

    def set_logo(self, logo):
        """

        :param logo: Path to image that will be used as logo in report
        :type logo: str
        """
        self.logo = logo

    def set_template(self, template):
        """

        :param template: Path to composer template that will be used for report
        :type template: str
        """
        self.template = template

    def setup_composition(self):
        """Set up the composition ready for drawing elements onto it."""
        LOGGER.debug('InaSAFE Map setupComposition called')
        canvas = self.iface.mapCanvas()
        renderer = canvas.mapRenderer()
        self.composition = QgsComposition(renderer)
        self.composition.setPlotStyle(QgsComposition.Print)  # or preview
        #self.composition.setPaperSize(self.page_width, self.page_height)
        self.composition.setPrintResolution(self.page_dpi)
        self.composition.setPrintAsRaster(True)

    def compose_map(self):
        """Place all elements on the map ready for printing."""
        self.setup_composition()
        # Keep track of our vertical positioning as we work our way down
        # the page placing elements on it.
        top_offset = self.page_margin
        self.draw_logo(top_offset)
        label_height = self.draw_title(top_offset)
        # Update the map offset for the next row of content
        top_offset += label_height + self.vertical_spacing
        composer_map = self.draw_map(top_offset)
        self.draw_scalebar(composer_map, top_offset)
        # Update the top offset for the next horizontal row of items
        top_offset += self.map_height + self.vertical_spacing - 1
        impact_title_height = self.draw_impact_title(top_offset)
        # Update the top offset for the next horizontal row of items
        if impact_title_height:
            top_offset += impact_title_height + self.vertical_spacing + 2
        self.draw_legend(top_offset)
        self.draw_host_and_time(top_offset)
        self.draw_disclaimer()

    def render(self):
        """Render the map composition to an image and save that to disk.

        :returns: A three-tuple of:
            * str: image_path - absolute path to png of rendered map
            * QImage: image - in memory copy of rendered map
            * QRectF: target_area - dimensions of rendered map
        :rtype: tuple
        """
        LOGGER.debug('InaSAFE Map renderComposition called')
        # NOTE: we ignore self.composition.printAsRaster() and always rasterise
        width = int(self.page_dpi * self.page_width / 25.4)
        height = int(self.page_dpi * self.page_height / 25.4)
        image = QtGui.QImage(
            QtCore.QSize(width, height),
            QtGui.QImage.Format_ARGB32)
        image.setDotsPerMeterX(dpi_to_meters(self.page_dpi))
        image.setDotsPerMeterY(dpi_to_meters(self.page_dpi))

        # Only works in Qt4.8
        #image.fill(QtGui.qRgb(255, 255, 255))
        # Works in older Qt4 versions
        image.fill(55 + 255 * 256 + 255 * 256 * 256)
        image_painter = QtGui.QPainter(image)
        source_area = QtCore.QRectF(
            0, 0, self.page_width,
            self.page_height)
        target_area = QtCore.QRectF(0, 0, width, height)
        self.composition.render(image_painter, target_area, source_area)
        image_painter.end()
        image_path = unique_filename(
            prefix='mapRender_',
            suffix='.png',
            dir=temp_dir())
        image.save(image_path)
        return image_path, image, target_area

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
            map_pdf_path = unique_filename(
                prefix='report', suffix='.pdf', dir=temp_dir())
        else:
            # We need to cast to python string in case we receive a QString
            map_pdf_path = str(filename)

        self.load_template()

        resolution = self.composition.printResolution()
        self.printer = setup_printer(map_pdf_path, resolution=resolution)
        _, image, rectangle = self.render()
        painter = QtGui.QPainter(self.printer)
        painter.drawImage(rectangle, image, rectangle)
        painter.end()
        return map_pdf_path

    def draw_logo(self, top_offset):
        """Add a picture containing the logo to the map top left corner

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        logo = QgsComposerPicture(self.composition)
        logo.setPictureFile(':/plugins/inasafe/bnpb_logo.png')
        logo.setItemPosition(self.page_margin, top_offset, 10, 10)
        logo.setFrameEnabled(self.show_frames)
        logo.setZValue(1)  # To ensure it overlays graticule markers
        self.composition.addItem(logo)

    def draw_title(self, top_offset):
        """Add a title to the composition.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The height of the label as rendered.
        :rtype: float
        """
        LOGGER.debug('InaSAFE Map drawTitle called')
        font_size = 14
        font_weight = QtGui.QFont.Bold
        italics_flag = False
        font = QtGui.QFont(
            'verdana',
            font_size,
            font_weight,
            italics_flag)
        label = QgsComposerLabel(self.composition)
        label.setFont(font)
        heading = self.tr(
            'InaSAFE - Indonesia Scenario Assessment for Emergencies')
        label.setText(heading)
        label.adjustSizeToText()
        label_height = 10.0  # determined using qgis map composer
        label_width = 170.0   # item - position and size...option
        left_offset = self.page_width - self.page_margin - label_width
        label.setItemPosition(
            left_offset,
            top_offset - 2,  # -2 to push it up a little
            label_width,
            label_height)
        label.setFrameEnabled(self.show_frames)
        self.composition.addItem(label)
        return label_height

    def draw_map(self, top_offset):
        """Add a map to the composition and return the composer map instance.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The composer map.
        :rtype: QgsComposerMap
        """
        LOGGER.debug('InaSAFE Map drawMap called')
        map_width = self.mapWidth
        composer_map = QgsComposerMap(
            self.composition,
            self.page_margin,
            top_offset,
            map_width,
            self.map_height)
        #myExtent = self.iface.mapCanvas().extent()
        # The dimensions of the map canvas and the print composer map may
        # differ. So we set the map composer extent using the canvas and
        # then defer to the map canvas's map extents thereafter
        # Update: disabled as it results in a rectangular rather than
        # square map
        #composer_map.setNewExtent(myExtent)
        composer_extent = composer_map.extent()
        # Recenter the composer map on the center of the canvas
        # Note that since the composer map is square and the canvas may be
        # arbitrarily shaped, we center based on the longest edge
        canvas_extent = self.iface.mapCanvas().extent()
        width = canvas_extent.width()
        height = canvas_extent.height()
        longest_length = width
        if width < height:
            longest_length = height
        half_length = longest_length / 2
        center = canvas_extent.center()
        min_x = center.x() - half_length
        max_x = center.x() + half_length
        min_y = center.y() - half_length
        max_y = center.y() + half_length
        square_extent = QgsRectangle(min_x, min_y, max_x, max_y)
        composer_map.setNewExtent(square_extent)

        composer_map.setGridEnabled(True)
        split_count = 5
        # .. todo:: Write logic to adjust precision so that adjacent tick marks
        #    always have different displayed values
        precision = 2
        x_interval = composer_extent.width() / split_count
        composer_map.setGridIntervalX(x_interval)
        y_interval = composer_extent.height() / split_count
        composer_map.setGridIntervalY(y_interval)
        composer_map.setGridStyle(QgsComposerMap.Cross)
        cross_length_mm = 1
        composer_map.setCrossLength(cross_length_mm)
        composer_map.setZValue(0)  # To ensure it does not overlay logo
        font_size = 6
        font_weight = QtGui.QFont.Normal
        italics_flag = False
        font = QtGui.QFont(
            'verdana',
            font_size,
            font_weight,
            italics_flag)
        composer_map.setGridAnnotationFont(font)
        composer_map.setGridAnnotationPrecision(precision)
        composer_map.setShowGridAnnotation(True)
        composer_map.setGridAnnotationDirection(
            QgsComposerMap.BoundaryDirection, QgsComposerMap.Top)
        self.composition.addItem(composer_map)
        self.draw_graticule_mask(top_offset)
        return composer_map

    def draw_graticule_mask(self, top_offset):
        """A helper function to mask out graticule labels.

         It will hide labels on the right side by over painting a white
         rectangle with white border on them. **kludge**

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawGraticuleMask called')
        left_offset = self.page_margin + self.mapWidth
        rect = QgsComposerShape(
            left_offset + 0.5,
            top_offset,
            self.page_width - left_offset,
            self.map_height + 1,
            self.composition)

        rect.setShapeType(QgsComposerShape.Rectangle)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(0, 0, 0))
        pen.setWidthF(0.1)
        rect.setPen(pen)
        rect.setBackgroundColor(QtGui.QColor(255, 255, 255))
        rect.setTransparency(100)
        #rect.setLineWidth(0.1)
        #rect.setFrameEnabled(False)
        #rect.setOutlineColor(QtGui.QColor(255, 255, 255))
        #rect.setFillColor(QtGui.QColor(255, 255, 255))
        #rect.setOpacity(100)
        # These two lines seem superfluous but are needed
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        rect.setBrush(brush)
        self.composition.addItem(rect)

    def draw_native_scalebar(self, composer_map, top_offset):
        """Draw a scale bar using QGIS' native drawing.

        In the case of geographic maps, scale will be in degrees, not km.

        :param composer_map: Composer map on which to draw the scalebar.
        :type composer_map: QgsComposerMap

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawNativeScaleBar called')
        scale_bar = QgsComposerScaleBar(self.composition)
        scale_bar.setStyle('Numeric')  # optionally modify the style
        scale_bar.setComposerMap(composer_map)
        scale_bar.applyDefaultSize()
        scale_bar_height = scale_bar.boundingRect().height()
        scale_bar_width = scale_bar.boundingRect().width()
        # -1 to avoid overlapping the map border
        scale_bar.setItemPosition(
            self.page_margin + 1,
            top_offset + self.map_height - (scale_bar_height * 2),
            scale_bar_width,
            scale_bar_height)
        scale_bar.setFrameEnabled(self.show_frames)
        # Disabled for now
        #self.composition.addItem(scale_bar)

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
        canvas = self.iface.mapCanvas()
        renderer = canvas.mapRenderer()
        #
        # Add a linear map scale
        #
        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(renderer.destinationCrs().srsid())
        distance_area.setEllipsoidalMode(True)
        # Determine how wide our map is in km/m
        # Starting point at BL corner
        composer_extent = composer_map.extent()
        start_point = QgsPoint(
            composer_extent.xMinimum(),
            composer_extent.yMinimum())
        # Ending point at BR corner
        end_point = QgsPoint(
            composer_extent.xMaximum(),
            composer_extent.yMinimum())
        ground_distance = distance_area.measureLine(start_point, end_point)
        # Get the equivalent map distance per page mm
        map_width = self.mapWidth
        # How far is 1mm on map on the ground in meters?
        mm_to_ground = ground_distance / map_width
        #print 'MM:', myMMDistance
        # How long we want the scale bar to be in relation to the map
        scalebar_to_map_ratio = 0.5
        # How many divisions the scale bar should have
        tick_count = 5
        scale_bar_width_mm = map_width * scalebar_to_map_ratio
        print_segment_width_mm = scale_bar_width_mm / tick_count
        # Segment width in real world (m)
        # We apply some logic here so that segments are displayed in meters
        # if each segment is less that 1000m otherwise km. Also the segment
        # lengths are rounded down to human looking numbers e.g. 1km not 1.1km
        units = ''
        ground_segment_width = print_segment_width_mm * mm_to_ground
        if ground_segment_width < 1000:
            units = 'm'
            ground_segment_width = round(ground_segment_width)
            # adjust the segment width now to account for rounding
            print_segment_width_mm = ground_segment_width / mm_to_ground
        else:
            units = 'km'
            # Segment with in real world (km)
            ground_segment_width = round(ground_segment_width / 1000)
            print_segment_width_mm = (
                (ground_segment_width * 1000) / mm_to_ground)
        # Now adjust the scalebar width to account for rounding
        scale_bar_width_mm = tick_count * print_segment_width_mm

        #print "SBWMM:", scale_bar_width_mm
        #print "SWMM:", print_segment_width_mm
        #print "SWM:", myGroundSegmentWidthM
        #print "SWKM:", myGroundSegmentWidthKM
        # start drawing in line segments
        scalebar_height = 5  # mm
        line_width = 0.3  # mm
        inset_distance = 7  # how much to inset the scalebar into the map by
        scalebar_x = self.page_margin + inset_distance
        scalebar_y = (
            top_offset + self.map_height - inset_distance -
            scalebar_height)  # mm

        # Draw an outer background box - shamelessly hardcoded buffer
        rectangle = QgsComposerShape(
            scalebar_x - 4,  # left edge
            scalebar_y - 3,  # top edge
            scale_bar_width_mm + 13,  # right edge
            scalebar_height + 6,  # bottom edge
            self.composition)

        rectangle.setShapeType(QgsComposerShape.Rectangle)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(255, 255, 255))
        pen.setWidthF(line_width)
        rectangle.setPen(pen)
        #rectangle.setLineWidth(line_width)
        rectangle.setFrameEnabled(False)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        # workaround for missing setTransparentFill missing from python api
        rectangle.setBrush(brush)
        self.composition.addItem(rectangle)
        # Set up the tick label font
        font_weight = QtGui.QFont.Normal
        font_size = 6
        italics_flag = False
        font = QtGui.QFont(
            'verdana',
            font_size,
            font_weight,
            italics_flag)
        # Draw the bottom line
        up_shift = 0.3  # shift the bottom line up for better rendering
        rectangle = QgsComposerShape(
            scalebar_x,
            scalebar_y + scalebar_height - up_shift,
            scale_bar_width_mm,
            0.1,
            self.composition)

        rectangle.setShapeType(QgsComposerShape.Rectangle)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(255, 255, 255))
        pen.setWidthF(line_width)
        rectangle.setPen(pen)
        #rectangle.setLineWidth(line_width)
        rectangle.setFrameEnabled(False)
        self.composition.addItem(rectangle)

        # Now draw the scalebar ticks
        for tick_counter in range(0, tick_count + 1):
            distance_suffix = ''
            if tick_counter == tick_count:
                distance_suffix = ' ' + units
            real_world_distance = (
                '%.0f%s' %
                (tick_counter *
                ground_segment_width,
                distance_suffix))
            #print 'RW:', myRealWorldDistance
            mm_offset = scalebar_x + (
                tick_counter * print_segment_width_mm)
            #print 'MM:', mm_offset
            tick_height = scalebar_height / 2
            # Lines are not exposed by the api yet so we
            # bodge drawing lines using rectangles with 1px height or width
            tick_width = 0.1  # width or rectangle to be drawn
            uptick_line = QgsComposerShape(
                mm_offset,
                scalebar_y + scalebar_height - tick_height,
                tick_width,
                tick_height,
                self.composition)

            uptick_line.setShapeType(QgsComposerShape.Rectangle)
            pen = QtGui.QPen()
            pen.setWidthF(line_width)
            uptick_line.setPen(pen)
            #uptick_line.setLineWidth(line_width)
            uptick_line.setFrameEnabled(False)
            self.composition.addItem(uptick_line)
            #
            # Add a tick label
            #
            label = QgsComposerLabel(self.composition)
            label.setFont(font)
            label.setText(real_world_distance)
            label.adjustSizeToText()
            label.setItemPosition(
                mm_offset - 3,
                scalebar_y - tick_height)
            label.setFrameEnabled(self.show_frames)
            self.composition.addItem(label)

    def draw_impact_title(self, top_offset):
        """Draw the map subtitle - obtained from the impact layer keywords.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int

        :returns: The height of the label as rendered.
        :rtype: float
        """
        LOGGER.debug('InaSAFE Map drawImpactTitle called')
        title = self.map_title()
        if title is None:
            title = ''
        font_size = 20
        font_weight = QtGui.QFont.Bold
        italics_flag = False
        font = QtGui.QFont(
            'verdana', font_size, font_weight, italics_flag)
        label = QgsComposerLabel(self.composition)
        label.setFont(font)
        heading = title
        label.setText(heading)
        label_width = self.page_width - (self.page_margin * 2)
        label_height = 12
        label.setItemPosition(
            self.page_margin, top_offset, label_width, label_height)
        label.setFrameEnabled(self.show_frames)
        self.composition.addItem(label)
        return label_height

    def draw_legend(self, top_offset):
        """Add a legend to the map using our custom legend renderer.

        .. note:: getLegend generates a pixmap in 150dpi so if you set
           the map to a higher dpi it will appear undersized.

        :param top_offset: Vertical offset at which the logo should be drawn.
        :type top_offset: int
        """
        LOGGER.debug('InaSAFE Map drawLegend called')
        legend_attributes = self.map_legend_attributes()
        legend_notes = legend_attributes.get('legend_notes', None)
        legend_units = legend_attributes.get('legend_units', None)
        legend_title = legend_attributes.get('legend_title', None)
        LOGGER.debug(legend_attributes)
        legend = MapLegend(
            self.layer,
            self.page_dpi,
            legend_title,
            legend_notes,
            legend_units)
        self.legend = legend.get_legend()
        picture1 = QgsComposerPicture(self.composition)
        legend_file_path = unique_filename(
            prefix='legend', suffix='.png', dir='work')
        self.legend.save(legend_file_path, 'PNG')
        picture1.setPictureFile(legend_file_path)
        legend_height = points_to_mm(self.legend.height(), self.page_dpi)
        legend_width = points_to_mm(self.legend.width(), self.page_dpi)
        picture1.setItemPosition(
            self.page_margin,
            top_offset,
            legend_width,
            legend_height)
        picture1.setFrameEnabled(False)
        self.composition.addItem(picture1)
        os.remove(legend_file_path)

    def draw_image(self, image, width_mm, left_offset, top_offset):
        """Helper to draw an image directly onto the QGraphicsScene.
        This is an alternative to using QgsComposerPicture which in
        some cases leaves artifacts under windows.

        The Pixmap will have a transform applied to it so that
        it is rendered with the same resolution as the composition.

        :param image: Image that will be rendered to the layout.
        :type image: QImage

        :param width_mm: Desired width in mm of output on page.
        :type width_mm: int

        :param left_offset: Offset from left of page.
        :type left_offset: int

        :param top_offset: Offset from top of page.
        :type top_offset: int

        :returns: Graphics scene item.
        :rtype: QGraphicsSceneItem
        """
        LOGGER.debug('InaSAFE Map drawImage called')
        desired_width_mm = width_mm  # mm
        desired_width_px = mm_to_points(desired_width_mm, self.page_dpi)
        actual_width_px = image.width()
        scale_factor = desired_width_px / actual_width_px

        LOGGER.debug('%s %s %s' % (
            scale_factor, actual_width_px, desired_width_px))
        transform = QtGui.QTransform()
        transform.scale(scale_factor, scale_factor)
        transform.rotate(0.5)
        # noinspection PyArgumentList
        item = self.composition.addPixmap(QtGui.QPixmap.fromImage(image))
        item.setTransform(transform)
        item.setOffset(
            left_offset / scale_factor, top_offset / scale_factor)
        return item

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
        #myUser = self.keyword_io.readKeywords(self.layer, 'user')
        #myHost = self.keyword_io.readKeywords(self.layer, 'host_name')
        date_time = self.keyword_io.read_keywords(self.layer, 'time_stamp')
        tokens = date_time.split('_')
        date = tokens[0]
        time = tokens[1]
        #myElapsedTime = self.keyword_io.readKeywords(self.layer,
        #                                            'elapsed_time')
        #myElapsedTime = humaniseSeconds(myElapsedTime)
        long_version = get_version()
        tokens = long_version.split('.')
        version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])
        label_text = self.tr(
            'Date and time of assessment: %s %s\n'
            'Special note: This assessment is a guide - we strongly recommend '
            'that you ground truth the results shown here before deploying '
            'resources and / or personnel.\n'
            'Assessment carried out using InaSAFE release %s (QGIS '
            'plugin version).') % (date, time, version)
        font_size = 6
        font_weight = QtGui.QFont.Normal
        italics_flag = True
        font = QtGui.QFont(
            'verdana',
            font_size,
            font_weight,
            italics_flag)
        label = QgsComposerLabel(self.composition)
        label.setFont(font)
        label.setText(label_text)
        label.adjustSizeToText()
        label_height = 50.0  # mm determined using qgis map composer
        label_width = (self.page_width / 2) - self.page_margin
        left_offset = self.page_width / 2  # put in right half of page
        label.setItemPosition(
            left_offset,
            top_offset,
            label_width,
            label_height,)
        label.setFrameEnabled(self.show_frames)
        self.composition.addItem(label)

    def draw_disclaimer(self):
        """Add a disclaimer to the composition."""
        LOGGER.debug('InaSAFE Map drawDisclaimer called')
        font_size = 10
        font_weight = QtGui.QFont.Normal
        italics_flag = True
        font = QtGui.QFont(
            'verdana',
            font_size,
            font_weight,
            italics_flag)
        label = QgsComposerLabel(self.composition)
        label.setFont(font)
        label.setText(self.disclaimer)
        label.adjustSizeToText()
        label_height = 7.0  # mm determined using qgis map composer
        label_width = self.page_width   # item - position and size...option
        left_offset = self.page_margin
        top_offset = self.page_height - self.page_margin
        label.setItemPosition(
            left_offset,
            top_offset,
            label_width,
            label_height,)
        label.setFrameEnabled(self.show_frames)
        self.composition.addItem(label)

    def map_title(self):
        """Get the map title from the layer keywords if possible.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        LOGGER.debug('InaSAFE Map getMapTitle called')
        try:
            title = self.keyword_io.read_keywords(self.layer, 'map_title')
            return title
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
        legend_attribute_list = [
            'legend_notes',
            'legend_units',
            'legend_title']
        legend_attribute_dict = {}
        for myLegendAttribute in legend_attribute_list:
            try:
                legend_attribute_dict[myLegendAttribute] = \
                    self.keyword_io.read_keywords(
                        self.layer, myLegendAttribute)
            except KeywordNotFoundError:
                pass
            except Exception:
                pass
        return legend_attribute_dict

    def show_composer(self):
        """Show the composition in a composer view so the user can tweak it.
        """
        view = QgsComposerView(self.iface.mainWindow())
        view.show()

    def write_template(self, template_path):
        """Write current composition as a template that can be re-used in QGIS.

        :param template_path: Path to which template should be written.
        :type template_path: str
        """
        document = QtXml.QDomDocument()
        element = document.createElement('Composer')
        document.appendChild(element)
        self.composition.writeXML(element, document)
        xml = document.toByteArray()
        template_file = file(template_path, 'wb')
        template_file.write(xml)
        template_file.close()

    def load_template(self):
        """Load a QgsComposer map from a template and render it.

        .. note:: THIS METHOD IS EXPERIMENTAL
        """
        self.setup_composition()

        template_file = QtCore.QFile(self.template)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        template_file.close()

        document = QtXml.QDomDocument()
        document.setContent(template_content)

        # get information for substitutions
        # date, time and plugin version
        date_time = self.keyword_io.read_keywords(self.layer, 'time_stamp')
        tokens = date_time.split('_')
        date = tokens[0]
        time = tokens[1]
        long_version = get_version()
        tokens = long_version.split('.')
        version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])

        # map title
        LOGGER.debug('InaSAFE Map getMapTitle called')
        try:
            title = self.keyword_io.read_keywords(self.layer, 'map_title')
        except KeywordNotFoundError:
            title = None
        except Exception:
            title = None

        if not title:
            title = ''

        substitution_map = {
            'impact-title': title,
            'date': date,
            'time': time,
            'safe-version': version
        }
        LOGGER.debug(substitution_map)
        load_ok = self.composition.loadFromTemplate(document,
                                                    substitution_map)
        if not load_ok:
            raise ReportCreationError(
                self.tr('Error loading template %s') %
                self.template)

        self.page_width = self.composition.paperWidth()
        self.page_height = self.composition.paperHeight()

        # set logo
        image = self.composition.getComposerItemById('safe-logo')
        image.setPictureFile(self.logo)

        # Get the main map canvas on the composition and set
        # its extents to the event.
        map = self.composition.getComposerItemById('impact-map')
        if map is not None:
            # Recenter the composer map on the center of the canvas
            # Note that since the composer map is square and the canvas may be
            # arbitrarily shaped, we center based on the longest edge
            canvas_extent = self.iface.mapCanvas().extent()
            width = canvas_extent.width()
            height = canvas_extent.height()
            longest_width = width
            if width < height:
                longest_width = height
            half_length = longest_width / 2
            center = canvas_extent.center()
            min_x = center.x() - half_length
            max_x = center.x() + half_length
            min_y = center.y() - half_length
            max_y = center.y() + half_length
            square_extent = QgsRectangle(min_x, min_y, max_x, max_y)
            map.setNewExtent(square_extent)

            # calculate intervals for grid
            split_count = 5
            x_interval = square_extent.width() / split_count
            map.setGridIntervalX(x_interval)
            y_interval = square_extent.height() / split_count
            map.setGridIntervalY(y_interval)
        else:
            raise ReportCreationError(self.tr(
                'Map "impact-map" could not be found'))

        legend = self.composition.getComposerItemById('impact-legend')
        legend_attributes = self.map_legend_attributes()
        LOGGER.debug(legend_attributes)
        #legend_notes = mapLegendAttributes.get('legend_notes', None)
        #legend_units = mapLegendAttributes.get('legend_units', None)
        legend_title = legend_attributes.get('legend_title', None)
        if legend_title is None:
            legend_title = ""
        legend.setTitle(legend_title)
        legend.updateLegend()
