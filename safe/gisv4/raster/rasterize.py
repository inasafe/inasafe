# coding=utf-8

from qgis.core import QgsRasterLayer

from processing.core.Processing import Processing

from safe.common.utilities import unique_filename
from safe.definitions.processing_steps import rasterize_steps

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def rasterize_vector_layer(layer, attribute_name, width, height, extent):
    """Rasterize a vector layer to the grid given by extent and
    width/height of the output raster.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param attribute_name: The attribute name to be created.
    :type attribute_name: basestring

    :param width: The width of the output.
    :type width: int

    :param height: The height of the output.
    :type height: int

    :param extent: The extent to use.
    :type extent: QgsRectangle

    :return: The new raster layer.
    :rtype: QgsRasterLayer
    """

    output_filename = unique_filename(
        prefix=rasterize_steps['gdal_layer_name'], suffix='.tif')

    extent_str = '%f,%f,%f,%f' % (extent.xMinimum(), extent.xMaximum(),
                                  extent.yMinimum(), extent.yMaximum())
    Processing.runAlgorithm(
        'gdalogr:rasterize',
        None,
        layer,
        attribute_name,
        0,      # output size is given in pixels
        width,
        height,
        extent_str,
        False,  # force generation of ESRI TFW
        # advanced options
        1,      # raster type: Int16
        '-1',   # nodata value
        4,      # GeoTIFF compression: DEFLATE
        75,     # JPEG compression level: 75
        6,      # DEFLATE compression level
        1,      # predictor for JPEG/DEFLATE
        False,  # Tiled GeoTIFF?
        0,      # whether to make big TIFF
        '',     # additional creation parameters
        # output
        output_filename)

    layer_aligned = QgsRasterLayer(
        output_filename, rasterize_steps['output_layer_name'], 'gdal')

    assert layer_aligned.isValid()

    return layer_aligned
