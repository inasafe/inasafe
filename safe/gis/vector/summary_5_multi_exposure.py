# coding=utf-8

"""Multi-exposure summary calculation."""

from qgis.core import QgsFeatureRequest

from safe.definitions.fields import (
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
from safe.gis.vector.tools import (
    create_field_from_definition,
    read_dynamic_inasafe_field,
)

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
            index = analysis.fieldNameIndex(field.name())
            value = feature[analysis_result.fieldNameIndex(
                hazard_count_field['field_name'] % hazard_zone)]
            analysis.changeAttributeValue(target_id, index, value)
            # keywords
            key = exposure_hazard_count_field['key'] % (exposure, hazard_zone)
            value = exposure_hazard_count_field['field_name'] % (
                exposure, hazard_zone)
            analysis.keywords['inasafe_fields'][key] = value

        # total affected
        source_index = analysis_result.fieldNameIndex(
            total_affected_field['field_name'])
        field = create_field_from_definition(
            exposure_total_affected_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fieldNameIndex(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_affected_field['key'] % exposure
        value = exposure_total_affected_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total not affected
        source_index = analysis_result.fieldNameIndex(
            total_not_affected_field['field_name'])
        field = create_field_from_definition(
            exposure_total_not_affected_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fieldNameIndex(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_not_affected_field['key'] % exposure
        value = exposure_total_not_affected_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total exposed
        source_index = analysis_result.fieldNameIndex(
            total_exposed_field['field_name'])
        field = create_field_from_definition(
            exposure_total_exposed_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fieldNameIndex(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_exposed_field['key'] % exposure
        value = exposure_total_exposed_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total not exposed
        source_index = analysis_result.fieldNameIndex(
            total_not_exposed_field['field_name'])
        field = create_field_from_definition(
            exposure_total_not_exposed_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fieldNameIndex(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_not_exposed_field['key'] % exposure
        value = exposure_total_not_exposed_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

        # total
        source_index = analysis_result.fieldNameIndex(
            total_field['field_name'])
        field = create_field_from_definition(
            exposure_total_field, exposure)
        analysis.addAttribute(field)
        index = analysis.fieldNameIndex(field.name())
        analysis.changeAttributeValue(target_id, index, feature[source_index])
        # keywords
        key = exposure_total_field['key'] % exposure
        value = exposure_total_field['field_name'] % exposure
        analysis.keywords['inasafe_fields'][key] = value

    analysis.commitChanges()
    return analysis


def multi_exposure_aggregation_summary(aggregation, intermediate_aggregations):
    """Merge intermediate aggregations into one aggregation summary.

    Source layer :
    | haz_id | haz_class | aggr_id | aggr_name | total_feature |

    Target layer :
    | analysis_id |

    Output layer :
    | analysis_id | count_hazard_class | affected_count | total |

    :param aggregate_hazard: The layer to aggregate vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param analysis: The target vector layer where to write statistics.
    :type analysis: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.summary_5_multi_exposure.py
    :type callback: function

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.3
    """
    # output_layer_name = summary_3_analysis_steps['output_layer_name']  # NOQA
    # processing_step = summary_3_analysis_steps['step_name']  # NOQA

    return aggregation
