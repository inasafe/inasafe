# coding=utf-8

"""
Aggregate the impact table to the aggregate hazard.
"""

from qgis.core import QGis, QgsField, QgsFeatureRequest

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    aggregation_id_field,
    hazard_id_field,
    exposure_class_field,
    total_field,
    exposure_count_field,
    size_field
)
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def aggregate_summary(aggregate_hazard, impact, callback=None):
    """Compute the summary from the impact into the aggregate hazard.

    :param aggregate_hazard: The aggregate hazard vector layer.
    :type aggregate_hazard: QgsVectorLayer

    :param impact: The impact vector layer.
    :type impact: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new aggregate hazard with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    impact_fields = impact.keywords['inasafe_fields']
    aggregate_fields = aggregate_hazard.keywords['inasafe_fields']

    if not aggregate_fields.get(aggregation_id_field['key']):
        msg = '%s not found in %s' % (
            aggregation_id_field['key'], aggregate_fields)
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    if not impact_fields.get(exposure_class_field['key']):
        msg = '%s not found in %s' % (
            exposure_class_field['key'], impact_fields)
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    aggregation_id = aggregate_fields[aggregation_id_field['key']]

    hazard_id = aggregate_fields[hazard_id_field['key']]

    exposure_class = impact_fields[exposure_class_field['key']]
    exposure_class_index = impact.fieldNameIndex(exposure_class)
    unique_exposure = impact.uniqueValues(exposure_class_index)

    if impact_fields.get(size_field['key']):
        field_size = impact_fields[size_field['key']]
        field_index = impact.fieldNameIndex(field_size)
    else:
        field_index = None

    aggregate_hazard.startEditing()

    shift = aggregate_hazard.fields().count()

    for column in unique_exposure:
        field = QgsField(exposure_count_field['field_name'] % column)
        field.setType(exposure_count_field['type'])
        field.setLength(exposure_count_field['length'])
        field.setPrecision(exposure_count_field['precision'])
        aggregate_hazard.addAttribute(field)

    field = QgsField(total_field['field_name'])
    field.setType(total_field['type'])
    field.setLength(total_field['length'])
    field.setPrecision(total_field['precision'])
    aggregate_hazard.addAttribute(field)

    flat_table = FlatTable('aggregation_id', 'hazard_id', 'exposure_class')

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for f in impact.getFeatures(request):

        if field_index:
            value = f[field_index]
        else:
            value = 1

        flat_table.add_value(
            value,
            aggregation_id=f[aggregation_id],
            hazard_id=f[hazard_id],
            exposure_class=f[exposure_class]
        )

    for area in aggregate_hazard.getFeatures(request):
        aggregation_value = area[aggregation_id]
        hazard_value = area[hazard_id]
        total = 0
        for i, val in enumerate(unique_exposure):
            sum = flat_table.get_value(
                aggregation_id=aggregation_value,
                hazard_id=hazard_value,
                exposure_class=val
            )
            total += sum
            aggregate_hazard.changeAttributeValue(area.id(), shift + i, sum)

        aggregate_hazard.changeAttributeValue(
            area.id(), shift + len(unique_exposure), total)

    aggregate_hazard.commitChanges()

    # Todo add keywords for these new fields
    aggregate_hazard.keywords['inasafe_fields'][total_field['key']] = total_field['field_name']
    return aggregate_hazard

