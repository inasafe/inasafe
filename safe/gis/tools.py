# coding=utf-8

"""Tools for GIS operations."""

from PyQt4.QtCore import QPyNullVariant

from safe.definitions.layer_geometry import (
    layer_geometry_raster,
    layer_geometry_point,
    layer_geometry_line,
    layer_geometry_polygon,
)
from safe.utilities.gis import is_raster_layer, is_point_layer, is_line_layer


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def geometry_type(layer):
    """Retrieve the geometry type: point, line, polygon or raster for a layer.

    :param layer: The layer.
    :type layer: QgsMapLayer

    :return: The definition key.
    :rtype: basestring
    """
    if is_raster_layer(layer):
        return layer_geometry_raster['key']
    elif is_point_layer(layer):
        return layer_geometry_point['key']
    elif is_line_layer(layer):
        return layer_geometry_line['key']
    else:
        return layer_geometry_polygon['key']


def reclassify_value(one_value, ranges):
    """This function will return the classified value according to ranges.

    The algorithm will return None if the continuous value has not any class.

    :param one_value: The continuous value to classify.
    :type one_value: float

    :param ranges: Classes, following the hazard classification definitions.
    :type ranges: OrderedDict

    :return: The classified value or None.
    :rtype: float or None
    """
    if one_value is None or one_value == '' or isinstance(
            one_value, QPyNullVariant):
        return None

    for threshold_id, threshold in ranges.iteritems():
        value_min = threshold[0]
        value_max = threshold[1]

        # If, eg [0, 0], the one_value must be equal to 0.
        if value_min == value_max and value_max == one_value:
            return threshold_id

        # If, eg [None, 0], the one_value must be less or equal than 0.
        if value_min is None and one_value <= value_max:
            return threshold_id

        # If, eg [0, None], the one_value must be greater than 0.
        if value_max is None and one_value > value_min:
            return threshold_id

        # If, eg [0, 1], the one_value must be
        # between 0 excluded and 1 included.
        if value_min < one_value <= value_max:
            return threshold_id

    return None
