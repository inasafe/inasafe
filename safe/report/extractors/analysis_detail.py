# coding=utf-8
from safe.definitions.exposure import exposure_all, exposure_population
from safe.definitions.fields import (
    exposure_type_field,
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_not_affected_field,
    total_field, total_not_exposed_field)
from safe.definitions.hazard_classifications import hazard_classes_all
from safe.report.extractors.util import (
    layer_definition_type,
    resolve_from_dictionary,
    value_from_field_name)
from safe.utilities.i18n import tr
from safe.utilities.rounding import format_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


def analysis_detail_extractor(impact_report, component_metadata):
    """Extracting analysis result from the impact layer.

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
    extra_args = component_metadata.extra_args

    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    analysis_feature = analysis_layer.getFeatures().next()
    exposure_summary_table = impact_report.exposure_summary_table
    if exposure_summary_table:
        exposure_summary_table_fields = exposure_summary_table.keywords[
            'inasafe_fields']
    provenance = impact_report.impact_function.provenance
    debug_mode = impact_report.impact_function.debug_mode

    """Initializations"""

    # Get hazard classification
    hazard_classification = None
    # retrieve hazard classification from hazard layer
    for classification in hazard_classes_all:
        classification_name = hazard_layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break

    # Get exposure type definition
    exposure_type = layer_definition_type(exposure_layer)
    # Only round the number when it is population exposure and it is not
    # in debug mode
    is_rounding = not debug_mode
    use_population_rounding = exposure_type == exposure_population

    # Analysis detail only applicable for breakable exposure types:
    itemizable_exposures_all = [
        exposure for exposure in exposure_all
        if exposure.get('classifications')]
    if exposure_type not in itemizable_exposures_all:
        return context

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

    """Create detail header"""
    headers = []

    # breakdown header
    breakdown_header_template = ''
    if breakdown_field == exposure_type_field:
        breakdown_header_template = resolve_from_dictionary(
            extra_args, 'breakdown_header_type_format')
    elif breakdown_field == exposure_class_field:
        breakdown_header_template = resolve_from_dictionary(
            extra_args, 'breakdown_header_class_format')

    # check if there is header type associations
    type_header_mapping = resolve_from_dictionary(
        extra_args, 'exposure_type_header_mapping')

    if exposure_type['key'] in type_header_mapping:
        exposure_header = type_header_mapping[exposure_type['key']]
    else:
        exposure_header = exposure_type['name']

    headers.append(
        breakdown_header_template.format(exposure=exposure_header))

    # this is mapping for customizing double header for
    # affected/not affected hazard classes
    hazard_class_header_mapping = resolve_from_dictionary(
        extra_args,
        'hazard_class_header_mapping')
    # hazard header
    # TODO: we need to get affected and not_affected key from
    # definitions concept
    header_hazard_group = {
        'affected': {
            'hazards': []
        },
        'not_affected': {
            'hazards': []
        }
    }
    for key, group in header_hazard_group.iteritems():
        if key in hazard_class_header_mapping:
            header_hazard_group[key].update(hazard_class_header_mapping[key])

    for hazard_class in hazard_classification['classes']:
        # the tuple format would be:
        # (class name, is it affected, header background color
        hazard_class_name = hazard_class['name']
        if hazard_class.get('affected'):
            affected_status = 'affected'
        else:
            affected_status = 'not_affected'

        header_hazard_group[affected_status]['hazards'].append(
            hazard_class_name)
        headers.append(hazard_class_name)

    # affected, not affected, not exposed, total header
    report_fields = [
        total_affected_field,
        total_not_affected_field,
        total_not_exposed_field,
        total_field
    ]
    for report_field in report_fields:
        headers.append(report_field['name'])

    """Create detail rows"""
    details = []
    for feat in exposure_summary_table.getFeatures():
        row = []

        # Get breakdown name
        exposure_summary_table_field_name = breakdown_field['field_name']
        field_index = exposure_summary_table.fieldNameIndex(
            exposure_summary_table_field_name)
        class_key = feat[field_index]

        row.append(class_key)

        # Get hazard count
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )

            group_key = None
            for key, group in header_hazard_group.iteritems():
                if hazard_class['name'] in group['hazards']:
                    group_key = key
                    break

            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = exposure_summary_table_fields[field_key_name]
                field_index = exposure_summary_table.fieldNameIndex(field_name)
                # exposure summary table is in csv format, so the field
                # returned is always in text format
                count_value = int(float(feat[field_index]))
                count_value = format_number(
                    count_value,
                    enable_rounding=is_rounding)
                row.append({
                    'value': count_value,
                    'header_group': group_key
                })
            except KeyError:
                # in case the field was not found
                # assume value 0
                row.append({
                    'value': 0,
                    'header_group': group_key
                })

        skip_row = False

        for field in report_fields:
            field_index = exposure_summary_table.fieldNameIndex(
                field['field_name'])
            total_count = int(float(feat[field_index]))
            total_count = format_number(
                total_count,
                enable_rounding=is_rounding)
            if total_count == '0' and field == total_affected_field:
                skip_row = True
                break

            row.append(total_count)

        if skip_row:
            continue

        details.append(row)

    # retrieve classes definitions
    exposure_classifications = exposure_type['classifications']
    exposure_class_lists = []
    for classes_definition in exposure_classifications:
        classes = classes_definition.get('classes')
        if classes:
            exposure_class_lists += classes

    # sort detail rows based on class order
    # create lambda function to sort
    def sort_classes(row):
        """Sort method to retrieve exposure class key index"""
        # class key is first column
        class_key = row[0]
        # find index in class list
        for i, exposure_class in enumerate(exposure_class_lists):
            if class_key == exposure_class['key']:
                return i
        else:
            return -1

    # sort
    details = sorted(details, key=sort_classes)

    # retrieve breakdown name from classes list
    for row in details:
        class_key = row[0]
        for exposure_class in exposure_class_lists:
            if class_key == exposure_class['key']:
                breakdown_name = exposure_class['name']
                break
        else:
            # attempt for dynamic translations
            breakdown_name = tr(class_key.capitalize())

        # replace class_key with the class name
        row[0] = breakdown_name

    """create total footers"""
    # create total header
    footers = [total_field['name']]
    # total for hazard
    for hazard_class in hazard_classification['classes']:
        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'],)

        group_key = None
        for key, group in header_hazard_group.iteritems():
            if hazard_class['name'] in group['hazards']:
                group_key = key
                break

        try:
            # retrieve dynamic field name from analysis_fields keywords
            # will cause key error if no hazard count for that particular
            # class
            field_name = analysis_layer_fields[field_key_name]
            field_index = analysis_layer.fieldNameIndex(field_name)
            count_value = format_number(
                analysis_feature[field_index],
                enable_rounding=is_rounding)
        except KeyError:
            # in case the field was not found
            # assume value 0
            count_value = '0'

        if count_value == '0':
            # if total affected for hazard class is zero, delete entire
            # column
            column_index = len(footers)
            # delete header column
            headers = headers[:column_index] + headers[column_index + 1:]
            for row_idx in range(0, len(details)):
                row = details[row_idx]
                row = row[:column_index] + row[column_index + 1:]
                details[row_idx] = row
            continue
        footers.append({
            'value': count_value,
            'header_group': group_key
        })

    # for footers
    for field in report_fields:
        total_count = value_from_field_name(
            field['field_name'], analysis_layer)
        total_count = format_number(
            total_count,
            enable_rounding=is_rounding)
        footers.append(total_count)

    header = resolve_from_dictionary(
        extra_args, 'header')
    notes = resolve_from_dictionary(
        extra_args, 'notes')

    context['header'] = header
    context['group_border_color'] = resolve_from_dictionary(
        extra_args, 'group_border_color')
    context['notes'] = notes

    breakdown_header_index = 0
    total_header_index = len(headers) - len(report_fields)
    context['detail_header'] = {
        'header_hazard_group': header_hazard_group,
        'breakdown_header_index': breakdown_header_index,
        'total_header_index': total_header_index
    }

    # modify headers to include double header
    affected_headers = []
    last_group = 0
    for i in range(breakdown_header_index, total_header_index):
        hazard_class_name = headers[i]
        group_key = None
        for key, group in header_hazard_group.iteritems():
            if hazard_class_name in group['hazards']:
                group_key = key
                break

        if group_key and group_key not in affected_headers:
            affected_headers.append(group_key)
            headers[i] = {
                'name': hazard_class_name,
                'start': True,
                'header_group': group_key,
                'colspan': 1
            }
            last_group = i
            header_hazard_group[group_key]['start_index'] = i
        elif group_key:
            colspan = headers[last_group]['colspan']
            headers[last_group]['colspan'] = colspan + 1
            headers[i] = {
                'name': hazard_class_name,
                'start': False,
                'header_group': group_key
            }

    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')
    table_header = table_header_format.format(
        title=provenance['map_legend_title'],
        exposure=exposure_header)

    context['detail_table'] = {
        'table_header': table_header,
        'headers': headers,
        'details': details,
        'footers': footers,
    }

    return context
