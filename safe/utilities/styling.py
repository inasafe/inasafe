# coding=utf-8

"""Styling."""

import logging
from operator import itemgetter

from qgis.core import (
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer)

from safe.definitions.hazard_classifications import earthquake_mmi_scale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


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


def mmi_ramp_roman(raster_layer):
    """Generate an mmi ramp using range of 1-10 on roman.

    A standarised range is used so that two shakemaps of different
    intensities can be properly compared visually with colours stretched
    accross the same range.

    The colours used are the 'standard' colours commonly shown for the
    mercalli scale e.g. on wikipedia and other sources.

    :param raster_layer: A raster layer that will have an mmi style applied.
    :type raster_layer: QgsRasterLayer

    .. versionadded:: 4.0
    """

    items = []
    sorted_mmi_scale = sorted(
        earthquake_mmi_scale['classes'], key=itemgetter('value'))
    for class_max in sorted_mmi_scale:
        colour = class_max['color']
        label = '%s' % class_max['key']
        ramp_item = QgsColorRampShader.ColorRampItem(
            class_max['value'], colour, label)
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
