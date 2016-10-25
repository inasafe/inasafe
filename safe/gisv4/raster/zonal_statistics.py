# coding=utf-8
"""
Zonal statistics on a raster layer.

Issue https://github.com/inasafe/inasafe/issues/3190
"""

import logging
from qgis.core import QgsRasterLayer
from qgis.analysis import QgsZonalStatistics

from safe.gisv4.vector.tools import copy_layer, create_memory_layer
from safe.common.exceptions import FileNotFoundError
from safe.common.utilities import unique_filename, temp_dir
from safe.definitionsv4.fields import population_count_field
from safe.definitionsv4.utilities import definition
from safe.definitionsv4.processing import reclassify_raster
from safe.utilities.profiling import profile
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def zonal_stats(raster, vector, callback=None):
    """Reclassify a continuous raster layer.

    :param raster: The raster layer.
    :type raster: QgsRasterLayer

    :param vector: The vector layer.
    :type vector: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The output of the zonal stats.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    # output_layer_name = zonal_statistics['output_layer_name']
    # processing_step = zonal_statistics['step_name']
    output_layer_name = 'zonal_statistics'
    processing_step = 'zonal_statistics'

    layer = create_memory_layer(
        output_layer_name,
        vector.geometryType(),
        vector.crs(),
        vector.fields()
    )

    copy_layer(vector, layer)

    analysis = QgsZonalStatistics(
        layer, raster.source(), 'exposure_', 1, QgsZonalStatistics.Sum)
    result = analysis.calculateStatistics(None)
    LOGGER.debug(tr('Zonal stats on %s : %s' % (raster.source(), result)))

    layer.keywords = raster.keywords.copy()
    layer.keywords['inasafe_fields'] = {
        population_count_field['key']: 'exposure_sum'
    }

    return layer
