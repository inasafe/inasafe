# coding=utf-8
"""
Zonal statistics on a raster layer.

Issue https://github.com/inasafe/inasafe/issues/3190
"""

import logging
from qgis.core import QgsRasterLayer
from qgis.analysis import QgsZonalStatistics

from safe.gisv4.vector.tools import copy_layer, create_memory_layer
from safe.gisv4.vector.prepare_vector_layer import copy_fields, remove_fields
from safe.definitionsv4.fields import exposure_count_field, total_field
from safe.definitionsv4.processing_steps import zonal_stats_steps
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
    output_layer_name = zonal_stats_steps['output_layer_name']
    processing_step = zonal_stats_steps['step_name']

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

    layer.startEditing()
    exposure = raster.keywords['exposure']
    output_field = exposure_count_field['field_name'] % exposure
    fields_to_rename = {
        'exposure_sum': output_field
    }
    copy_fields(layer, fields_to_rename)
    remove_fields(layer, fields_to_rename.keys())
    layer.commitChanges()

    layer.keywords = raster.keywords.copy()
    layer.keywords['inasafe_fields'] = vector.keywords['inasafe_fields'].copy()
    key = exposure_count_field['key'] % raster.keywords['exposure']

    # Special case here, one field is the exposure count and the total.
    layer.keywords['inasafe_fields'][key] = output_field
    layer.keywords['inasafe_fields'][total_field['key']] = output_field

    layer.keywords['exposure_keywords'] = raster.keywords
    layer.keywords['hazard_keywords'] = vector.keywords['hazard_keywords']
    layer.keywords['aggregation_keywords'] = (
        vector.keywords['aggregation_keywords'])

    layer.keywords['title'] = output_layer_name

    return layer
