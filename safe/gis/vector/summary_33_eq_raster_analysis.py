# coding=utf-8

"""Aggregate the aggregation layer to the analysis layer."""

from qgis.core import QGis, QgsFeatureRequest

from safe.definitions.fields import (
    analysis_id_field,
    analysis_name_field,
    aggregation_id_field,
    aggregation_name_field,
    displaced_field,
    fatalities_field,
    population_count_field,
    count_fields,
)
from safe.definitions.processing_steps import (
    summary_3_analysis_steps)
from safe.definitions.layer_purposes import layer_purpose_analysis_impacted
from safe.gis.vector.summary_tools import check_inputs
from safe.gis.vector.tools import create_field_from_definition
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

    summaries = {}
    # Summary is a dictionary with a tuple a key and the value to write in
    # the output layer as a value.
    # tuple (index in the aggregation layer, index in the analysis layer) : val
    analysis.startEditing()
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

    for row in analysis.getFeatures():
        # We should have only one row in the analysis layer.
        for field in summaries.keys():
            analysis.changeAttributeValue(
                row.id(),
                field[1],
                summaries[field])

    analysis.commitChanges()

    analysis.keywords['title'] = output_layer_name
    analysis.keywords['layer_purpose'] = layer_purpose_analysis_impacted['key']

    return analysis
