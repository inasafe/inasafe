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

import logging

from PyQt4 import QtCore, QtGui, QtXml
from qgis.core import (
    QgsComposition,
    QgsRectangle)
from safe_qgis.safe_interface import temp_dir, unique_filename, get_version
from safe_qgis.exceptions import KeywordNotFoundError, ReportCreationError
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    setup_printer,
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
        self.extent = iface.mapCanvas().extent()
        self.logo = ':/plugins/inasafe/bnpb_logo.png'
        self.template = ':/plugins/inasafe/inasafe.qpt'
        self.page_width = 0  # width in mm
        self.page_height = 0  # height in mm
        self.page_dpi = 300.0
        self.show_frames = False  # intended for debugging use only

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
        """Set image that will be used as logo in reports.

        :param logo: Path to image file
        :type logo: str
        """
        self.logo = logo

    def set_template(self, template):
        """Set template that will be used for report generation.

        :param template: Path to composer template
        :type template: str
        """
        self.template = template

    def set_extent(self, extent):
        """Set extent or the report map

        :param extent: Extent of the report map
        :type extent: QgsRectangle

        """
        self.extent = extent

    def setup_composition(self):
        """Set up the composition ready for drawing elements onto it."""
        LOGGER.debug('InaSAFE Map setupComposition called')
        canvas = self.iface.mapCanvas()
        renderer = canvas.mapRenderer()
        self.composition = QgsComposition(renderer)
        self.composition.setPlotStyle(QgsComposition.Print)  # or preview
        self.composition.setPrintResolution(self.page_dpi)
        self.composition.setPrintAsRaster(True)

    def render(self):
        """Render the map composition to an image and save that to disk.

        :returns: A three-tuple of:
            * str: image_path - absolute path to png of rendered map
            * QImage: image - in memory copy of rendered map
            * QRectF: target_area - dimensions of rendered map
        :rtype: tuple
        """
        LOGGER.debug('InaSAFE Map renderComposition called')
        # NOTE: we ignore self.composition.printAsRaster() and always rasterize
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

    def load_template(self):
        """Load a QgsComposer map from a template.
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
        if date_time is None:
            date = ''
            time = ''
        else:
            tokens = date_time.split('_')
            date = tokens[0]
            time = tokens[1]
        long_version = get_version()
        tokens = long_version.split('.')
        version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])

        title = self.map_title()
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
        if image is not None:
            image.setPictureFile(self.logo)
        else:
            raise ReportCreationError(self.tr(
                'Image "safe-logo" could not be found'))

        # Get the main map canvas on the composition and set
        # its extents to the event.
        composer_map = self.composition.getComposerItemById('impact-map')
        if composer_map is not None:
            # Recenter the composer map on the center of the extent
            # Note that since the composer map is square and the canvas may be
            # arbitrarily shaped, we center based on the longest edge
            canvas_extent = self.extent
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
            composer_map.setNewExtent(square_extent)

            # calculate intervals for grid
            split_count = 5
            x_interval = square_extent.width() / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = square_extent.height() / split_count
            composer_map.setGridIntervalY(y_interval)
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

        # remove from legend all layers, except impact one
        model = legend.model()
        impact_item = model.findItems(self.layer.name())[0]
        row = impact_item.index().row()
        model.removeRows(row + 1, model.rowCount() - row)
        if row > 0:
            model.removeRows(0, row)
