# coding=utf-8
"""
Impact function
"""

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsGeometry,
    QgsFeature,
    QGis,
)

from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
    analysis_id_field,
    analysis_name_field,
    profiling_function_field,
    profiling_time_field
)
from safe.definitionsv4.constants import inasafe_keyword_version_key
from safe.definitionsv4.versions import inasafe_keyword_version
from safe.gisv4.vector.tools import (
    create_memory_layer, create_field_from_definition)
from safe.utilities.profiling import profile
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def create_virtual_aggregation(extent, extent_crs):
    """Function to create aggregation layer based on extent

    :returns: A polygon layer with exposure's crs.
    :rtype: QgsVectorLayer
    """

    fields = [
        create_field_from_definition(aggregation_id_field),
        create_field_from_definition(aggregation_name_field)
    ]
    aggregation_layer = create_memory_layer(
        'aggregation', QGis.Polygon, extent_crs, fields)

    aggregation_layer.startEditing()

    feature = QgsFeature()
    # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
    feature.setGeometry(QgsGeometry.fromRect(extent))
    feature.setAttributes([1, tr('Entire Area')])
    aggregation_layer.addFeature(feature)
    aggregation_layer.commitChanges()

    # Generate aggregation keywords
    aggregation_layer.keywords['layer_purpose'] = 'aggregation'
    aggregation_layer.keywords['title'] = 'aggr_from_bbox'
    aggregation_layer.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)
    aggregation_layer.keywords['inasafe_fields'] = {
        aggregation_id_field['key']: aggregation_id_field['field_name'],
        aggregation_name_field['key']: aggregation_name_field['field_name']
    }

    return aggregation_layer


@profile
def create_analysis_layer(aggregation, crs, name):
    """Create the analysis layer.

    :param aggregation: The aggregation layer.
    :type aggregation: QgsVectorLayer

    :param crs: The CRS to use.
    :type crs: QgsCoordinateReferenceSystem

    :param name: The name of the analysis.
    :type name: basestring

    :returns: A polygon layer with exposure's crs.
    :rtype: QgsVectorLayer
    """
    fields = [
        create_field_from_definition(analysis_id_field),
        create_field_from_definition(analysis_name_field)
    ]
    analysis_layer = create_memory_layer(
        'analysis', QGis.Polygon, crs, fields)

    analysis_layer.startEditing()

    geometries = []
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    for area in aggregation.getFeatures(request):
        geometries.append(QgsGeometry(area.geometry()))

    feature = QgsFeature()
    # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
    feature.setGeometry(QgsGeometry.unaryUnion(geometries))
    feature.setAttributes([1, name])
    analysis_layer.addFeature(feature)
    analysis_layer.commitChanges()

    # Generate analysis keywords
    analysis_layer.keywords['layer_purpose'] = 'analysis'
    analysis_layer.keywords['title'] = 'analysis'
    analysis_layer.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)
    analysis_layer.keywords['inasafe_fields'] = {
        analysis_id_field['key']: analysis_id_field['field_name'],
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
    tabular = create_memory_layer('profiling', QGis.NoGeometry, fields=fields)

    # Generate profiling keywords
    tabular.keywords['layer_purpose'] = 'profiling'
    tabular.keywords['title'] = 'profiling'
    tabular.keywords['inasafe_fields'] = {
        profiling_function_field['key']:
            profiling_function_field['field_name'],
        profiling_time_field['key']:
            profiling_time_field['field_name']
    }
    tabular.keywords[inasafe_keyword_version_key] = (
        inasafe_keyword_version)

    table = profiling.to_text().splitlines()[3:]
    tabular.startEditing()
    for line in table:
        feature = QgsFeature()
        items = line.split(', ')
        time = items[1].replace('-', '')
        feature.setAttributes([items[0], time])
        tabular.addFeature(feature)

    tabular.commitChanges()
    tabular.keywords['title'] = 'profiling'

    return tabular
