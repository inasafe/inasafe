# coding=utf-8
"""Common utilities function for GIS."""

import os
import logging
from qgis.core import QgsRasterLayer, QgsVectorLayer

from safe.common.exceptions import NoKeywordsFoundError
from safe.utilities.metadata import read_iso19115_metadata
from safe.utilities.utilities import monkey_patch_keywords

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


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

    # noinspection PyUnresolvedReferences
    message = 'Layer "%s" is not valid' % layer.source()
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        LOGGER.debug(message)
        raise Exception(message)

    monkey_patch_keywords(layer)

    return layer, layer_purpose
