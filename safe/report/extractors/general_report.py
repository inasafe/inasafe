# coding=utf-8
"""Module used to extract context for general summary."""
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    hazard_count_field,
    total_field,
    fatalities_field)
from safe.report.extractors.util import (
    layer_definition_type,
    resolve_from_dictionary,
    value_from_field_name,
    layer_hazard_classification)
from safe.utilities.rounding import format_number, fatalities_range

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def general_report_extractor(impact_report, component_metadata):
    """Extracting general analysis result from the impact layer.

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
    extra_args = component_metadata.extra_args

    # figure out analysis report type
    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    provenance = impact_report.impact_function.provenance
    debug_mode = impact_report.impact_function.debug_mode

    exposure_type = layer_definition_type(exposure_layer)
    # Only round the number when it is population exposure and it is not
    # in debug mode
    is_rounded = not debug_mode
    is_population = exposure_type is exposure_population

    # find hazard class
    summary = []

    analysis_feature = analysis_layer.getFeatures().next()
    analysis_inasafe_fields = analysis_layer.keywords['inasafe_fields']

    exposure_unit = exposure_type['units'][0]
    hazard_header = resolve_from_dictionary(extra_args, 'hazard_header')
    if exposure_unit['abbreviation']:
        value_header = u'{measure} ({abbreviation})'.format(**exposure_unit)
    else:
        value_header = u'{name}'.format(**exposure_unit)

    # in case there is a classification
    if 'classification' in hazard_layer.keywords:

        # retrieve hazard classification from hazard layer
        hazard_classification = layer_hazard_classification(hazard_layer)

        # classified hazard must have hazard count in analysis layer
        hazard_stats = []
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )
            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = analysis_inasafe_fields[field_key_name]
                field_index = analysis_layer.fieldNameIndex(field_name)
                # Hazard label taken from translated hazard count field
                # label, string-formatted with translated hazard class label
                hazard_label = hazard_class['name']

                hazard_value = format_number(
                    analysis_feature[field_index],
                    enable_rounding=is_rounded,
                    is_population=is_population)
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'value': hazard_value
                }
            except KeyError:
                # in case the field was not found
                hazard_label = hazard_class['name']
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'value': 0,
                }

            hazard_stats.append(stats)

        # find total field
        try:
            field_name = analysis_inasafe_fields[total_field['key']]
            total = value_from_field_name(field_name, analysis_layer)
            total = format_number(
                total, enable_rounding=is_rounded, is_population=is_population)
            stats = {
                'key': total_field['key'],
                'name': total_field['name'],
                'as_header': True,
                'value': total
            }
            hazard_stats.append(stats)
        except KeyError:
            pass

        summary.append({
            'header_label': hazard_header,
            'value_label': value_header,
            'rows': hazard_stats
        })

    # retrieve affected column
    report_stats = []

    reported_fields = resolve_from_dictionary(
        extra_args, 'reported_fields')
    for item in reported_fields:
        header = item['header']
        field = item['field']
        if field['key'] in analysis_inasafe_fields:
            field_index = analysis_layer.fieldNameIndex(
                field['field_name'])
            if field == fatalities_field:
                # For fatalities field, we show a range of number
                # instead
                row_value = fatalities_range(analysis_feature[field_index])
            else:
                row_value = format_number(
                    analysis_feature[field_index],
                    enable_rounding=is_rounded,
                    is_population=is_population)
            row_stats = {
                'key': field['key'],
                'name': header,
                'value': row_value
            }
            report_stats.append(row_stats)

    # Give report section
    exposure_type = layer_definition_type(exposure_layer)
    header_label = exposure_type['name']
    summary.append({
        'header_label': header_label,
        # This should depend on exposure unit
        # TODO: Change this so it can take the unit dynamically
        'value_label': value_header,
        'rows': report_stats
    })

    header = resolve_from_dictionary(extra_args, ['header'])
    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')
    table_header = table_header_format.format(
        title=provenance['map_legend_title'],
        unit=hazard_classification['classification_unit'])

    # Section notes
    note_format = resolve_from_dictionary(
        extra_args, ['concept_notes', 'note_format'])

    if is_population:
        concepts = resolve_from_dictionary(
            extra_args, ['concept_notes', 'population_concepts'])
    else:
        concepts = resolve_from_dictionary(
            extra_args, ['concept_notes', 'general_concepts'])

    notes = []
    for concept in concepts:
        note = note_format.format(**concept)
        notes.append(note)

    context['header'] = header
    context['summary'] = summary
    context['table_header'] = table_header
    context['notes'] = notes

    return context
