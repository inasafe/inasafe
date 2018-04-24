# coding=utf-8

"""Zonal statistics on a raster layer."""


import logging

from qgis.analysis import QgsZonalStatistics
from qgis.core import QgsFeatureRequest

from safe.definitions.fields import exposure_count_field, total_field
from safe.definitions.layer_purposes import (
    layer_purpose_aggregate_hazard_impacted)
from safe.definitions.processing_steps import zonal_stats_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.reproject import reproject
from safe.gis.vector.tools import (
    copy_layer,
    copy_fields,
    remove_fields,
    rename_fields,
    create_memory_layer,
    create_field_from_definition)
from safe.utilities.gis import qgis_version
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def zonal_stats(raster, vector):
    """Reclassify a continuous raster layer.

    Issue https://github.com/inasafe/inasafe/issues/3190

    The algorithm will take care about projections.
    We don't want to reproject the raster layer.
    So if CRS are different, we reproject the vector layer and then we do a
    lookup from the reprojected layer to the original vector layer.

    :param raster: The raster layer.
    :type raster: QgsRasterLayer

    :param vector: The vector layer.
    :type vector: QgsVectorLayer

    :return: The output of the zonal stats.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = zonal_stats_steps['output_layer_name']

    exposure = raster.keywords['exposure']
    if raster.crs().authid() != vector.crs().authid():
        layer = reproject(vector, raster.crs())

        # We prepare the copy
        output_layer = create_memory_layer(
            output_layer_name,
            vector.geometryType(),
            vector.crs(),
            vector.fields()
        )
        copy_layer(vector, output_layer)
    else:
        layer = create_memory_layer(
            output_layer_name,
            vector.geometryType(),
            vector.crs(),
            vector.fields()
        )
        copy_layer(vector, layer)

    input_band = layer.keywords.get('active_band', 1)
    analysis = QgsZonalStatistics(
        layer,
        raster.source(),
        'exposure_',
        input_band,
        QgsZonalStatistics.Sum)
    result = analysis.calculateStatistics(None)
    LOGGER.debug(tr('Zonal stats on %s : %s' % (raster.source(), result)))

    output_field = exposure_count_field['field_name'] % exposure
    if raster.crs().authid() != vector.crs().authid():
        output_layer.startEditing()
        field = create_field_from_definition(
            exposure_count_field, exposure)

        output_layer.addAttribute(field)
        new_index = output_layer.fields().lookupField(field.name())
        old_index = layer.fields().lookupField('exposure_sum')
        for feature_input, feature_output in zip(
                layer.getFeatures(), output_layer.getFeatures()):
            output_layer.changeAttributeValue(
                feature_input.id(), new_index, feature_input[old_index])
        output_layer.commitChanges()
        layer = output_layer
    else:
        fields_to_rename = {
            'exposure_sum': output_field
        }
        if qgis_version() >= 21600:
            rename_fields(layer, fields_to_rename)
        else:
            copy_fields(layer, fields_to_rename)
            remove_fields(layer, list(fields_to_rename.keys()))
        layer.commitChanges()

    # The zonal stats is producing some None values. We need to fill these
    # with 0. See issue : #3778
    # We should start a new editing session as previous fields need to be
    # committed first.
    layer.startEditing()
    request = QgsFeatureRequest()
    expression = '\"%s\" is None' % output_field
    request.setFilterExpression(expression)
    request.setFlags(QgsFeatureRequest.NoGeometry)
    index = layer.fields().lookupField(output_field)
    for feature in layer.getFeatures():
        if feature[output_field] is None:
            layer.changeAttributeValue(feature.id(), index, 0)
    layer.commitChanges()

    layer.keywords = raster.keywords.copy()
    layer.keywords['inasafe_fields'] = vector.keywords['inasafe_fields'].copy()
    layer.keywords['inasafe_default_values'] = (
        raster.keywords['inasafe_default_values'].copy())

    key = exposure_count_field['key'] % raster.keywords['exposure']

    # Special case here, one field is the exposure count and the total.
    layer.keywords['inasafe_fields'][key] = output_field
    layer.keywords['inasafe_fields'][total_field['key']] = output_field

    layer.keywords['exposure_keywords'] = raster.keywords.copy()
    layer.keywords['hazard_keywords'] = vector.keywords[
        'hazard_keywords'].copy()
    layer.keywords['aggregation_keywords'] = (
        vector.keywords['aggregation_keywords'])
    layer.keywords['layer_purpose'] = (
        layer_purpose_aggregate_hazard_impacted['key'])

    layer.keywords['title'] = output_layer_name

    check_layer(layer)
    return layer
