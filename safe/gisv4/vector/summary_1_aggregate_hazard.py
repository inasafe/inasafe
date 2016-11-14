# coding=utf-8

"""
Aggregate the impact table to the aggregate hazard.
"""
from PyQt4.QtCore import QPyNullVariant
from qgis.core import QGis, QgsFeatureRequest

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
    affected_field,
    size_field
)
from safe.definitionsv4.post_processors import post_processor_affected_function
from safe.definitionsv4.processing_steps import (
    summary_1_aggregate_hazard_steps)
from safe.definitionsv4.utilities import definition
from safe.gisv4.vector.tools import create_field_from_definition
from safe.utilities.profiling import profile
from safe.utilities.pivot_table import FlatTable
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def aggregate_hazard_summary(impact, aggregate_hazard, callback=None):
    """Compute the summary from the source layer to the aggregate_hazard layer.

    Source layer :
    |exp_id|exp_class|haz_id|haz_class|aggr_id|aggr_name|affected|extra*|

    Target layer :
    | aggr_id | aggr_name | haz_id | haz_class | extra* |

    Output layer :
    |aggr_id| aggr_name|haz_id|haz_class|affected|extra*|count ber exposure*|


    :param impact: The layer to aggregate vector layer.
    :type impact: QgsVectorLayer

    :param aggregate_hazard: The aggregate_hazard vector layer where to write
        statistics.
    :type aggregate_hazard: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new aggregate_hazard layer with summary.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = summary_1_aggregate_hazard_steps['output_layer_name']
    processing_step = summary_1_aggregate_hazard_steps['step_name']

    source_fields = impact.keywords['inasafe_fields']
    target_fields = aggregate_hazard.keywords['inasafe_fields']

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
    hazard_class = target_fields[hazard_class_field['key']]

    exposure_class = source_fields[exposure_class_field['key']]
    exposure_class_index = impact.fieldNameIndex(exposure_class)
    unique_exposure = impact.uniqueValues(exposure_class_index)

    if source_fields.get(size_field['key']):
        field_size = source_fields[size_field['key']]
        field_index = impact.fieldNameIndex(field_size)
    else:
        field_index = None

    # Special case for a point layer and indivisible polygon,
    # we do not want to report on the size.
    geometry = impact.geometryType()
    exposure = impact.keywords.get('exposure')
    if geometry == QGis.Point:
        field_index = None
    if geometry == QGis.Polygon and exposure == 'structure':
        field_index = None

    # Special case if it's an exposure without classification. It means it's
    # a continuous exposure. We count the compulsory field.
    classification = impact.keywords.get('classification')
    if not classification:
        exposure_definitions = definition(exposure)
        # I take the only first field for reporting, I don't know how to manage
        # with many fields. AFAIK we don't have this case yet.
        field = exposure_definitions['compulsory_fields'][0]
        field_name = source_fields[field['key']]
        field_index = impact.fieldNameIndex(field_name)

    aggregate_hazard.startEditing()

    shift = aggregate_hazard.fields().count()

    for column in unique_exposure:
        if not column or isinstance(column, QPyNullVariant):
            column = 'NULL'
        field = create_field_from_definition(exposure_count_field, column)
        aggregate_hazard.addAttribute(field)
        key = exposure_count_field['key'] % column
        value = exposure_count_field['field_name'] % column
        aggregate_hazard.keywords['inasafe_fields'][key] = value

    # Affected field
    field = create_field_from_definition(affected_field)
    aggregate_hazard.addAttribute(field)
    aggregate_hazard.keywords['inasafe_fields'][affected_field['key']] = (
        affected_field['field_name'])

    # Total field
    field = create_field_from_definition(total_field)
    aggregate_hazard.addAttribute(field)
    aggregate_hazard.keywords['inasafe_fields'][total_field['key']] = (
        total_field['field_name'])

    flat_table = FlatTable('aggregation_id', 'hazard_id', 'exposure_class')

    request = QgsFeatureRequest()
    request.setFlags(QgsFeatureRequest.NoGeometry)
    for f in impact.getFeatures(request):

        # Field_index can be equal to 0.
        if field_index is not None:
            value = f[field_index]
        else:
            value = 1

        aggregation_value = f[aggregation_id]
        hazard_value = f[hazard_id]
        exposure_value = f[exposure_class]
        if not exposure_value or isinstance(exposure_value, QPyNullVariant):
            exposure_value = 'NULL'

        flat_table.add_value(
            value,
            aggregation_id=aggregation_value,
            hazard_id=hazard_value,
            exposure_class=exposure_value
        )

    hazard_keywords = aggregate_hazard.keywords['hazard_keywords']
    classification = hazard_keywords['classification']

    for area in aggregate_hazard.getFeatures(request):
        aggregation_value = area[aggregation_id]
        feature_hazard_id = area[hazard_id]
        feature_hazard_value = area[hazard_class]
        total = 0
        for i, val in enumerate(unique_exposure):
            sum = flat_table.get_value(
                aggregation_id=aggregation_value,
                hazard_id=feature_hazard_id,
                exposure_class=val
            )
            total += sum
            aggregate_hazard.changeAttributeValue(area.id(), shift + i, sum)

        affected = post_processor_affected_function(
            classification=classification, hazard_class=feature_hazard_value)
        affected = tr(unicode(affected))
        aggregate_hazard.changeAttributeValue(
            area.id(), shift + len(unique_exposure), affected)

        aggregate_hazard.changeAttributeValue(
            area.id(), shift + len(unique_exposure) + 1, total)

    aggregate_hazard.commitChanges()

    aggregate_hazard.keywords['title'] = output_layer_name

    return aggregate_hazard
