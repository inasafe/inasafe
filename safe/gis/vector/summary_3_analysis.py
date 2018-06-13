# coding=utf-8

"""Aggregate the aggregate hazard to the analysis layer."""

from math import isnan

from qgis.core import QgsFeatureRequest

from safe.definitions.fields import (
    analysis_name_field,
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    total_exposed_field,
    total_field,
    hazard_count_field,
    summary_rules,
)
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.layer_purposes import layer_purpose_analysis_impacted
from safe.gis.sanity_check import check_layer
from safe.gis.vector.summary_tools import (
    check_inputs, create_absolute_values_structure, add_fields)
from safe.gis.vector.tools import create_field_from_definition
from safe.processors import post_processor_affected_function
from safe.utilities.gis import qgis_version
from safe.utilities.pivot_table import FlatTable
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def analysis_summary(aggregate_hazard, analysis):
    """Compute the summary from the aggregate hazard to analysis.

    Source layer :
    | haz_id | haz_class | aggr_id | aggr_name | total_feature |

    Target layer :
    | analysis_name |

    Output layer :
    | analysis_name | count_hazard_class | affected_count | total |

    :param aggregate_hazard: The layer to aggregate vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param analysis: The target vector layer where to write statistics.
    :type analysis: QgsVectorLayer

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    source_fields = aggregate_hazard.keywords['inasafe_fields']
    target_fields = analysis.keywords['inasafe_fields']

    target_compulsory_fields = [
        analysis_name_field,
    ]
    check_inputs(target_compulsory_fields, target_fields)

    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field,
        total_field
    ]
    check_inputs(source_compulsory_fields, source_fields)

    absolute_values = create_absolute_values_structure(
        aggregate_hazard, ['all'])

    hazard_class = source_fields[hazard_class_field['key']]
    hazard_class_index = aggregate_hazard.fields().lookupField(hazard_class)
    unique_hazard = list(aggregate_hazard.uniqueValues(hazard_class_index))

    hazard_keywords = aggregate_hazard.keywords['hazard_keywords']
    hazard = hazard_keywords['hazard']
    classification = hazard_keywords['classification']

    exposure_keywords = aggregate_hazard.keywords['exposure_keywords']
    exposure = exposure_keywords['exposure']

    total = source_fields[total_field['key']]

    flat_table = FlatTable('hazard_class')

    # First loop over the aggregate_hazard layer
    request = QgsFeatureRequest()
    request.setSubsetOfAttributes(
        [hazard_class, total], aggregate_hazard.fields())
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for area in aggregate_hazard.getFeatures():
        hazard_value = area[hazard_class_index]
        value = area[total]
        if (value == '' or value is None or isnan(value) or
                (hasattr(value, 'isNull') and value.isNull())):
            # For isnan, see ticket #3812
            value = 0
        if (hazard_value == '' or hazard_value is None or
                (hasattr(hazard_value, 'isNull') and
                    hazard_value.isNull())):
            hazard_value = 'NULL'
        flat_table.add_value(
            value,
            hazard_class=hazard_value
        )

        # We summarize every absolute values.
        for field, field_definition in list(absolute_values.items()):
            value = area[field]
            if (value == '' or value is None or
                    (hasattr(value, 'isNull') and value.isNull())):
                value = 0
            field_definition[0].add_value(
                value,
                all='all'
            )

    analysis.startEditing()

    shift = analysis.fields().count()

    counts = [
        total_affected_field,
        total_not_affected_field,
        total_exposed_field,
        total_not_exposed_field,
        total_field]

    dynamic_structure = [
        [hazard_count_field, unique_hazard],
    ]
    add_fields(
        analysis,
        absolute_values,
        counts,
        dynamic_structure)

    affected_sum = 0
    not_affected_sum = 0
    not_exposed_sum = 0

    # Summarization
    summary_values = {}
    for key, summary_rule in list(summary_rules.items()):
        input_field = summary_rule['input_field']
        case_field = summary_rule['case_field']
        if aggregate_hazard.fields().lookupField(input_field['field_name']) == -1:
            continue
        if aggregate_hazard.fields().lookupField(case_field['field_name']) == -1:
            continue

        summary_value = 0
        for area in aggregate_hazard.getFeatures():
            case_value = area[case_field['field_name']]
            if case_value in summary_rule['case_values']:
                summary_value += area[input_field['field_name']]

        summary_values[key] = summary_value

    for area in analysis.getFeatures(request):
        total = 0
        for i, val in enumerate(unique_hazard):
            if (val == '' or val is None or
                    (hasattr(val, 'isNull') and val.isNull())):
                val = 'NULL'
            sum = flat_table.get_value(hazard_class=val)
            total += sum
            analysis.changeAttributeValue(area.id(), shift + i, sum)

            affected = post_processor_affected_function(
                exposure=exposure,
                hazard=hazard,
                classification=classification,
                hazard_class=val)
            if affected == not_exposed_class['key']:
                not_exposed_sum += sum
            elif affected:
                affected_sum += sum
            else:
                not_affected_sum += sum

        # Total Affected field
        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard), affected_sum)

        # Total Not affected field
        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 1, not_affected_sum)

        # Total Exposed field
        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 2, total - not_exposed_sum)

        # Total Not exposed field
        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 3, not_exposed_sum)

        # Total field
        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 4, total)

        # Any absolute postprocessors
        for i, field in enumerate(absolute_values.values()):
            value = field[0].get_value(
                all='all'
            )
            analysis.changeAttributeValue(
                area.id(), shift + len(unique_hazard) + 5 + i, value)

        # Summarizer of custom attributes
        for key, summary_value in list(summary_values.items()):
            summary_field = summary_rules[key]['summary_field']
            field = create_field_from_definition(summary_field)
            analysis.addAttribute(field)
            field_index = analysis.fields().lookupField(field.name())
            # noinspection PyTypeChecker
            analysis.keywords['inasafe_fields'][summary_field['key']] = (
                summary_field['field_name'])

            analysis.changeAttributeValue(
                area.id(), field_index, summary_value)

    # Sanity check ± 1 to the result. Disabled for now as it seems ± 1 is not
    # enough. ET 13/02/17
    # total_computed = (
    #     affected_sum + not_affected_sum + not_exposed_sum)
    # if not -1 < (total_computed - total) < 1:
    #     raise ComputationError

    analysis.commitChanges()

    analysis.keywords['title'] = layer_purpose_analysis_impacted['name']
    if qgis_version() >= 21600:
        analysis.setName(analysis.keywords['title'])
    else:
        analysis.setLayerName(analysis.keywords['title'])
    analysis.keywords['layer_purpose'] = layer_purpose_analysis_impacted['key']

    check_layer(analysis)
    return analysis
