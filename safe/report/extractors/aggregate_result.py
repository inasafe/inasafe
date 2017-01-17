# coding=utf-8
from safe.definitions.exposure import exposure_all, exposure_population
from safe.definitions.fields import (
    affected_exposure_count_field,
    aggregation_name_field,
    total_affected_field,
    exposure_type_field,
    exposure_class_field)
from safe.gis.vector.tools import read_dynamic_inasafe_field
from safe.report.extractors.util import (
    round_affected_number,
    layer_definition_type)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def aggregation_result_extractor(impact_report, component_metadata):
    """Extracting aggregation result of breakdown from the impact layer.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    """Initializations"""

    # Find out aggregation report type
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    exposure_breakdown = impact_report.exposure_breakdown
    if exposure_breakdown:
        exposure_breakdown_fields = exposure_breakdown.keywords[
            'inasafe_fields']
    aggregation_impacted = impact_report.aggregation_impacted
    aggregation_impacted_fields = aggregation_impacted.keywords[
        'inasafe_fields']
    debug_mode = impact_report.impact_function.debug_mode

    """Filtering report sections"""

    # Only process for applicable exposure types
    # Get exposure type definition
    exposure_type = layer_definition_type(exposure_layer)
    # Only round the number when it is population exposure and it is not
    # in debug mode
    is_rounded = not debug_mode
    use_population_rounding = exposure_type == exposure_population

    # For now aggregation report only applicable for breakable exposure types:
    itemizable_exposures_all = [
        exposure for exposure in exposure_all
        if exposure.get('classifications')]
    if exposure_type not in itemizable_exposures_all:
        return context

    """Generating type name for columns"""

    type_fields = read_dynamic_inasafe_field(
        aggregation_impacted_fields, affected_exposure_count_field)
    # do not include total, to preserve ordering and proper reference
    type_fields.remove('total')

    # generate type_header_labels for column header
    type_header_labels = []
    for type_name in type_fields:
        type_label = type_name.capitalize()
        type_header_labels.append(type_label)

    """Generating values for rows"""

    # generate rows of values for values of each column
    rows = []
    aggregation_name_index = aggregation_impacted.fieldNameIndex(
        aggregation_name_field['field_name'])
    total_field_index = aggregation_impacted.fieldNameIndex(
        total_affected_field['field_name'])

    type_field_index = []
    for type_name in type_fields:
        field_name = affected_exposure_count_field['field_name'] % type_name
        type_index = aggregation_impacted.fieldNameIndex(field_name)
        type_field_index.append(type_index)

    for feat in aggregation_impacted.getFeatures():
        total_affected_value = round_affected_number(
            feat[total_field_index],
            enable_rounding=is_rounded,
            use_population_rounding=use_population_rounding)
        if total_affected_value == 0:
            # skip aggregation type if the total affected is zero
            continue
        item = {
            # Name is the header for each row
            'name': feat[aggregation_name_index],
            # Total is the total for each row
            'total': total_affected_value
        }
        # Type values is the values for each column in each row
        type_values = []
        for idx in type_field_index:
            affected_value = round_affected_number(
                feat[idx],
                enable_rounding=is_rounded,
                use_population_rounding=use_population_rounding)
            type_values.append(affected_value)
        item['type_values'] = type_values
        rows.append(item)

    """Generate total for footers"""

    # calculate total values for each type. Taken from exposure breakdown
    type_total_values = []
    # Get affected field index
    affected_field_index = exposure_breakdown.fieldNameIndex(
        total_affected_field['field_name'])

    # Get breakdown field
    breakdown_field = None
    # I'm not sure what's the difference
    # It is possible to have exposure_type_field or exposure_class_field
    # at the moment
    breakdown_fields = [
        exposure_type_field,
        exposure_class_field
    ]
    for field in breakdown_fields:
        if field['key'] in exposure_breakdown_fields:
            breakdown_field = field
            break
    breakdown_field_name = breakdown_field['field_name']
    breakdown_field_index = exposure_breakdown.fieldNameIndex(
        breakdown_field_name)

    # Fetch total affected for each breakdown name
    value_dict = {}
    for feat in exposure_breakdown.getFeatures():
        affected_value = round_affected_number(
            feat[affected_field_index],
            enable_rounding=is_rounded,
            use_population_rounding=use_population_rounding)
        value_dict[feat[breakdown_field_index]] = affected_value

    if value_dict:
        for type_name in type_fields:
            if int(value_dict[type_name]) == 0:
                # if total affected for breakdown type is zero
                # current column index
                column_index = len(type_total_values)
                # cut column header
                type_header_labels = (
                    type_header_labels[:column_index] +
                    type_header_labels[column_index + 1:])
                # cut all row values for the column
                for item in rows:
                    type_values = item['type_values']
                    item['type_values'] = (
                        type_values[:column_index] +
                        type_values[column_index + 1:])
                continue
            type_total_values.append(value_dict[type_name])

    """Get the super total affected"""

    # total for affected (super total)
    analysis_feature = analysis_layer.getFeatures().next()
    field_index = analysis_layer.fieldNameIndex(
        total_affected_field['field_name'])
    total_all = round_affected_number(
        analysis_feature[field_index],
        enable_rounding=is_rounded,
        use_population_rounding=use_population_rounding)

    """Generate and format the context"""

    header_label = aggregation_impacted.title() or tr('Aggregation area')

    context['header'] = tr('Aggregation Result')
    context['notes'] = tr(
        'Columns and rows containing only 0 or "No data" values are '
        'excluded from the tables.')
    context['aggregation_result'] = {
        'header_label': header_label,
        'type_header_labels': type_header_labels,
        'total_label': tr('Total'),
        'total_in_aggregation': tr('Total in aggregation areas'),
        'rows': rows,
        'type_total_values': type_total_values,
        'total_all': total_all,
    }
    return context
