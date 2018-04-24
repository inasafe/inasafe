# coding=utf-8

"""Multi-exposure summary calculation."""


from qgis.core import QgsFeatureRequest

from safe.definitions.constants import MULTI_EXPOSURE_ANALYSIS_FLAG
from safe.definitions.extra_keywords import extra_keyword_analysis_type
from safe.definitions.fields import (
    aggregation_id_field,
    affected_exposure_count_field,
    exposure_affected_exposure_type_count_field,
    hazard_count_field,
    exposure_hazard_count_field,
    total_affected_field,
    exposure_total_affected_field,
    total_not_affected_field,
    exposure_total_not_affected_field,
    total_exposed_field,
    exposure_total_exposed_field,
    total_not_exposed_field,
    exposure_total_not_exposed_field,
    total_field,
    exposure_total_field,
)
from safe.definitions.layer_purposes import (
    layer_purpose_analysis_impacted,
    layer_purpose_aggregation_summary,
)
from safe.gis.vector.tools import (
    create_field_from_definition,
    read_dynamic_inasafe_field,
)
from safe.utilities.gis import qgis_version

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def multi_exposure_analysis_summary(analysis, intermediate_analysis):
    """Merge intermediate analysis into one analysis summary.

    List of analysis layers like:
    | analysis_id | count_hazard_class | affected_count | total |

    Target layer :
    | analysis_id |

    Output layer :
    | analysis_id | count_hazard_class | affected_count | total |

    :param analysis: The target vector layer where to write statistics.
    :type analysis: QgsVectorLayer

    :param intermediate_analysis: List of analysis layer for a single exposure.
    :type intermediate_analysis: list

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.3
    """
    analysis.startEditing()

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    target_id = next(analysis.getFeatures(request)).id()

    for analysis_result in intermediate_analysis:
        exposure = analysis_result.keywords['exposure_keywords']['exposure']

        iterator = analysis_result.getFeatures(request)
        feature = next(iterator)

        source_fields = analysis_result.keywords['inasafe_fields']

        # Dynamic fields
        hazards = read_dynamic_inasafe_field(source_fields, hazard_count_field)
        for hazard_zone in hazards:
            field = create_field_from_definition(
                exposure_hazard_count_field, exposure, hazard_zone)
            analysis.addAttribute(field)
            index = analysis.fields().lookupField(field.name())
            value = feature[analysis_result.fields().lookupField()(
                hazard_count_field['field_name'] % hazard_zone)]
            analysis.changeAttributeValue(target_id, index, value)
            # keywords
            key = exposure_hazard_count_field['key'] % (exposure, hazard_zone)
            value = exposure_hazard_count_field['field_name'] % (
                exposure, hazard_zone)
            analysis.keywords['inasafe_fields'][key] = value

        # total affected
        source_index = analysis_result.fields().lookupField()(
            total_affected_field['field_name'])
        field = create_field_from_definition(
            exposure_total_affected_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fields().lookupField(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_affected_field['key'] % exposure
        value = exposure_total_affected_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total not affected
        source_index = analysis_result.fields().lookupField()(
            total_not_affected_field['field_name'])
        field = create_field_from_definition(
            exposure_total_not_affected_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fields().lookupField(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_not_affected_field['key'] % exposure
        value = exposure_total_not_affected_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total exposed
        source_index = analysis_result.fields().lookupField()(
            total_exposed_field['field_name'])
        field = create_field_from_definition(
            exposure_total_exposed_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fields().lookupField(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_exposed_field['key'] % exposure
        value = exposure_total_exposed_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total not exposed
        source_index = analysis_result.fields().lookupField()(
            total_not_exposed_field['field_name'])
        field = create_field_from_definition(
            exposure_total_not_exposed_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fields().lookupField(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_not_exposed_field['key'] % exposure
        value = exposure_total_not_exposed_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total
        source_index = analysis_result.fields().lookupField()(
            total_field['field_name'])
        field = create_field_from_definition(
            exposure_total_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fields().lookupField(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_field['key'] % exposure
        value = exposure_total_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

    analysis.commitChanges()
    analysis.keywords['title'] = (
        layer_purpose_analysis_impacted['multi_exposure_name'])
    analysis.keywords['layer_purpose'] = layer_purpose_analysis_impacted['key']

    # Set up the extra keywords so everyone knows it's a
    # multi exposure analysis result.
    extra_keywords = {
        extra_keyword_analysis_type['key']: MULTI_EXPOSURE_ANALYSIS_FLAG
    }
    analysis.keywords['extra_keywords'] = extra_keywords

    if qgis_version() >= 21600:
        analysis.setName(analysis.keywords['title'])
    else:
        analysis.setLayerName(analysis.keywords['title'])
    return analysis


def multi_exposure_aggregation_summary(aggregation, intermediate_layers):
    """Merge intermediate aggregations into one aggregation summary.

    Source layer :
    | aggr_id | aggr_name | count of affected features per exposure type

    Target layer :
    | aggregation_id | aggregation_name |

    Output layer :
    | aggr_id | aggr_name | count of affected per exposure type for each

    :param aggregation: The target vector layer where to write statistics.
    :type aggregation: QgsVectorLayer

    :param intermediate_layers: List of aggregation layer for a single exposure
    :type intermediate_layers: list

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.3
    """
    target_index_field_name = (
        aggregation.keywords['inasafe_fields'][aggregation_id_field['key']])

    aggregation.startEditing()

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for layer in intermediate_layers:
        source_fields = layer.keywords['inasafe_fields']
        exposure = layer.keywords['exposure_keywords']['exposure']
        unique_exposure = read_dynamic_inasafe_field(
            source_fields,
            affected_exposure_count_field,
            [total_affected_field])
        field_map = {}

        for exposure_class in unique_exposure:
            field = create_field_from_definition(
                exposure_affected_exposure_type_count_field,
                name=exposure, sub_name=exposure_class
            )
            aggregation.addAttribute(field)
            source_field_index = layer.fields().lookupField()(
                affected_exposure_count_field['field_name'] % exposure_class)
            target_field_index = aggregation.fields().lookupField(field.name())
            field_map[source_field_index] = target_field_index

        # Total affected field
        field = create_field_from_definition(
            exposure_total_not_affected_field, exposure)
        aggregation.addAttribute(field)
        source_field_index = layer.fields().lookupField()(
            total_affected_field['field_name'])
        target_field_index = aggregation.fields().lookupField(field.name())
        field_map[source_field_index] = target_field_index

        # Get Aggregation ID from original feature
        index = (
            layer.fields().lookupField(source_fields[aggregation_id_field['key']]))

        for source_feature in layer.getFeatures(request):
            target_expression = QgsFeatureRequest()
            target_expression.setFlags(QgsFeatureRequest.NoGeometry)
            expression = '\"{field_name}\" = {id_value}'.format(
                field_name=target_index_field_name,
                id_value=source_feature[index])
            target_expression.setFilterExpression(expression)
            iterator = aggregation.getFeatures(target_expression)
            target_feature = next(iterator)  # It must return only 1 feature.

            for source_field, target_field in list(field_map.items()):
                aggregation.changeAttributeValue(
                    target_feature.id(),
                    target_field,
                    source_feature[source_field])

            try:
                next(iterator)
            except StopIteration:
                # Everything is fine, it's normal.
                pass
            else:
                # This should never happen ! IDs are duplicated in the
                # aggregation layer.
                raise Exception(
                    'Aggregation IDs are duplicated in the aggregation layer. '
                    'We can\'t make any joins.')

    aggregation.commitChanges()
    aggregation.keywords['title'] = (
        layer_purpose_aggregation_summary['multi_exposure_name'])
    aggregation.keywords['layer_purpose'] = (
        layer_purpose_aggregation_summary['key'])

    # Set up the extra keywords so everyone knows it's a
    # multi exposure analysis result.
    extra_keywords = {
        extra_keyword_analysis_type['key']: MULTI_EXPOSURE_ANALYSIS_FLAG
    }
    aggregation.keywords['extra_keywords'] = extra_keywords

    if qgis_version() >= 21600:
        aggregation.setName(aggregation.keywords['title'])
    else:
        aggregation.setLayerName(aggregation.keywords['title'])
    return aggregation
