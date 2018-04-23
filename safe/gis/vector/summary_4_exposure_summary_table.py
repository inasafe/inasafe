# coding=utf-8

"""Aggregate the aggregate hazard to the analysis layer."""

from numbers import Number

from qgis.core import Qgis, QgsFeatureRequest, QgsFeature

from safe.definitions.fields import (
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    exposure_type_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    total_field,
    affected_field,
    hazard_count_field,
    exposure_count_field,
    exposure_class_field,
    summary_rules,
)
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.layer_purposes import \
    layer_purpose_exposure_summary_table
from safe.definitions.processing_steps import (
    summary_4_exposure_summary_table_steps)
from safe.definitions.utilities import definition
from safe.gis.sanity_check import check_layer
from safe.gis.vector.summary_tools import (
    check_inputs, create_absolute_values_structure)
from safe.gis.vector.tools import (
    create_field_from_definition,
    read_dynamic_inasafe_field,
    create_memory_layer)
from safe.processors import post_processor_affected_function
from safe.utilities.gis import qgis_version
from safe.utilities.pivot_table import FlatTable
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def exposure_summary_table(
        aggregate_hazard, exposure_summary=None, callback=None):
    """Compute the summary from the aggregate hazard to analysis.

    Source layer :
    | haz_id | haz_class | aggr_id | aggr_name | exposure_count |

    Output layer :
    | exp_type | count_hazard_class | total |

    :param aggregate_hazard: The layer to aggregate vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param exposure_summary: The layer impact layer.
    :type exposure_summary: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new tabular table, without geometry.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_4_exposure_summary_table_steps[
        'output_layer_name']

    source_fields = aggregate_hazard.keywords['inasafe_fields']

    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field,
        affected_field,
        total_field
    ]
    check_inputs(source_compulsory_fields, source_fields)

    absolute_values = create_absolute_values_structure(
        aggregate_hazard, ['all'])

    hazard_class = source_fields[hazard_class_field['key']]
    hazard_class_index = aggregate_hazard.fieldNameIndex(hazard_class)
    unique_hazard = aggregate_hazard.uniqueValues(hazard_class_index)

    unique_exposure = read_dynamic_inasafe_field(
        source_fields, exposure_count_field)

    flat_table = FlatTable('hazard_class', 'exposure_class')

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for area in aggregate_hazard.getFeatures():
        hazard_value = area[hazard_class_index]
        for exposure in unique_exposure:
            key_name = exposure_count_field['key'] % exposure
            field_name = source_fields[key_name]
            exposure_count = area[field_name]
            if not exposure_count:
                exposure_count = 0

            flat_table.add_value(
                exposure_count,
                hazard_class=hazard_value,
                exposure_class=exposure
            )

        # We summarize every absolute values.
        for field, field_definition in list(absolute_values.items()):
            value = area[field]
            if not value or value is None:
                value = 0
            field_definition[0].add_value(
                value,
                all='all'
            )

    tabular = create_memory_layer(output_layer_name, Qgis.NoGeometry)
    tabular.startEditing()

    field = create_field_from_definition(exposure_type_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][exposure_type_field['key']] = (
        exposure_type_field['field_name'])

    hazard_keywords = aggregate_hazard.keywords['hazard_keywords']
    hazard = hazard_keywords['hazard']
    classification = hazard_keywords['classification']

    exposure_keywords = aggregate_hazard.keywords['exposure_keywords']
    exposure = exposure_keywords['exposure']

    hazard_affected = {}
    for hazard_class in unique_hazard:
        if hazard_class == '' or hazard_class is None:
            hazard_class = 'NULL'
        field = create_field_from_definition(hazard_count_field, hazard_class)
        tabular.addAttribute(field)
        key = hazard_count_field['key'] % hazard_class
        value = hazard_count_field['field_name'] % hazard_class
        tabular.keywords['inasafe_fields'][key] = value

        hazard_affected[hazard_class] = post_processor_affected_function(
            exposure=exposure,
            hazard=hazard,
            classification=classification,
            hazard_class=hazard_class
        )

    field = create_field_from_definition(total_affected_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_affected_field['key']] = (
        total_affected_field['field_name'])

    # essentially have the same value as NULL_hazard_count
    # but with this, make sure that it exists in layer so it can be used for
    # reporting, and can be referenced to fields.py to take the label.
    field = create_field_from_definition(total_not_affected_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_not_affected_field['key']] = (
        total_not_affected_field['field_name'])

    field = create_field_from_definition(total_not_exposed_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_not_exposed_field['key']] = (
        total_not_exposed_field['field_name'])

    field = create_field_from_definition(total_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    summarization_dicts = {}
    if exposure_summary:
        summarization_dicts = summarize_result(exposure_summary, callback)

    sorted_keys = sorted(summarization_dicts.keys())

    for key in sorted_keys:
        summary_field = summary_rules[key]['summary_field']
        field = create_field_from_definition(summary_field)
        tabular.addAttribute(field)
        tabular.keywords['inasafe_fields'][
            summary_field['key']] = (
            summary_field['field_name'])

    # Only add absolute value if there is no summarization / no exposure
    # classification
    if not summarization_dicts:
        # For each absolute values
        for absolute_field in list(absolute_values.keys()):
            field_definition = definition(absolute_values[absolute_field][1])
            field = create_field_from_definition(field_definition)
            tabular.addAttribute(field)
            key = field_definition['key']
            value = field_definition['field_name']
            tabular.keywords['inasafe_fields'][key] = value

    for exposure_type in unique_exposure:
        feature = QgsFeature()
        attributes = [exposure_type]
        total_affected = 0
        total_not_affected = 0
        total_not_exposed = 0
        total = 0
        for hazard_class in unique_hazard:
            if hazard_class == '' or hazard_class is None:
                hazard_class = 'NULL'
            value = flat_table.get_value(
                hazard_class=hazard_class,
                exposure_class=exposure_type
            )
            attributes.append(value)

            if hazard_affected[hazard_class] == not_exposed_class['key']:
                total_not_exposed += value
            elif hazard_affected[hazard_class]:
                total_affected += value
            else:
                total_not_affected += value

            total += value

        attributes.append(total_affected)
        attributes.append(total_not_affected)
        attributes.append(total_not_exposed)
        attributes.append(total)

        if summarization_dicts:
            for key in sorted_keys:
                attributes.append(summarization_dicts[key].get(
                    exposure_type, 0))
        else:
            for i, field in enumerate(absolute_values.values()):
                value = field[0].get_value(
                    all='all'
                )
                attributes.append(value)

        feature.setAttributes(attributes)
        tabular.addFeature(feature)

        # Sanity check ± 1 to the result. Disabled for now as it seems ± 1 is
        # not enough. ET 13/02/17
        # total_computed = (
        #     total_affected + total_not_affected + total_not_exposed)
        # if not -1 < (total_computed - total) < 1:
        #     raise ComputationError

    tabular.commitChanges()

    tabular.keywords['title'] = layer_purpose_exposure_summary_table['name']
    if qgis_version() >= 21800:
        tabular.setName(tabular.keywords['title'])
    else:
        tabular.setLayerName(tabular.keywords['title'])
    tabular.keywords['layer_purpose'] = layer_purpose_exposure_summary_table[
        'key']

    check_layer(tabular, has_geometry=False)
    return tabular


@profile
def summarize_result(exposure_summary, callback=None):
    """Extract result based on summarizer field value and sum by exposure type.

    :param exposure_summary: The layer impact layer.
    :type exposure_summary: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: Dictionary of attributes per exposure per summarizer field.
    :rtype: dict

    .. versionadded:: 4.2
    """
    summarization_dicts = {}
    summarizer_flags = {}

    # for summarizer_field in summarizer_fields:
    for key, summary_rule in list(summary_rules.items()):
        input_field = summary_rule['input_field']
        if exposure_summary.fieldNameIndex(
                input_field['field_name']) == -1:
            summarizer_flags[key] = False
        else:
            summarizer_flags[key] = True
            summarization_dicts[key] = {}

    for feature in exposure_summary.getFeatures():
        exposure_class_name = feature[exposure_class_field['field_name']]
        # for summarizer_field in summarizer_fields:
        for key, summary_rule in list(summary_rules.items()):
            input_field = summary_rule['input_field']
            case_field = summary_rule['case_field']
            case_value = feature[case_field['field_name']]

            flag = summarizer_flags[key]
            if not flag:
                continue
            if case_value in summary_rule['case_values']:
                if exposure_class_name not in summarization_dicts[key]:
                    summarization_dicts[key][exposure_class_name] = 0
                value = feature[input_field['field_name']]
                if isinstance(value, Number):
                    summarization_dicts[key][exposure_class_name] += value

    return summarization_dicts
