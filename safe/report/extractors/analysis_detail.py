# coding=utf-8
from safe.definitions.exposure import exposure_all, exposure_population
from safe.definitions.fields import (
    exposure_type_field,
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_unaffected_field,
    total_field, total_not_exposed_field)
from safe.definitions.hazard_classifications import hazard_classes_all
from safe.report.extractors.util import (
    layer_definition_type,
    resolve_from_dictionary,
    value_from_field_name)
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
    exposure_breakdown = impact_report.exposure_breakdown
    if exposure_breakdown:
        exposure_breakdown_fields = exposure_breakdown.keywords[
            'inasafe_fields']
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
        if field['key'] in exposure_breakdown_fields:
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

    headers.append(
        breakdown_header_template.format(exposure=exposure_type['name']))

    # hazard header
    for hazard_class in hazard_classification['classes']:
        headers.append(hazard_class['name'])

    # affected, not exposed, unaffected, total header
    report_fields = [
        total_affected_field,
        total_unaffected_field,
        total_not_exposed_field,
        total_field
    ]
    for report_field in report_fields:
        headers.append(report_field['name'])

    """Create detail rows"""
    details = []
    for feat in exposure_breakdown.getFeatures():
        row = []

        # Get breakdown name
        breakdown_field_name = breakdown_field['field_name']
        field_index = exposure_breakdown.fieldNameIndex(breakdown_field_name)
        breakdown_name = feat[field_index]
        row.append(breakdown_name)

        # Get hazard count
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )

            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = exposure_breakdown_fields[field_key_name]
                field_index = exposure_breakdown.fieldNameIndex(field_name)
                # exposure breakdown is in csv format, so the field
                # returned is always in text format
                count_value = int(float(feat[field_index]))
                count_value = format_number(
                    count_value,
                    enable_rounding=is_rounding)
                row.append(count_value)
            except KeyError:
                # in case the field was not found
                # assume value 0
                row.append(0)

        skip_row = False

        for field in report_fields:
            field_index = exposure_breakdown.fieldNameIndex(
                field['field_name'])
            total_count = int(float(feat[field_index]))
            total_count = format_number(
                total_count,
                enable_rounding=is_rounding)
            if total_count == 0 and field == total_affected_field:
                skip_row = True
                break

            row.append(total_count)

        if skip_row:
            continue

        details.append(row)

    """create total footers"""
    # create total header
    footers = [total_field['name']]
    # total for hazard
    for hazard_class in hazard_classification['classes']:
        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'],)

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
            count_value = 0

        if count_value == 0:
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
        footers.append(count_value)

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

    context['header'] = header.format(exposure=exposure_type['name'])
    context['notes'] = notes
    context['detail_table'] = {
        'headers': headers,
        'details': details,
        'footers': footers,
    }

    return context
