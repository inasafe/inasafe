# coding=utf-8

"""Module used to generate context for aggregation result section."""

from safe.definitions.exposure import exposure_all, exposure_population
from safe.definitions.fields import (
    affected_exposure_count_field,
    aggregation_name_field,
    total_affected_field,
    exposure_type_field,
    exposure_class_field)
from safe.definitions.utilities import definition
from safe.gis.vector.tools import read_dynamic_inasafe_field
from safe.report.extractors.util import (
    resolve_from_dictionary,
    retrieve_exposure_classes_lists)
from safe.utilities.i18n import tr
from safe.utilities.rounding import format_number

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

    .. versionadded:: 4.0
    """
    context = {}

    """Initializations."""

    extra_args = component_metadata.extra_args
    # Find out aggregation report type
    analysis_layer = impact_report.analysis
    provenance = impact_report.impact_function.provenance
    exposure_keywords = provenance['exposure_keywords']
    exposure_summary_table = impact_report.exposure_summary_table
    if exposure_summary_table:
        exposure_summary_table_fields = exposure_summary_table.keywords[
            'inasafe_fields']
    aggregation_summary = impact_report.aggregation_summary
    aggregation_summary_fields = aggregation_summary.keywords[
        'inasafe_fields']
    use_rounding = impact_report.impact_function.use_rounding
    use_aggregation = bool(
        impact_report.impact_function.provenance['aggregation_layer'])
    if not use_aggregation:
        return context

    """Filtering report sections."""

    # Only process for applicable exposure types
    # Get exposure type definition
    exposure_type = definition(exposure_keywords['exposure'])
    # Only round the number when it is population exposure and we use rounding
    is_population = exposure_type is exposure_population

    # For now aggregation report only applicable for breakable exposure types:
    itemizable_exposures_all = [
        exposure for exposure in exposure_all
        if exposure.get('classifications')]
    if exposure_type not in itemizable_exposures_all:
        return context

    """Generating type name for columns."""

    type_fields = read_dynamic_inasafe_field(
        aggregation_summary_fields, affected_exposure_count_field)
    # do not include total, to preserve ordering and proper reference
    type_fields.remove('total')

    # we need to sort the column
    # get the classes lists
    # retrieve classes definitions
    exposure_classes_lists = retrieve_exposure_classes_lists(exposure_keywords)

    # sort columns based on class order
    # create function to sort
    def sort_classes(_type_field):
        """Sort method to retrieve exposure class key index."""
        # class key is the type field name
        # find index in class list
        for i, _exposure_class in enumerate(exposure_classes_lists):
            if _type_field == _exposure_class['key']:
                index = i
                break
        else:
            index = -1

        return index

    # sort
    type_fields = sorted(type_fields, key=sort_classes)

    # generate type_header_labels for column header
    type_header_labels = []
    for type_name in type_fields:
        type_label = tr(type_name.capitalize())
        type_header_labels.append(type_label)

    """Generating values for rows."""

    # generate rows of values for values of each column
    rows = []
    aggregation_name_index = aggregation_summary.fields().lookupField(
        aggregation_name_field['field_name'])
    total_field_index = aggregation_summary.fields().lookupField(
        total_affected_field['field_name'])

    type_field_index = []
    for type_name in type_fields:
        field_name = affected_exposure_count_field['field_name'] % type_name
        type_index = aggregation_summary.fields().lookupField(field_name)
        type_field_index.append(type_index)

    for feat in aggregation_summary.getFeatures():
        total_affected_value = format_number(
            feat[total_field_index],
            use_rounding=use_rounding,
            is_population=is_population)
        if total_affected_value == '0':
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
            affected_value = format_number(
                feat[idx],
                use_rounding=use_rounding)
            type_values.append(affected_value)
        item['type_values'] = type_values
        rows.append(item)

    """Generate total for footers."""

    # calculate total values for each type. Taken from exposure summary table
    type_total_values = []
    # Get affected field index
    affected_field_index = exposure_summary_table.fields().lookupField(
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
        if field['key'] in exposure_summary_table_fields:
            breakdown_field = field
            break
    breakdown_field_name = breakdown_field['field_name']
    breakdown_field_index = exposure_summary_table.fields().lookupField(
        breakdown_field_name)

    # Fetch total affected for each breakdown name
    value_dict = {}
    for feat in exposure_summary_table.getFeatures():
        # exposure summary table is in csv format, so the field returned is
        # always in text format
        affected_value = int(float(feat[affected_field_index]))
        affected_value = format_number(
            affected_value,
            use_rounding=use_rounding,
            is_population=is_population)
        value_dict[feat[breakdown_field_index]] = affected_value

    if value_dict:
        for type_name in type_fields:
            affected_value_string_formatted = value_dict[type_name]
            if affected_value_string_formatted == '0':
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
            type_total_values.append(affected_value_string_formatted)

    """Get the super total affected."""

    # total for affected (super total)
    analysis_feature = next(analysis_layer.getFeatures())
    field_index = analysis_layer.fields().lookupField(
        total_affected_field['field_name'])
    total_all = format_number(
        analysis_feature[field_index],
        use_rounding=use_rounding)

    """Generate and format the context."""
    aggregation_area_default_header = resolve_from_dictionary(
        extra_args, 'aggregation_area_default_header')
    header_label = (
        aggregation_summary.title() or aggregation_area_default_header)

    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')

    # check unit
    units = exposure_type['units']
    if units:
        unit = units[0]
        abbreviation = unit['abbreviation']
        if abbreviation:
            unit_string = '({abbreviation})'.format(abbreviation=abbreviation)
        else:
            unit_string = ''
    else:
        unit_string = ''

    table_header = table_header_format.format(
        title=provenance['map_legend_title'],
        unit=unit_string)
    table_header = ' '.join(table_header.split())

    section_header = resolve_from_dictionary(extra_args, 'header')
    notes = resolve_from_dictionary(extra_args, 'notes')
    total_header = resolve_from_dictionary(extra_args, 'total_header')
    total_in_aggregation_header = resolve_from_dictionary(
        extra_args, 'total_in_aggregation_header')
    context['header'] = section_header
    context['notes'] = notes
    context['aggregation_result'] = {
        'table_header': table_header,
        'header_label': header_label,
        'type_header_labels': type_header_labels,
        'total_label': total_header,
        'total_in_aggregation_area_label': total_in_aggregation_header,
        'rows': rows,
        'type_total_values': type_total_values,
        'total_all': total_all,
    }
    return context
