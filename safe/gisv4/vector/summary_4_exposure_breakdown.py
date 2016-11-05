# coding=utf-8

"""
Aggregate the aggregate hazard to the analysis layer.
"""

from qgis.core import QGis, QgsFeatureRequest, QgsFeature

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    exposure_type_field,
    total_field,
    total_affected_field,
    affected_field,
    hazard_count_field,
    exposure_count_field,
)
from safe.definitionsv4.processing_steps import (
    summary_4_exposure_breakdown_steps)
from safe.definitionsv4.post_processors import post_processor_affected_function
from safe.gisv4.vector.tools import (
    create_field_from_definition,
    read_dynamic_inasafe_field,
    create_memory_layer)
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def exposure_type_breakdown(aggregate_hazard, callback=None):
    """Compute the summary from the aggregate hazard to analysis.

    Source layer :
    | haz_id | haz_class | aggr_id | aggr_name | exposure_count |

    Output layer :
    | exp_type | count_hazard_class | total |

    :param aggregate_hazard: The layer to aggregate vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new tabular table, without geometry.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_4_exposure_breakdown_steps['output_layer_name']
    processing_step = summary_4_exposure_breakdown_steps['step_name']

    source_fields = aggregate_hazard.keywords['inasafe_fields']

    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field,
        affected_field,
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

            flat_table.add_value(
                exposure_count,
                hazard_class=hazard_value,
                exposure_class=exposure
            )

    tabular = create_memory_layer(output_layer_name, QGis.NoGeometry)
    tabular.startEditing()

    field = create_field_from_definition(exposure_type_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][exposure_type_field['key']] = (
        exposure_type_field['field_name'])

    classification = aggregate_hazard.keywords['hazard_keywords']['classification']

    hazard_affected = {}
    for hazard_class in unique_hazard:
        field = create_field_from_definition(hazard_count_field, hazard_class)
        tabular.addAttribute(field)
        key = hazard_count_field['key'] % hazard_class
        value = hazard_count_field['field_name'] % hazard_class
        tabular.keywords['inasafe_fields'][key] = value

        hazard_affected[hazard_class] = post_processor_affected_function(
            classification=classification, hazard_class=hazard_class)

    field = create_field_from_definition(total_affected_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_affected_field['key']] = (
        total_affected_field['field_name'])

    field = create_field_from_definition(total_field)
    tabular.addAttribute(field)
    tabular.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    for exposure_type in unique_exposure:
        feature = QgsFeature()
        attributes = [exposure_type]
        total_affected = 0
        total = 0
        for hazard_class in unique_hazard:
            value = flat_table.get_value(
                hazard_class=hazard_class,
                exposure_class=exposure_type
            )
            attributes.append(value)

            if hazard_affected[hazard_class]:
                total_affected += value

            total += value

        attributes.append(total_affected)
        attributes.append(total)

        feature.setAttributes(attributes)
        tabular.addFeature(feature)

    tabular.commitChanges()

    tabular.keywords['title'] = output_layer_name
    tabular.keywords['layer_purpose'] = 'exposure_breakdown'

    return tabular
