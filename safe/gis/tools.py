# coding=utf-8

"""Tools for GIS operations."""

import logging
import os

from PyQt4.QtCore import QPyNullVariant
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsMapLayerRegistry

from safe.common.exceptions import NoKeywordsFoundError
from safe.definitions.layer_geometry import (
    layer_geometry_raster,
    layer_geometry_point,
    layer_geometry_line,
    layer_geometry_polygon,
)
from safe.utilities.gis import (
    is_raster_layer, is_point_layer, is_line_layer, is_polygon_layer)
from safe.utilities.metadata import read_iso19115_metadata
from safe.utilities.utilities import monkey_patch_keywords

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


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
    elif is_polygon_layer(layer):
        return layer_geometry_polygon['key']
    else:
        return None


def load_layer_from_registry(layer_path):
    """Helper method to load a layer from registry if its already there.

    If the layer is not loaded yet, it will create the QgsMapLayer on the fly.

    :param layer_path: Layer source path.
    :type layer_path: str

    :return: Vector layer
    :rtype: QgsVectorLayer

    .. versionadded: 4.3.0
    """
    layers = QgsMapLayerRegistry.instance().mapLayers()
    for _, layer in layers.items():
        if layer.source() == layer_path:
            monkey_patch_keywords(layer)
            return layer

    return load_layer(layer_path)[0]


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


def load_layer(layer_path):
    """Helper to load and return a single QGIS layer.

    :param layer_path: Path name to raster or vector file.
    :type layer_path: str

    :returns: tuple containing layer and its layer_purpose.
    :rtype: (QgsMapLayer, str)
    """
    # Extract basename and absolute path
    file_name = os.path.split(layer_path)[-1]  # In case path was absolute
    base_name, extension = os.path.splitext(file_name)

    # Determine if layer is hazard or exposure
    layer_purpose = 'undefined'
    try:
        keywords = read_iso19115_metadata(layer_path)
        if 'layer_purpose' in keywords:
            layer_purpose = keywords['layer_purpose']
    except NoKeywordsFoundError:
        pass

    # Create QGis Layer Instance
    if extension in ['.asc', '.tif', '.tiff']:
        layer = QgsRasterLayer(layer_path, base_name)
    elif extension in ['.shp', '.geojson', '.gpkg']:
        layer = QgsVectorLayer(layer_path, base_name, 'ogr')
    elif extension in ['.csv']:
        uri = 'file:///%s?delimiter=%s' % (layer_path, ',')
        layer = QgsVectorLayer(uri, base_name, 'delimitedtext')
    else:
        message = 'File %s had illegal extension' % layer_path
        raise Exception(message)

    if not layer.isValid():
        message = 'Layer "%s" is not valid' % layer.source()
        LOGGER.debug(message)
        raise Exception(message)

    monkey_patch_keywords(layer)

    return layer, layer_purpose
