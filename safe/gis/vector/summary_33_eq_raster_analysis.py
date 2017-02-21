# coding=utf-8

"""Aggregate the aggregation layer to the analysis layer."""

from PyQt4.QtCore import QPyNullVariant
from qgis.core import QGis, QgsFeatureRequest

from safe.definitions.utilities import definition
from safe.definitions.fields import (
    analysis_id_field,
    analysis_name_field,
    aggregation_id_field,
    aggregation_name_field,
    displaced_field,
    fatalities_field,
    population_count_field,
    count_fields,
    hazard_count_field,
    population_exposed_per_mmi_field,
)
from safe.definitions.processing_steps import (
    summary_3_analysis_steps)
from safe.definitions.layer_purposes import layer_purpose_analysis_impacted
from safe.impact_function.earthquake import from_mmi_to_hazard_class
from safe.gis.vector.summary_tools import check_inputs
from safe.gis.vector.tools import create_field_from_definition
from safe.gis.sanity_check import check_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def analysis_eartquake_summary(aggregation, analysis, callback=None):
    """Compute the summary from the aggregation to the analysis.

    Source layer :
    | aggr_id | aggr_name | total_feature | total_displaced | total_fatalities

    Target layer :
    | analysis_id |

    Output layer :
    | analysis_id | total_feature | total_displaced | total_fatalities |

    :param aggregation: The layer to aggregate vector layer.
    :type aggregation: QgsVectorLayer

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

    source_fields = aggregation.keywords['inasafe_fields']
    target_fields = analysis.keywords['inasafe_fields']

    target_compulsory_fields = [
        analysis_id_field,
        analysis_name_field,
    ]
    check_inputs(target_compulsory_fields, target_fields)

    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        population_count_field,
        fatalities_field,
        displaced_field,
    ]
    check_inputs(source_compulsory_fields, source_fields)

    analysis.startEditing()

    count_hazard_level = {}
    index_hazard_level = {}
    classification = definition(
        aggregation.keywords['hazard_keywords']['classification'])
    hazard_classes = classification['classes']
    for hazard_class in hazard_classes:
        key = hazard_class['key']
        new_field = create_field_from_definition(hazard_count_field, key)
        analysis.addAttribute(new_field)
        new_index = analysis.fieldNameIndex(new_field.name())
        count_hazard_level[key] = 0
        index_hazard_level[key] = new_index
        target_fields[hazard_count_field['key'] % key] = (
            hazard_count_field['field_name'] % key)

    summaries = {}
    # Summary is a dictionary with a tuple a key and the value to write in
    # the output layer as a value.
    # tuple (index in the aggregation layer, index in the analysis layer) : val
    for layer_field in source_fields:
        for definition_field in count_fields:
            if layer_field == definition_field['key']:
                field_name = source_fields[layer_field]
                index = aggregation.fieldNameIndex(field_name)
                new_field = create_field_from_definition(definition_field)
                analysis.addAttribute(new_field)
                new_index = analysis.fieldNameIndex(new_field.name())
                summaries[(index, new_index)] = 0
                target_fields[definition_field['key']] = (
                    definition_field['field_name'])

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for area in aggregation.getFeatures():
        for index in summaries.keys():
            summaries[index] += area[index[0]]
        for mmi_level in range(2, 11):
            field_name = (
                population_exposed_per_mmi_field['field_name'] % mmi_level)
            index = aggregation.fieldNameIndex(field_name)
            if index > 0:
                value = area[index]
                if not value or isinstance(value, QPyNullVariant):
                    value = 0
                hazard_class = from_mmi_to_hazard_class(
                    mmi_level, classification['key'])
                if hazard_class:
                    count_hazard_level[hazard_class] += value

    for row in analysis.getFeatures():
        # We should have only one row in the analysis layer.
        for field in summaries.keys():
            analysis.changeAttributeValue(
                row.id(),
                field[1],
                summaries[field])

        for hazard_level, index in index_hazard_level.iteritems():
            analysis.changeAttributeValue(
                row.id(),
                index,
                count_hazard_level[hazard_level])

    analysis.commitChanges()

    analysis.keywords['title'] = output_layer_name
    analysis.keywords['layer_purpose'] = layer_purpose_analysis_impacted['key']
    analysis.keywords['hazard_keywords'] = dict(
        aggregation.keywords['hazard_keywords'])
    analysis.keywords['exposure_keywords'] = dict(
        aggregation.keywords['exposure_keywords'])

    check_layer(analysis)
    return analysis
