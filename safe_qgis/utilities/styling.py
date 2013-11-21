# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import sys
import logging
import math
import numpy

from PyQt4 import QtGui
from qgis.core import (
    QGis,
    QgsGraduatedSymbolRendererV2,
    QgsSymbolV2,
    QgsRendererRangeV2,
    QgsRendererCategoryV2,
    QgsCategorizedSymbolRendererV2,
    QgsSimpleMarkerSymbolLayerV2,
    QgsSimpleFillSymbolLayerV2,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer)

from safe_qgis.exceptions import StyleError

LOGGER = logging.getLogger('InaSAFE')


def set_vector_graduated_style(vector_layer, style):
    """Set graduated QGIS vector style based on InaSAFE style dictionary.

    For **opaque** a value of **0** can be used. For **fully transparent**, a
    value of **100** can be used. The calling function should take care to
    scale the transparency level to between 0 and 100.

    :param vector_layer: A QGIS vector layer that will be styled.
    :type vector_layer: QgsVectorLayer, QgsMapLayer

    :param style: Dictionary of the form as in the example below
    :type style: dict

    :returns: None - Sets and saves style for vector_layer

    Example style::

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'transparency': 1, 'max': 1.5, 'colour': '#fecc5c',
          'min': 0.5, 'label': '[0.5 - 1.5] Low damage', 'size' : 1},
        {'transparency': 55, 'max': 2.5, 'colour': '#fd8d3c',
         'min': 1.5, 'label': '[1.5 - 2.5] Medium damage', 'size' : 1},
        {'transparency': 80, 'max': 3.5, 'colour': '#f31a1c',
         'min': 2.5, 'label': '[2.5 - 3.5] High damage', 'size' : 1}]}

    .. note:: The transparency and size keys are optional. Size applies
       to points only.

    .. note:: you can optionally pass border_color also, if not color will be
        used
    """
    target_field = style['target_field']
    style_classes = style['style_classes']
    geometry_type = vector_layer.geometryType()

    range_list = []
    for style_class in style_classes:
        # Transparency 100: transparent
        # Transparency 0: opaque
        size = 2  # mm
        if 'size' in style_class:
            size = style_class['size']
        transparency_percent = 0
        if 'transparency' in style_class:
            transparency_percent = style_class['transparency']

        if 'min' not in style_class:
            raise StyleError('Style info should provide a "min" entry')
        if 'max' not in style_class:
            raise StyleError('Style info should provide a "max" entry')

        try:
            min_val = float(style_class['min'])
        except TypeError:
            raise StyleError(
                'Class break lower bound should be a number.'
                'I got %s' % style_class['min'])

        try:
            max_val = float(style_class['max'])
        except TypeError:
            raise StyleError('Class break upper bound should be a number.'
                             'I got %s' % style_class['max'])

        color = style_class['colour']
        label = style_class['label']
        color = QtGui.QColor(color)
        # noinspection PyArgumentList
        symbol = QgsSymbolV2.defaultSymbol(geometry_type)
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        # noinspection PyArgumentList
        try:
            border_color = QtGui.QColor(style_class['border_color'])
        except KeyError:
            border_color = color

        if geometry_type == QGis.Point:
            symbol_layer = QgsSimpleMarkerSymbolLayerV2()
            symbol_layer.setBorderColor(border_color)
            symbol_layer.setSize(size)
            symbol.changeSymbolLayer(0, symbol_layer)
        elif geometry_type == QGis.Polygon:
            symbol_layer = QgsSimpleFillSymbolLayerV2()
            symbol_layer.setBorderColor(border_color)
            symbol.changeSymbolLayer(0, symbol_layer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        try:
            symbol_layer.setBorderWidth(style_class['border_width'])
        except (NameError, KeyError):
            # use QGIS default border size
            # NameError is when symbol_layer is not defined (lines for example)
            # KeyError is when border_width is not defined
            pass
        symbol.setColor(color)
        # .. todo:: Check that vectors use alpha as % otherwise scale TS
        # Convert transparency % to opacity
        # alpha = 0: transparent
        # alpha = 1: opaque
        alpha = 1 - transparency_percent / 100.0
        symbol.setAlpha(alpha)
        range_renderer = QgsRendererRangeV2(min_val, max_val, symbol, label)
        range_list.append(range_renderer)

    renderer = QgsGraduatedSymbolRendererV2('', range_list)
    renderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    renderer.setClassAttribute(target_field)
    vector_layer.setRendererV2(renderer)
    vector_layer.saveDefaultStyle()


def set_vector_categorized_style(vector_layer, style):
    """Set categorized QGIS vector style based on InaSAFE style dictionary.

    For **opaque** a value of **0** can be used. For **fully transparent**, a
    value of **100** can be used. The calling function should take care to
    scale the transparency level to between 0 and 100.

    :param vector_layer: A QGIS vector layer that will be styled.
    :type vector_layer: QgsVectorLayer

    :param style: Dictionary of the form as in the example below.
    :type style: dict

    :returns: None - Sets and saves style for vector_layer

    Example::

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'transparency': 1, 'value': 1, 'colour': '#fecc5c',
          'label': 'Low damage', 'size' : 1},
        {'transparency': 55, 'value': 2, 'colour': '#fd8d3c',
         'label': 'Medium damage', 'size' : 1},
        {'transparency': 80, 'value': 3, 'colour': '#f31a1c',
         'label': 'High damage', 'size' : 1}]}

    .. note:: The transparency and size keys are optional. Size applies
        to points only.

    .. note:: We should change 'value' in style classes to something more
        meaningful e.g. discriminant value

    .. note:: you can optionally pass border_color also, if not color will be
        used
    .. note:: you can optionally pass border_width also, if not QGIS defaults
        will be used
    """
    target_field = style['target_field']
    style_classes = style['style_classes']
    geometry_type = vector_layer.geometryType()

    category_list = []
    for style_class in style_classes:
        # Transparency 100: transparent
        # Transparency 0: opaque
        size = 2  # mm
        if 'size' in style_class:
            size = style_class['size']
        transparency_percent = 0
        if 'transparency' in style_class:
            transparency_percent = style_class['transparency']

        if 'value' not in style_class:
            raise StyleError('Style info should provide a "value" entry')

        value = style_class['value']
        colour = style_class['colour']
        label = style_class['label']
        colour = QtGui.QColor(colour)
        try:
            border_color = QtGui.QColor(style_class['border_color'])
        except KeyError:
            border_color = colour

        # noinspection PyArgumentList
        symbol = QgsSymbolV2.defaultSymbol(geometry_type)
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        # noinspection PyArgumentList
        if geometry_type == QGis.Point:
            symbol_layer = QgsSimpleMarkerSymbolLayerV2()
            symbol_layer.setBorderColor(border_color)
            symbol_layer.setSize(size)
            symbol.changeSymbolLayer(0, symbol_layer)
        elif geometry_type == QGis.Polygon:
            symbol_layer = QgsSimpleFillSymbolLayerV2()
            symbol_layer.setBorderColor(border_color)
            symbol.changeSymbolLayer(0, symbol_layer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        try:
            symbol_layer.setBorderWidth(style_class['border_width'])
        except (NameError, KeyError):
            # use QGIS default border size
            # NameError is when symbol_layer is not defined (lines for example)
            # KeyError is when border_width is not defined
            pass

        symbol.setColor(colour)
        # .. todo:: Check that vectors use alpha as % otherwise scale TS
        # Convert transparency % to opacity
        # alpha = 0: transparent
        # alpha = 1: opaque
        alpha = 1 - transparency_percent / 100.0
        symbol.setAlpha(alpha)
        category = QgsRendererCategoryV2(value, symbol, label)
        category_list.append(category)

    renderer = QgsCategorizedSymbolRendererV2('', category_list)
    renderer.setClassAttribute(target_field)
    vector_layer.setRendererV2(renderer)
    vector_layer.saveDefaultStyle()


def setRasterStyle(raster_layer, style):
    """Set QGIS raster style based on InaSAFE style dictionary.

    This function will set both the colour map and the transparency
    for the passed in layer.

    :param raster_layer: A QGIS raster layer that will be styled.
    :type raster_layer: QgsVectorLayer

    :param style: Dictionary of the form as in the example below.
    :type style: dict

    Example:
        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    :returns: A two tuple containing a range list and a transparency list.
    :rtype: (list, list)
    """
    new_styles = add_extrema_to_style(style['style_classes'])
    LOGGER.debug('Rendering raster using 2+ styling')
    return set_raster_style(raster_layer, new_styles)


def add_extrema_to_style(style):
    """Add a min and max to each style class in a style dictionary.

    When InaSAFE provides style classes they are specific values, not ranges.
    However QGIS wants to work in ranges, so this helper will address that by
    updating the dictionary to include a min max value for each class.

    It is assumed that we will start for 0 as the min for the first class
    and the quantity of each class shall constitute the max. For all other
    classes , min shall constitute the smalles increment to a float that can
    meaningfully be made by python (as determined by numpy.nextafter()).

    :param style: A list of dictionaries of the form as per the example below.
    :type style: list(dict)

    :returns: A new dictionary list with min max attributes added to each
        entry.
    :rtype: list(dict)

    Example input::

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    Example output::

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0,
                              min=0, max=2),
                         dict(colour='#38A800', quantity=5, transparency=50,
                              min=2.0000000000002, max=5),
                         ),
                         dict(colour='#79C900', quantity=10, transparency=50,
                              min=5.0000000000002, max=10),),
                         dict(colour='#CEED00', quantity=20, transparency=50,
                              min=5.0000000000002, max=20),),
                         dict(colour='#FFCC00', quantity=50, transparency=34,
                              min=20.0000000000002, max=50),),
                         dict(colour='#FF6600', quantity=100, transparency=77,
                              min=50.0000000000002, max=100),),
                         dict(colour='#FF0000', quantity=200, transparency=24,
                              min=100.0000000000002, max=200),),
                         dict(colour='#7A0000', quantity=300, transparency=22,
                              min=200.0000000000002, max=300),)]
    """
    new_styles = []
    last_max = 0.0
    for style_class in style:
        quantity = float(style_class['quantity'])
        style_class['min'] = last_max
        style_class['max'] = quantity
        if quantity == last_max and quantity != 0:
            # skip it as it does not represent a class increment
            continue
        last_max = numpy.nextafter(quantity, sys.float_info.max)
        new_styles.append(style_class)
    return new_styles


def set_raster_style(raster_layer, style):
    """Set QGIS raster style based on InaSAFE style dictionary for QGIS >= 2.0.

    This function will set both the colour map and the transparency
    for the passed in layer.

    :param raster_layer: A QGIS raster layer that will be styled.
    :type raster_layer: QgsVectorLayer

    :param style: Dictionary of the form as in the example below.
    :type style: dict

    Example::

        style_classes = [dict(colour='#38A800', quantity=2, transparency=0),
                         dict(colour='#38A800', quantity=5, transparency=50),
                         dict(colour='#79C900', quantity=10, transparency=50),
                         dict(colour='#CEED00', quantity=20, transparency=50),
                         dict(colour='#FFCC00', quantity=50, transparency=34),
                         dict(colour='#FF6600', quantity=100, transparency=77),
                         dict(colour='#FF0000', quantity=200, transparency=24),
                         dict(colour='#7A0000', quantity=300, transparency=22)]

    :returns: A two tuple containing a range list and a transparency list.
    :rtype: (list, list)

    """
    # Note imports here to prevent importing on unsupported QGIS versions
    # pylint: disable=E0611
    # pylint: disable=W0621
    # pylint: disable=W0404
    # noinspection PyUnresolvedReferences
    from qgis.core import (QgsRasterShader,
                           QgsColorRampShader,
                           QgsSingleBandPseudoColorRenderer,
                           QgsRasterTransparency)
    # pylint: enable=E0611
    # pylint: enable=W0621
    # pylint: enable=W0404

    ramp_item_list = []
    transparency_list = []
    LOGGER.debug(style)
    for style_class in style:

        LOGGER.debug('Evaluating class:\n%s\n' % style_class)

        if 'quantity' not in style_class:
            LOGGER.exception('Class has no quantity attribute')
            continue

        class_max = style_class['max']
        if math.isnan(class_max):
            LOGGER.debug('Skipping class - max is nan.')
            continue

        class_min = style_class['min']
        if math.isnan(class_min):
            LOGGER.debug('Skipping class - min is nan.')
            continue

        colour = QtGui.QColor(style_class['colour'])
        label = ''
        if 'label' in style_class:
            label = style_class['label']
        # noinspection PyCallingNonCallable
        ramp_item = QgsColorRampShader.ColorRampItem(class_max, colour, label)
        ramp_item_list.append(ramp_item)

        # Create opacity entries for this range
        transparency_percent = 0
        if 'transparency' in style_class:
            transparency_percent = int(style_class['transparency'])
        if transparency_percent > 0:
            # Check if range extrema are integers so we know if we can
            # use them to calculate a value range
            # noinspection PyCallingNonCallable
            pixel = QgsRasterTransparency.TransparentSingleValuePixel()
            pixel.min = class_min
            # We want it just a little bit smaller than max
            # so that ranges are discrete
            pixel.max = class_max
            #noinspection PyPep8Naming
            pixel.percentTransparent = transparency_percent
            transparency_list.append(pixel)

    band = 1  # gdal counts bands from base 1
    LOGGER.debug('Setting colour ramp list')
    raster_shader = QgsRasterShader()
    color_ramp_shader = QgsColorRampShader()
    color_ramp_shader.setColorRampType(QgsColorRampShader.INTERPOLATED)
    color_ramp_shader.setColorRampItemList(ramp_item_list)
    LOGGER.debug('Setting shader function')
    raster_shader.setRasterShaderFunction(color_ramp_shader)
    LOGGER.debug('Setting up renderer')
    renderer = QgsSingleBandPseudoColorRenderer(
        raster_layer.dataProvider(),
        band,
        raster_shader)
    LOGGER.debug('Assigning renderer to raster layer')
    raster_layer.setRenderer(renderer)

    LOGGER.debug('Setting raster transparency list')

    renderer = raster_layer.renderer()
    transparency = QgsRasterTransparency()
    transparency.setTransparentSingleValuePixelList(transparency_list)
    renderer.setRasterTransparency(transparency)
    # For interest you can also view the list like this:
    #pix = t.transparentSingleValuePixelList()
    #for px in pix:
    #    print 'Min: %s Max %s Percent %s' % (
    #       px.min, px.max, px.percentTransparent)

    LOGGER.debug('Saving style as default')
    raster_layer.saveDefaultStyle()
    LOGGER.debug('Setting raster style done!')
    return ramp_item_list, transparency_list


def mmi_ramp(raster_layer):
    """Generate an mmi ramp using standardised range of 1-12

    A standarised range is used so that two shakemaps of different
    intensities can be properly compared visually with colours stretched
    accross the same range.

    The colours used are the 'standard' colours commonly shown for the
    mercalli scale e.g. on wikipedia and other sources.

    :param raster_layer: A raster layer that will have an mmi style applied.
    :type raster_layer: QgsRasterLayer
    """

    items = []
    for class_max in range(1, 13):
        colour = QtGui.QColor(mmi_colour(class_max))
        label = '%i' % class_max
        ramp_item = QgsColorRampShader.ColorRampItem(class_max, colour, label)
        items.append(ramp_item)

    raster_shader = QgsRasterShader()
    ramp_shader = QgsColorRampShader()
    ramp_shader.setColorRampType(QgsColorRampShader.INTERPOLATED)
    ramp_shader.setColorRampItemList(items)
    raster_shader.setRasterShaderFunction(ramp_shader)
    band = 1
    renderer = QgsSingleBandPseudoColorRenderer(
        raster_layer.dataProvider(),
        band,
        raster_shader)
    raster_layer.setRenderer(renderer)


def mmi_colour(mmi_value):
    """Return the colour for an mmi value.

    :param mmi_value: float or int required.
    :returns str: html hex code colour for the value
    """

    rgb_list = ['#FFFFFF', '#FFFFFF', '#209fff', '#00cfff', '#55ffff',
                '#aaffff', '#fff000', '#ffa800', '#ff7000', '#ff0000',
                '#D00', '#800', '#400']
    rgb = rgb_list[int(mmi_value)]
    return rgb
