# coding=utf-8

"""
Aggregate the impact table to the aggregate hazard.
"""

from qgis.core import QGis, QgsField, QgsFeatureRequest

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    analysis_id_field,
    analysis_name_field,
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    total_field,
    affected_count_field,
    hazard_count_field,
)
from safe.definitionsv4.processing_steps import (
    summary_3_aggregate_hazard_steps)
from safe.definitionsv4.post_processors import post_processor_affected_function
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def analysis_summary(source, target, callback=None):
    """Compute the summary from the aggregate hazard to analysis.

    :param source: The layer to aggregate vector layer.
    :type source: QgsVectorLayer

    :param target: The target vector layer where to write statistics.
    :type target: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_3_aggregate_hazard_steps['output_layer_name']
    processing_step = summary_3_aggregate_hazard_steps['step_name']

    source_fields = source.keywords['inasafe_fields']
    target_fields = target.keywords['inasafe_fields']

    target_compulsory_fields = [
        analysis_id_field,
        analysis_name_field,
    ]
    for field in target_compulsory_fields:
        # noinspection PyTypeChecker
        if not target_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], target_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field,
        total_field
    ]
    for field in source_compulsory_fields:
        # noinspection PyTypeChecker
        if not source_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], source_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    hazard_class = source_fields[hazard_class_field['key']]
    hazard_class_index = source.fieldNameIndex(hazard_class)
    unique_hazard = source.uniqueValues(hazard_class_index)

    classification = source.keywords['hazard_keywords']['classification']

    total = source_fields[total_field['key']]

    flat_table = FlatTable('hazard_class')

    request = QgsFeatureRequest()
    request.setSubsetOfAttributes([hazard_class, total], source.fields())
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for area in source.getFeatures():
        flat_table.add_value(
            area[total],
            hazard_class=area[hazard_class_index]
        )

    target.startEditing()

    shift = target.fields().count()

    for column in unique_hazard:
        field = QgsField(hazard_count_field['field_name'] % column)
        field.setType(hazard_count_field['type'])
        field.setLength(hazard_count_field['length'])
        field.setPrecision(hazard_count_field['precision'])
        target.addAttribute(field)

    field = QgsField(affected_count_field['field_name'])
    field.setType(affected_count_field['type'])
    field.setLength(affected_count_field['length'])
    field.setPrecision(affected_count_field['precision'])
    target.addAttribute(field)

    field = QgsField(total_field['field_name'])
    field.setType(total_field['type'])
    field.setLength(total_field['length'])
    field.setPrecision(total_field['precision'])
    target.addAttribute(field)

    affected_sum = 0
    for area in target.getFeatures(request):
        total = 0
        for i, val in enumerate(unique_hazard):
            sum = flat_table.get_value(hazard_class=val)
            total += sum
            target.changeAttributeValue(area.id(), shift + i, sum)

            affected = post_processor_affected_function(
                    classification=classification, hazard_class=val)
            if affected:
                affected_sum += sum

        target.changeAttributeValue(
            area.id(), shift + len(unique_hazard), affected_sum)

        target.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 1, total)

    target.commitChanges()

    target.keywords['inasafe_fields'][affected_count_field['key']] = (
        affected_count_field['field_name'])
    target.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    for column in unique_hazard:
        key = hazard_count_field['key'] % column
        value = hazard_count_field['field_name'] % column
        target.keywords['inasafe_fields'][key] = value

    target.keywords['title'] = output_layer_name

    return target
