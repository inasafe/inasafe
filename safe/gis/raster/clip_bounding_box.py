# coding=utf-8

"""Clip a raster by bounding box."""

import logging

import processing
from qgis.core import QgsRasterLayer, QgsApplication

from safe.common.exceptions import ProcessingInstallationError
from safe.common.utilities import unique_filename, temp_dir
from safe.definitions.processing_steps import quick_clip_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.gis import is_raster_y_inverted
from safe.utilities.profiling import profile
from safe.utilities.utilities import get_error_message

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def clip_by_extent(layer, extent, callback=None):
    """Clip a raster using a bounding box using processing.

    Issue https://github.com/inasafe/inasafe/issues/3183

    :param layer: The layer to  clip.
    :type layer: QgsRasterLayer

    :param extent: The extent.
    :type extent: QgsRectangle

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :return: Clipped layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    parameters = dict()
    # noinspection PyBroadException
    try:
        output_layer_name = quick_clip_steps['output_layer_name']
        processing_step = quick_clip_steps['step_name']  # NOQA
        output_layer_name = output_layer_name % layer.keywords['layer_purpose']

        output_raster = unique_filename(suffix='.tif', dir=temp_dir())

        # We make one pixel size buffer on the extent to cover every pixels.
        # See https://github.com/inasafe/inasafe/issues/3655
        pixel_size_x = layer.rasterUnitsPerPixelX()
        pixel_size_y = layer.rasterUnitsPerPixelY()
        buffer_size = max(pixel_size_x, pixel_size_y)
        extent = extent.buffered(buffer_size)

        if is_raster_y_inverted(layer):
            # The raster is Y inverted. We need to switch Y min and Y max.
            bbox = [
                str(extent.xMinimum()),
                str(extent.xMaximum()),
                str(extent.yMaximum()),
                str(extent.yMinimum())
            ]
        else:
            # The raster is normal.
            bbox = [
                str(extent.xMinimum()),
                str(extent.xMaximum()),
                str(extent.yMinimum()),
                str(extent.yMaximum())
            ]

        # These values are all from the processing algorithm.
        # https://github.com/qgis/QGIS/blob/master/python/plugins/processing/
        # algs/gdal/ClipByExtent.py
        # Please read the file to know these parameters.
        parameters['INPUT'] = layer.source()
        parameters['NO_DATA'] = ''
        parameters['PROJWIN'] = ','.join(bbox)
        parameters['DATA_TYPE'] = 5
        parameters['COMPRESS'] = 4
        parameters['JPEGCOMPRESSION'] = 75
        parameters['ZLEVEL'] = 6
        parameters['PREDICTOR'] = 1
        parameters['TILED'] = False
        parameters['BIGTIFF'] = 0
        parameters['TFW'] = False
        parameters['EXTRA'] = ''
        parameters['OUTPUT'] = output_raster

        # Fix safe.impact_function test failing
        if not QgsApplication.processingRegistry().algorithms():
            processing.Processing.initialize()

        result = processing.run("gdal:cliprasterbyextent", parameters)

        if result is None:
            raise ProcessingInstallationError

        clipped = QgsRasterLayer(result['OUTPUT'], output_layer_name)

        # We transfer keywords to the output.
        clipped.keywords = layer.keywords.copy()
        clipped.keywords['title'] = output_layer_name

        check_layer(clipped)

    except Exception as e:
        # This step clip_raster_by_extent was nice to speedup the analysis.
        # As we got an exception because the layer is invalid, we are not going
        # to stop the analysis. We will return the original raster layer.
        # It will take more processing time until we clip the vector layer.
        # Check https://github.com/inasafe/inasafe/issues/4026 why we got some
        # exceptions with this step.
        LOGGER.exception(parameters)
        LOGGER.exception(
            'Error from QGIS clip raster by extent. Please check the QGIS '
            'logs too !')
        LOGGER.info(
            'Even if we got an exception, we are continuing the analysis. The '
            'layer was not clipped.')
        LOGGER.exception(str(e))
        LOGGER.exception(get_error_message(e).to_text())
        clipped = layer

    return clipped
