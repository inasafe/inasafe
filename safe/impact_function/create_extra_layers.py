# coding=utf-8

"""Create extra layers in the impact function."""

import logging

from qgis.core import (
    QgsFeature,
    QgsWkbTypes,
)

from safe.definitions.constants import inasafe_keyword_version_key
from safe.definitions.fields import (
    aggregation_id_field,
    aggregation_name_field,
    analysis_name_field,
    profiling_function_field,
    profiling_time_field,
    profiling_memory_field
)
from safe.definitions.layer_purposes import (
    layer_purpose_profiling,
    layer_purpose_aggregation,
    layer_purpose_analysis_impacted,
)
from safe.definitions.versions import inasafe_keyword_version
from safe.gis.vector.tools import (
    create_memory_layer, create_field_from_definition, copy_layer)
from safe.utilities.gis import qgis_version
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile
from safe.utilities.settings import setting

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def create_virtual_aggregation(geometry, crs):
    """Function to create aggregation layer based on extent.

    :param geometry: The geometry to use as an extent.
    :type geometry: QgsGeometry

    :param crs: The Coordinate Reference System to use for the layer.
    :type crs: QgsCoordinateReferenceSystem

    :returns: A polygon layer with exposure's crs.
    :rtype: QgsVectorLayer
    """
    fields = [
        create_field_from_definition(aggregation_id_field),
        create_field_from_definition(aggregation_name_field)
    ]
    aggregation_layer = create_memory_layer(
        'aggregation', QgsWkbTypes.Polygon, crs, fields)

    aggregation_layer.startEditing()

    feature = QgsFeature()
    feature.setGeometry(geometry)
    feature.setAttributes([1, tr('Entire Area')])
    aggregation_layer.addFeature(feature)
    aggregation_layer.commitChanges()

    # Generate aggregation keywords
    aggregation_layer.keywords['layer_purpose'] = (
        layer_purpose_aggregation['key'])
    aggregation_layer.keywords['title'] = 'aggr_from_bbox'
    aggregation_layer.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)
    aggregation_layer.keywords['inasafe_fields'] = {
        aggregation_id_field['key']: aggregation_id_field['field_name'],
        aggregation_name_field['key']: aggregation_name_field['field_name']
    }
    # We will fill default values later, according to the exposure.
    aggregation_layer.keywords['inasafe_default_values'] = {}

    return aggregation_layer


@profile
def create_analysis_layer(analysis_extent, crs, name):
    """Create the analysis layer.

    :param analysis_extent: The analysis extent.
    :type analysis_extent: QgsGeometry

    :param crs: The CRS to use.
    :type crs: QgsCoordinateReferenceSystem

    :param name: The name of the analysis.
    :type name: basestring

    :returns: A polygon layer with exposure's crs.
    :rtype: QgsVectorLayer
    """
    fields = [
        create_field_from_definition(analysis_name_field)
    ]
    analysis_layer = create_memory_layer(
        'analysis', QgsWkbTypes.Polygon, crs, fields)

    analysis_layer.startEditing()

    feature = QgsFeature()
    # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
    feature.setGeometry(analysis_extent)
    feature.setAttributes([name])
    analysis_layer.addFeature(feature)
    analysis_layer.commitChanges()

    # Generate analysis keywords
    analysis_layer.keywords['layer_purpose'] = (
        layer_purpose_analysis_impacted['key'])
    analysis_layer.keywords['title'] = 'analysis'
    analysis_layer.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)
    analysis_layer.keywords['inasafe_fields'] = {
        analysis_name_field['key']: analysis_name_field['field_name']
    }

    return analysis_layer


def create_profile_layer(profiling):
    """Create a tabular layer with the profiling.

    :param profiling: A dict containing benchmarking data.
    :type profiling: safe.messaging.message.Message

    :return: A tabular layer.
    :rtype: QgsVectorLayer
    """
    fields = [
        create_field_from_definition(profiling_function_field),
        create_field_from_definition(profiling_time_field)
    ]
    if setting(key='memory_profile', expected_type=bool):
        fields.append(create_field_from_definition(profiling_memory_field))
    tabular = create_memory_layer(
        'profiling',
        QgsWkbTypes.NoGeometry,
        fields=fields)

    # Generate profiling keywords
    tabular.keywords['layer_purpose'] = layer_purpose_profiling['key']
    tabular.keywords['title'] = layer_purpose_profiling['name']
    if qgis_version() >= 21800:
        tabular.setName(tabular.keywords['title'])
    else:
        tabular.setLayerName(tabular.keywords['title'])
    tabular.keywords['inasafe_fields'] = {
        profiling_function_field['key']:
            profiling_function_field['field_name'],
        profiling_time_field['key']:
            profiling_time_field['field_name'],
    }
    if setting(key='memory_profile', expected_type=bool):
        tabular.keywords['inasafe_fields'][
            profiling_memory_field['key']] = profiling_memory_field[
            'field_name']
    tabular.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)

    table = profiling.to_text().splitlines()[3:]
    tabular.startEditing()
    for line in table:
        feature = QgsFeature()
        items = line.split(', ')
        time = items[1].replace('-', '')
        if setting(key='memory_profile', expected_type=bool):
            memory = items[2].replace('-', '')
            feature.setAttributes([items[0], time, memory])
        else:
            feature.setAttributes([items[0], time])
        tabular.addFeature(feature)

    tabular.commitChanges()
    return tabular


def create_valid_aggregation(layer):
    """Create a local copy of the aggregation layer and try to make it valid.

    We need to make the layer valid if we can. We got some issues with
    DKI Jakarta dataset : Districts and Subdistricts layers.
    See issue : https://github.com/inasafe/inasafe/issues/3713

    :param layer: The aggregation layer.
    :type layer: QgsVectorLayer

    :return: The new aggregation layer in memory.
    :rtype: QgsVectorLayer
    """
    cleaned = create_memory_layer(
        'aggregation', layer.geometryType(), layer.crs(), layer.fields())

    # We transfer keywords to the output.
    cleaned.keywords = layer.keywords

    try:
        use_selected_only = layer.use_selected_features_only
    except AttributeError:
        use_selected_only = False

    cleaned.use_selected_features_only = use_selected_only

    copy_layer(layer, cleaned)
    return cleaned
