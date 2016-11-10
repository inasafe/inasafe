# coding=utf-8

"""
Aggregate the aggregate hazard to the analysis layer.
"""

from PyQt4.QtCore import QPyNullVariant
from qgis.core import QGis, QgsFeatureRequest

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    analysis_id_field,
    analysis_name_field,
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    total_field,
    total_affected_field,
    hazard_count_field,
)
from safe.definitionsv4.processing_steps import (
    summary_3_analysis_steps)
from safe.definitionsv4.post_processors import post_processor_affected_function
from safe.gisv4.vector.tools import create_field_from_definition
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def analysis_summary(aggregate_hazard, analysis, callback=None):
    """Compute the summary from the aggregate hazard to analysis.

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
        Defaults to None.
    :type callback: function

    :return: The new target layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_3_analysis_steps['output_layer_name']
    processing_step = summary_3_analysis_steps['step_name']

    source_fields = aggregate_hazard.keywords['inasafe_fields']
    target_fields = analysis.keywords['inasafe_fields']

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
    hazard_class_index = aggregate_hazard.fieldNameIndex(hazard_class)
    unique_hazard = aggregate_hazard.uniqueValues(hazard_class_index)

    hazard_keywords = aggregate_hazard.keywords['hazard_keywords']
    classification = hazard_keywords['classification']

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
        if not value or isinstance(value, QPyNullVariant):
            value = 0
        if not hazard_value or isinstance(hazard_value, QPyNullVariant):
            hazard_value = 'NULL'
        flat_table.add_value(
            value,
            hazard_class=hazard_value
        )

    analysis.startEditing()

    shift = analysis.fields().count()

    for column in unique_hazard:
        if not column or isinstance(column, QPyNullVariant):
            column = 'NULL'
        field = create_field_from_definition(hazard_count_field, column)
        analysis.addAttribute(field)
        key = hazard_count_field['key'] % column
        value = hazard_count_field['field_name'] % column
        analysis.keywords['inasafe_fields'][key] = value

    field = create_field_from_definition(total_affected_field)
    analysis.addAttribute(field)
    analysis.keywords['inasafe_fields'][total_affected_field['key']] = (
        total_affected_field['field_name'])

    field = create_field_from_definition(total_field)
    analysis.addAttribute(field)
    analysis.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    affected_sum = 0
    for area in analysis.getFeatures(request):
        total = 0
        for i, val in enumerate(unique_hazard):
            if not val or isinstance(val, QPyNullVariant):
                val = 'NULL'
            sum = flat_table.get_value(hazard_class=val)
            total += sum
            analysis.changeAttributeValue(area.id(), shift + i, sum)

            affected = post_processor_affected_function(
                    classification=classification, hazard_class=val)
            if affected:
                affected_sum += sum

        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard), affected_sum)

        analysis.changeAttributeValue(
            area.id(), shift + len(unique_hazard) + 1, total)

    analysis.commitChanges()

    analysis.keywords['title'] = output_layer_name

    return analysis
