# coding=utf-8
"""
Clip a raster by bounding box.
"""

import processing

from qgis.core import QgsRasterLayer

from safe.common.utilities import unique_filename, temp_dir
from safe.definitionsv4.processing_steps import quick_clip_steps
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

from qgis.core import QgsRectangle


@profile
def clip_by_extent(layer, extent, callback=None):
    """
    Clip a raster using a bounding box using processing.

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
    # Todo, we shoud use named parameters.
    result = processing.runalg(
        "gdalogr:cliprasterbyextent",
        layer.source(),
        "",
        ','.join(bbox),
        5,
        4,
        75,
        6,
        1,
        False,
        0,
        False,
        "",
        output_raster)

    clipped = QgsRasterLayer(result['OUTPUT'], output_layer_name)

    # We transfer keywords to the output.
    clipped.keywords = layer.keywords.copy()
    clipped.keywords['title'] = output_layer_name

    return clipped
