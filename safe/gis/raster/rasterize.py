# coding=utf-8

"""Rasterize a vector layer."""

from tempfile import mkdtemp
from collections import OrderedDict
from qgis.core import QgsRasterLayer

from processing import runalg

from safe.common.utilities import unique_filename
from safe.datastore.folder import Folder
from safe.definitions.fields import aggregation_id_field
from safe.definitions.processing_steps import rasterize_steps
from safe.definitions.layer_purposes import layer_purpose_aggregation_impacted
from safe.gis.sanity_check import check_layer
from safe.utilities.gis import qgis_version
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def rasterize_vector_layer(layer, width, height, extent):
    """Rasterize a vector layer to the grid given by extent and width/height.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param width: The width of the output.
    :type width: int

    :param height: The height of the output.
    :type height: int

    :param extent: The extent to use.
    :type extent: QgsRectangle

    :return: The new raster layer.
    :rtype: QgsRasterLayer
    """
    name = rasterize_steps['gdal_layer_name']
    output_filename = unique_filename(prefix=name, suffix='.tif')

    extent_str = '%f,%f,%f,%f' % (
        extent.xMinimum(),
        extent.xMaximum(),
        extent.yMinimum(),
        extent.yMaximum())

    keywords = dict(layer.keywords)

    # The layer is in memory, we need to save it to a file for Processing.
    data_store = Folder(mkdtemp())
    data_store.default_vector_format = 'geojson'
    result = data_store.add_layer(layer, 'vector_layer')
    layer = data_store.layer(result[1])
    assert layer.isValid()

    parameters = OrderedDict()
    parameters['INPUT'] = layer
    parameters['FIELD'] = (
        layer.keywords['inasafe_fields'][aggregation_id_field['key']])
    parameters['DIMENSIONS'] = 0  # output size is given in pixels
    parameters['WIDTH'] = width
    parameters['HEGHT'] = height
    parameters['RASTER_EXT'] = extent_str
    parameters['TFW'] = False  # force generation of ESRI TFW
    parameters['RTYPE'] = 1  # raster type: Int16
    parameters['NO_DATA'] = '-1'   # nodata value
    parameters['COMPRESS'] = 4  # GeoTIFF compression: DEFLATE
    parameters['JPEGCOMPRESSION'] = 75  # JPEG compression level: 75
    parameters['ZLEVEL'] = 6  # DEFLATE compression level
    parameters['PREDICTOR'] = 1  # predictor for JPEG/DEFLATE
    parameters['TILED'] = False  # Tiled GeoTIFF?
    parameters['BIGTIFF'] = 0  # whether to make big TIFF
    parameters['EXTRA'] = ''  # additional creation parameters
    parameters['OUTPUT'] = output_filename

    if qgis_version() < 21600:
        # New parameter in QGIS 2.16. We need to remove it if QGIS < 2.16.
        del parameters['RASTER_EXT']

    result = runalg('gdalogr:rasterize', *parameters.values())

    assert result is not None

    layer_aligned = QgsRasterLayer(output_filename, name, 'gdal')

    layer_aligned.keywords = keywords
    layer_aligned.keywords['title'] = (
        rasterize_steps['output_layer_name'] % 'aggregation')
    layer_aligned.keywords['layer_purpose'] = (
        layer_purpose_aggregation_impacted['key'])
    del layer_aligned.keywords['inasafe_fields']

    check_layer(layer_aligned)
    return layer_aligned
