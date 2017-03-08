# coding=utf-8

"""Clip a raster by bounding box."""

import processing
import logging

from qgis.core import QgsRasterLayer

from safe.common.exceptions import ProcessingInstallationError
from safe.common.utilities import unique_filename, temp_dir
from safe.definitions.processing_steps import quick_clip_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.gis import is_raster_y_inverted
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def clip_by_extent(layer, extent, callback=None):
    """Clip a raster using a bounding box using processing.

    Issue https://github.com/inasafe/inasafe/issues/3183

    :param layer: The layer to reproject.
    :type layer: QgsRasterLayer

    :param extent: The extent.
    :type extent: QgsRectangle

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = quick_clip_steps['output_layer_name']
    processing_step = quick_clip_steps['step_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']

    output_raster = unique_filename(dir=temp_dir())

    if is_raster_y_inverted(layer):
        bbox = [
            str(extent.xMinimum()),
            str(extent.xMaximum()),
            str(extent.yMaximum()),
            str(extent.yMinimum())
        ]
    else:
        bbox = [
            str(extent.xMinimum()),
            str(extent.xMaximum()),
            str(extent.yMinimum()),
            str(extent.yMaximum())
        ]

    # These values are all from the processing algorithm.
    # https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    # gdal/ClipByExtent.py
    # Please read the file to know these parameters.
    parameters = dict()
    parameters['INPUT'] = layer.source()
    parameters['NO_DATA'] = ''
    parameters['PROJWIN'] = ','.join(bbox)
    parameters['RTYPE'] = 5
    parameters['COMPRESS'] = 4
    parameters['JPEGCOMPRESSION'] = 75
    parameters['ZLEVEL'] = 6
    parameters['PREDICTOR'] = 1
    parameters['TILED'] = False
    parameters['BIGTIFF'] = 0
    parameters['TFW'] = False
    parameters['EXTRA'] = ''
    parameters['OUTPUT'] = output_raster
    result = processing.runalg("gdalogr:cliprasterbyextent", parameters)

    if result is None:
        raise ProcessingInstallationError

    clipped = QgsRasterLayer(result['OUTPUT'], output_layer_name)

    # We transfer keywords to the output.
    clipped.keywords = layer.keywords.copy()
    clipped.keywords['title'] = output_layer_name

    # noinspection PyBroadException
    try:
        check_layer(clipped)
    except:
        # This step clip_raster_by_extent was nice to speedup the analysis.
        # As we got an exception because the layer is invalid, we are not going
        # to stop the analysis. We will return the original raster layer.
        # It will take more processing time until we clip the vector layer.
        # LOGGER.exception(parameters)
        # LOGGER.exception(
        #    'Error from QGIS clip raster by extent. Please check the QGIS '
        #    'logs too !')
        clipped = layer

    return clipped
