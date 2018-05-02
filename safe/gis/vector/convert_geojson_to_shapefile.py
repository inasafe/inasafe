# coding=utf-8

"""Convert geojson file to shapefile.."""

import logging
import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


def convert_geojson_to_shapefile(geojson_path):
    """Convert geojson file to shapefile.
    It will create a necessary file next to the geojson file. It wil not
    affect another files (e.g. .xml, .qml, etc).

    :param geojson_path: The path to geojson file.
    :type geojson_path: basestring

    :returns: True if shapefile layer created, False otherwise.
    :rtype: bool
    """
    layer = QgsVectorLayer(geojson_path, 'vector layer', "ogr")
    if not layer.isValid():
        return False
    # Construct shapefile path
    shapefile_path = os.path.splitext(geojson_path)[0] + '.shp'
    QgsVectorFileWriter.writeAsVectorFormat(
        layer,
        shapefile_path,
        'utf-8',
        layer.crs(),
        'ESRI Shapefile')
    if os.path.exists(shapefile_path):
        return True
    return False
