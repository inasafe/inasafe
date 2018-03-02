# coding=utf-8

"""Tools for GIS operations."""

import logging
import os

from PyQt4.QtCore import QPyNullVariant
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsDataSourceURI,
)

from safe.common.exceptions import NoKeywordsFoundError, InvalidLayerError
from safe.definitions.constants import (
    VECTOR_DRIVERS,
    RASTER_DRIVERS,
    OGR_EXTENSIONS,
    GDAL_EXTENSIONS,
)
from safe.definitions.layer_geometry import (
    layer_geometry_raster,
    layer_geometry_point,
    layer_geometry_line,
    layer_geometry_polygon,
)
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer,
    is_line_layer,
    is_polygon_layer,
    qgis_version,
)
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
    # reload the layer in case the layer path has no provider information
    the_layer = load_layer(layer_path)[0]
    layers = QgsMapLayerRegistry.instance().mapLayers()
    for _, layer in layers.items():
        if full_layer_uri(layer) == full_layer_uri(the_layer):
            monkey_patch_keywords(layer)
            return layer

    return the_layer


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


def full_layer_uri(layer):
    """Internal URI helper for a layer.

    It combines the provider source and the provider key.

    :param layer: The layer.
    :type layer: QgsMapLayer

    :return: The full URI
    :rtype: basestring
    """
    return layer.source() + '|qgis_provider=' + layer.providerType()


def decode_full_layer_uri(full_layer_uri_string):
    """Decode the full layer URI.

    :param full_layer_uri_string: The full URI provided by our helper.
    :type full_layer_uri_string: basestring

    :return: A tuple with the QGIS URI and the provider key.
    :rtype: tuple
    """
    if not full_layer_uri_string:
        return None, None

    split = full_layer_uri_string.split('|qgis_provider=')
    if len(split) == 1:
        return split[0], None
    else:
        return split


def load_layer(full_layer_uri_string, name=None, provider=None):
    """Helper to load and return a single QGIS layer based on our layer URI.

    :param provider: The provider name to use if known to open the layer.
        Default to None, we will try to guess it, but it's much better if you
        can provide it.
    :type provider:

    :param name: The name of the layer. If not provided, it will be computed
        based on the URI.
    :type name: basestring

    :param full_layer_uri_string: Layer URI, with provider type.
    :type full_layer_uri_string: str

    :returns: tuple containing layer and its layer_purpose.
    :rtype: (QgsMapLayer, str)
    """
    if provider:
        # Cool !
        layer_path = full_layer_uri_string
    else:
        #  Let's check if the driver is included in the path
        layer_path, provider = decode_full_layer_uri(full_layer_uri_string)

        if not provider:
            # Let's try to check if it's file based and look for a extension
            if '|' in layer_path:
                clean_uri = layer_path.split('|')[0]
            else:
                clean_uri = layer_path
            is_file_based = os.path.exists(clean_uri)
            if is_file_based:
                # Extract basename and absolute path
                file_name = os.path.split(layer_path)[
                    -1]  # If path was absolute
                extension = os.path.splitext(file_name)[1]
                if extension in OGR_EXTENSIONS:
                    provider = 'ogr'
                elif extension in GDAL_EXTENSIONS:
                    provider = 'gdal'
                else:
                    provider = None

    if not provider:
        layer = load_layer_without_provider(layer_path)
    else:
        layer = load_layer_with_provider(layer_path, provider)

    if not layer or not layer.isValid():
        message = 'Layer "%s" is not valid' % layer_path
        LOGGER.debug(message)
        raise InvalidLayerError(message)

    # Define the name
    if not name:
        source = layer.source()
        if '|' in source:
            clean_uri = source.split('|')[0]
        else:
            clean_uri = source
        is_file_based = os.path.exists(clean_uri)
        if is_file_based:
            # Extract basename and absolute path
            file_name = os.path.split(layer_path)[-1]  # If path was absolute
            name = os.path.splitext(file_name)[0]
        else:
            # Might be a DB, take the DB name
            source = QgsDataSourceURI(source)
            name = source.table()

    if not name:
        name = 'default'

    if qgis_version() >= 21800:
        layer.setName(name)
    else:
        layer.setLayerName(name)

    # Determine if layer is hazard or exposure
    layer_purpose = 'undefined'
    try:
        keywords = read_iso19115_metadata(layer.source())
        if 'layer_purpose' in keywords:
            layer_purpose = keywords['layer_purpose']
    except NoKeywordsFoundError:
        pass

    monkey_patch_keywords(layer)

    return layer, layer_purpose


def load_layer_with_provider(layer_uri, provider, layer_name='tmp'):
    """Load a layer with a specific driver.

    :param layer_uri: Layer URI that will be used by QGIS to load the layer.
    :type layer_uri: basestring

    :param provider: Provider name to use.
    :type provider: basestring

    :param layer_name: Layer name to use. Default to 'tmp'.
    :type layer_name: basestring

    :return: The layer or None if it's failed.
    :rtype: QgsMapLayer
    """
    if provider in RASTER_DRIVERS:
        return QgsRasterLayer(layer_uri, layer_name, provider)
    elif provider in VECTOR_DRIVERS:
        return QgsVectorLayer(layer_uri, layer_name, provider)
    else:
        return None


def load_layer_without_provider(layer_uri, layer_name='tmp'):
    """Helper to load a layer when don't know the driver.

    Don't use it, it's an empiric function to try each provider one per one.

    OGR/GDAL is printing a lot of error saying that the layer is not valid.

    :param layer_uri: Layer URI that will be used by QGIS to load the layer.
    :type layer_uri: basestring

    :param layer_name: Layer name to use. Default to 'tmp'.
    :type layer_name: basestring

    :return: The layer or None if it's failed.
    :rtype: QgsMapLayer
    """
    # Let's try the most common vector driver
    layer = QgsVectorLayer(layer_uri, layer_name, VECTOR_DRIVERS[0])
    if layer.isValid():
        return layer

    # Let's try the most common raster driver
    layer = QgsRasterLayer(layer_uri, layer_name, RASTER_DRIVERS[0])
    if layer.isValid():
        return layer

    # Then try all other drivers
    for driver in VECTOR_DRIVERS[1:]:
        if driver == 'delimitedtext':
            # Explicitly use URI with delimiter or tests fail in Windows. TS.
            layer = QgsVectorLayer(
                'file:///%s?delimiter=,' % layer_uri, layer_name, driver)
            if layer.isValid():
                return layer
        layer = QgsVectorLayer(layer_uri, layer_name, driver)
        if layer.isValid():
            return layer

    for driver in RASTER_DRIVERS[1:]:
        layer = QgsRasterLayer(layer_uri, layer_name, driver)
        if layer.isValid():
            return layer

    return None
