# coding=utf-8
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    hazard_count_field,
    total_affected_field,
    total_field,
    total_unaffected_field,
    total_not_exposed_field)
from safe.definitions.hazard_classifications import hazard_classes_all
from safe.report.extractors.util import (
    layer_definition_type,
    resolve_from_dictionary)
from safe.utilities.rounding import round_affected_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def analysis_result_extractor(impact_report, component_metadata):
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

    # figure out analysis report type
    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    provenance = impact_report.impact_function.provenance
    debug_mode = impact_report.impact_function.debug_mode

    exposure_type = layer_definition_type(exposure_layer)
    is_rounded = not debug_mode
    use_population_rounding = exposure_type == exposure_population

    # find hazard class
    hazard_classification = None
    summary = []

    analysis_feature = analysis_layer.getFeatures().next()
    analysis_inasafe_fields = analysis_layer.keywords['inasafe_fields']

    hazard_header = resolve_from_dictionary(extra_args, 'hazard_header')
    value_header = resolve_from_dictionary(extra_args, 'value_header')

    # in case there is a classification
    if 'classification' in hazard_layer.keywords:

        # retrieve hazard classification from hazard layer
        for classification in hazard_classes_all:
            classification_name = hazard_layer.keywords['classification']
            if classification_name == classification['key']:
                hazard_classification = classification
                break

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
                hazard_value = round_affected_number(
                    analysis_feature[field_index],
                    enable_rounding=is_rounded,
                    use_population_rounding=use_population_rounding)
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

        summary.append({
            'header_label': hazard_header,
            # This should depend on exposure unit
            # TODO: Change this so it can take the unit dynamically
            'value_label': value_header,
            'rows': hazard_stats
        })

    # retrieve affected column
    report_stats = []

    report_fields = [
        total_affected_field,
        total_not_exposed_field,
        total_unaffected_field,
        total_field
    ]
    for report_field in report_fields:
        if report_field['key'] in analysis_inasafe_fields:
            field_index = analysis_layer.fieldNameIndex(
                report_field['field_name'])
            row_label = report_field['name']
            row_value = round_affected_number(
                analysis_feature[field_index],
                enable_rounding=is_rounded,
                use_population_rounding=use_population_rounding)
            row_stats = {
                'key': report_field['key'],
                'name': row_label,
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

    # Proper title from reporting standard
    analysis_title = provenance['analysis_question']

    header = resolve_from_dictionary(extra_args, ['header'])

    context['header'] = header
    context['summary'] = summary
    context['title'] = analysis_title

    return context
