# coding=utf-8

"""
Aggregate the aggregate hazard to the aggregation layer.
"""

from qgis.core import QGis, QgsFeatureRequest

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    total_affected_field,
    exposure_count_field,
    affected_exposure_count_field,
    affected_field,
)
from safe.definitionsv4.processing_steps import (
    summary_2_aggregation_steps)
from safe.gisv4.vector.tools import (
    create_field_from_definition, read_dynamic_inasafe_field)
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def aggregation_summary(aggregate_hazard, aggregation, callback=None):
    """Compute the summary from the aggregate hazard to the analysos layer.

    Source layer :
    | haz_id | haz_class | aggr_id | aggr_name | total_feature |

    Target layer :
    | aggr_id | aggr_name |

    Output layer :
    | aggr_id | aggr_name | count of affected features per exposure type

    :param aggregate_hazard: The layer to aggregate vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param aggregation: The aggregation vector layer where to write statistics.
    :type aggregation: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new aggregation layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_2_aggregation_steps['output_layer_name']
    processing_step = summary_2_aggregation_steps['step_name']

    source_fields = aggregate_hazard.keywords['inasafe_fields']
    target_fields = aggregation.keywords['inasafe_fields']

    target_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
    ]
    for field in target_compulsory_fields:
        # noinspection PyTypeChecker
        if not target_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], target_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    # Missing exposure_count_field
    source_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field,
        affected_field,
    ]
    for field in source_compulsory_fields:
        # noinspection PyTypeChecker
        if not source_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], source_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    pattern = exposure_count_field['key']
    pattern = pattern.replace('%s', '')
    unique_exposure = read_dynamic_inasafe_field(
        source_fields, exposure_count_field)

    flat_table = FlatTable('aggregation_id', 'exposure_class')

    aggregation_index = source_fields[aggregation_id_field['key']]

    # We want to loop over affected features only.
    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    expression = '\"%s\" = \'%s\'' % (
        affected_field['field_name'], tr('True'))
    request.setFilterExpression(expression)
    for area in aggregate_hazard.getFeatures(request):

        for key, name_field in source_fields.iteritems():
            if key.endswith(pattern):
                key.replace(pattern, '')
                flat_table.add_value(
                    area[name_field],
                    aggregation_id=area[aggregation_index],
                    exposure_class=key.replace(pattern, '')
                )

    shift = aggregation.fields().count()

    aggregation.startEditing()

    for column in unique_exposure:
        field = create_field_from_definition(
            affected_exposure_count_field, column)
        aggregation.addAttribute(field)
        key = affected_exposure_count_field['key'] % column
        value = affected_exposure_count_field['field_name'] % column
        aggregation.keywords['inasafe_fields'][key] = value

    # Total field
    field = create_field_from_definition(total_affected_field)
    aggregation.addAttribute(field)
    aggregation.keywords['inasafe_fields'][total_affected_field['key']] = (
        total_affected_field['field_name'])

    aggregation_index = target_fields[aggregation_id_field['key']]

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for area in aggregation.getFeatures(request):
        aggregation_value = area[aggregation_index]
        total = 0
        for i, val in enumerate(unique_exposure):
            sum = flat_table.get_value(
                aggregation_id=aggregation_value,
                exposure_class=val
            )
            total += sum
            aggregation.changeAttributeValue(area.id(), shift + i, sum)

        aggregation.changeAttributeValue(
            area.id(), shift + len(unique_exposure), total)

    aggregation.commitChanges()

    aggregation.keywords['title'] = output_layer_name

    return aggregation
