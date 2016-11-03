# coding=utf-8

"""
Aggregate the impact table to the aggregate hazard.
"""

from qgis.core import QGis, QgsField, QgsFeatureRequest

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import (
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    exposure_id_field,
    exposure_class_field,
    total_field,
    exposure_count_field,
    size_field
)
from safe.definitionsv4.processing_steps import summary_1_impact_steps
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def impact_summary(source, target, callback=None):
    """Compute the summary from the layer_to_aggregate into the aggregate hazard.

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
    output_layer_name = summary_1_impact_steps['output_layer_name']
    processing_step = summary_1_impact_steps['step_name']

    source_fields = source.keywords['inasafe_fields']
    target_fields = target.keywords['inasafe_fields']

    target_compulsory_fields = [
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field
    ]
    for field in target_compulsory_fields:
        # noinspection PyTypeChecker
        if not target_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], target_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    source_compulsory_fields = [
        exposure_id_field,
        exposure_class_field,
        aggregation_id_field,
        aggregation_name_field,
        hazard_id_field,
        hazard_class_field
    ]
    for field in source_compulsory_fields:
        # noinspection PyTypeChecker
        if not source_fields.get(field['key']):
            # noinspection PyTypeChecker
            msg = '%s not found in %s' % (field['key'], source_fields)
            raise InvalidKeywordsForProcessingAlgorithm(msg)

    aggregation_id = target_fields[aggregation_id_field['key']]

    hazard_id = target_fields[hazard_id_field['key']]

    exposure_class = source_fields[exposure_class_field['key']]
    exposure_class_index = source.fieldNameIndex(exposure_class)
    unique_exposure = source.uniqueValues(exposure_class_index)

    if source_fields.get(size_field['key']):
        field_size = source_fields[size_field['key']]
        field_index = source.fieldNameIndex(field_size)
    else:
        field_index = None

    # Special case for a point layer and indivisible polygon,
    # we do not want to report on the size.
    geometry = source.geometryType()
    exposure = source.keywords.get('exposure')
    if geometry == QGis.Point:
        field_index = None
    if geometry == QGis.Polygon and exposure == 'structure':
        field_index = None

    target.startEditing()

    shift = target.fields().count()

    for column in unique_exposure:
        field = QgsField(exposure_count_field['field_name'] % column)
        field.setType(exposure_count_field['type'])
        field.setLength(exposure_count_field['length'])
        field.setPrecision(exposure_count_field['precision'])
        target.addAttribute(field)

    field = QgsField(total_field['field_name'])
    field.setType(total_field['type'])
    field.setLength(total_field['length'])
    field.setPrecision(total_field['precision'])
    target.addAttribute(field)

    flat_table = FlatTable('aggregation_id', 'hazard_id', 'exposure_class')

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for f in source.getFeatures(request):

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

    for area in target.getFeatures(request):
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
            target.changeAttributeValue(area.id(), shift + i, sum)

        target.changeAttributeValue(
            area.id(), shift + len(unique_exposure), total)

    target.commitChanges()

    # Todo add keywords for these new fields
    target.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    for column in unique_exposure:
        key = exposure_count_field['key'] % column
        value = exposure_count_field['field_name'] % column
        target.keywords['inasafe_fields'][key] = value

    target.keywords['title'] = output_layer_name

    return target
