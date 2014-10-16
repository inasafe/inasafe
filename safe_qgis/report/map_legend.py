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

# noinspection PyPackageRequirements
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
        self.legend_image = None
        self.layer = layer
        # how high each row of the legend should be
        self.legend_increment = 42
        self.keyword_io = KeywordIO()
        self.legend_font_size = 8
        self.legend_width = 900
        self.dpi = dpi
        if legend_title is None:
            self.legend_title = self.tr('Legend')
        else:
            self.legend_title = legend_title
        self.legend_notes = legend_notes
        self.legend_units = legend_units

    # noinspection PyMethodMayBeStatic
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
            message = self.tr(
                'Unable to make a legend when map generator has no layer set.')
            raise LegendLayerError(message)
        try:
            self.keyword_io.read_keywords(self.layer, 'impact_summary')
        except KeywordNotFoundError, e:
            message = self.tr(
                'This layer does not appear to be an impact layer. Try '
                'selecting an impact layer in the QGIS layers list or '
                'creating a new impact scenario before using the print tool.'
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
        self.legend_image = None
        renderer = self.layer.rendererV2()
        renderer_type = renderer.type()
        LOGGER.debug('renderer_type' + str(renderer_type))
        if renderer_type == "singleSymbol":
            LOGGER.debug('singleSymbol')
            symbol = renderer.symbol()
            self.add_symbol(
                label=self.layer.name(),
                symbol=symbol,
                symbol_type=renderer_type)
        elif renderer_type == "categorizedSymbol":
            LOGGER.debug('categorizedSymbol')
            for myCategory in renderer.categories():
                symbol = myCategory.symbol()
                LOGGER.debug('theCategory' + myCategory.value())
                self.add_symbol(
                    category=myCategory.value(),
                    label=myCategory.label(),
                    symbol=symbol,
                    symbol_type=renderer_type)
        elif renderer_type == "graduatedSymbol":
            LOGGER.debug('graduatedSymbol')
            for myRange in renderer.ranges():
                symbol = myRange.symbol()
                self.add_symbol(
                    minimum=myRange.lowerValue(),
                    maximum=myRange.upperValue(),
                    label=myRange.label(),
                    symbol=symbol,
                    symbol_type=renderer_type)
        else:
            LOGGER.debug('else')
            # type unknown
            message = self.tr(
                'Unrecognised renderer type found for the impact layer. '
                'Please use one of these: single symbol, categorised symbol '
                'or graduated symbol and then try again.')
            raise LegendLayerError(message)
        self.add_notes()
        return self.legend_image

    def raster_legend(self):
        """Get the legend for a raster layer as an image.

        :returns: An image representing the layer's legend. self.legend is
            also populated.
        :rtype: QImage

        :Raises: InvalidLegendLayer will be raised if a legend cannot be
            created from the layer.
        """
        LOGGER.debug('InaSAFE Map Legend getRasterLegend called')
        shader = self.layer.renderer().shader().rasterShaderFunction()
        ramp_items = shader.colorRampItemList()
        last_value = 0  # Making an assumption here...
        LOGGER.debug('Source: %s' % self.layer.source())
        for ramp_item in ramp_items:
            value = ramp_item.value
            label = ramp_item.label
            color = ramp_item.color
            self.add_class(
                color,
                minimum=last_value,
                maximum=value,
                label=label,
                class_type='rasterStyle')
            last_value = value
        self.add_notes()
        return self.legend_image

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
        color = symbol.color()
        self.add_class(
            color,
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
        offset = self.legend_image.height() - self.legend_increment
        painter = QtGui.QPainter(self.legend_image)
        brush = QtGui.QBrush(colour)
        painter.setBrush(brush)
        painter.setPen(colour)
        whitespace = 2  # white space above and below each class icon
        square_size = self.legend_increment - (whitespace * 2)
        left_indent = 10
        painter.drawRect(
            QtCore.QRectF(
                left_indent, offset + whitespace, square_size, square_size))
        painter.setPen(QtGui.QColor(0, 0, 0))  # outline colour
        label_x = left_indent + square_size + 10
        font_weight = QtGui.QFont.Normal
        italics_flag = False
        font = QtGui.QFont(
            'verdana', self.legend_font_size, font_weight, italics_flag)
        font_metrics = QtGui.QFontMetricsF(font, self.legend_image)
        font_height = font_metrics.height()
        center_vertical_padding = (self.legend_increment - font_height) / 2
        extra_vertical_space = 8  # hack to get label centered on graphic
        offset += center_vertical_padding + extra_vertical_space
        painter.setFont(font)
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
                        min_string = '%i' % minimum
                    else:
                        min_string = str(minimum)
                    if float(maximum) - int(maximum) == 0.0:
                        max_string = '%i' % maximum
                    else:
                        max_string = str(maximum)
                    label += '[' + min_string + ', ' + max_string + ']'
                if float(str(minimum)) == float(str(maximum)):
                    # pass because it's not needed
                    return

        painter.drawText(label_x, offset + 25, label)

    def add_notes(self):
        """Add legend notes to the legend.
        """
        LOGGER.debug('InaSAFE Map Legend addLegendNotes called')
        if self.legend_notes is not None:
            self.grow_legend()
            offset = self.legend_image.height() - 15
            painter = QtGui.QPainter(self.legend_image)
            font_weight = QtGui.QFont.StyleNormal
            italics_flag = True
            legend_notes_font_size = self.legend_font_size / 2
            font = QtGui.QFont(
                'verdana',
                legend_notes_font_size,
                font_weight,
                italics_flag)
            painter.setFont(font)
            painter.drawText(10, offset, self.legend_notes)
        else:
            LOGGER.debug('No notes')

    def grow_legend(self):
        """Grow the legend pixmap enough to accommodate one more legend entry.
        """
        LOGGER.debug('InaSAFE Map Legend extendLegend called')
        if self.legend_image is None:

            self.legend_image = QtGui.QImage(
                self.legend_width, 95, QtGui.QImage.Format_RGB32)
            self.legend_image.setDotsPerMeterX(dpi_to_meters(self.dpi))
            self.legend_image.setDotsPerMeterY(dpi_to_meters(self.dpi))

            # Only works in Qt4.8
            #self.legendImage.fill(QtGui.QColor(255, 255, 255))
            # Works in older Qt4 versions
            self.legend_image.fill(255 + 255 * 256 + 255 * 256 * 256)
            painter = QtGui.QPainter(self.legend_image)
            font_weight = QtGui.QFont.Bold
            italics_flag = False
            font = QtGui.QFont(
                'verdana', self.legend_font_size, font_weight, italics_flag)
            painter.setFont(font)
            painter.drawText(10, 25, self.legend_title)

            if self.legend_units is not None:
                font_weight = QtGui.QFont.StyleNormal
                italics_flag = True
                legend_units_font_size = self.legend_font_size / 2
                font = QtGui.QFont(
                    'verdana',
                    legend_units_font_size,
                    font_weight,
                    italics_flag)
                painter.setFont(font)
                painter.drawText(10, 45, self.legend_units)

        else:
            # extend the existing legend down for the next class
            image = QtGui.QImage(
                self.legend_width,
                self.legend_image.height() + self.legend_increment,
                QtGui.QImage.Format_RGB32)
            image.setDotsPerMeterX(dpi_to_meters(self.dpi))
            image.setDotsPerMeterY(dpi_to_meters(self.dpi))
            # Only works in Qt4.8
            #myImage.fill(QtGui.qRgb(255, 255, 255))
            # Works in older Qt4 versions
            image.fill(255 + 255 * 256 + 255 * 256 * 256)
            painter = QtGui.QPainter(image)

            rect = QtCore.QRectF(
                0, 0, self.legend_image.width(), self.legend_image.height())
            painter.drawImage(rect, self.legend_image, rect)
            self.legend_image = image
