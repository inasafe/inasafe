# coding=utf-8
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    hazard_count_field,
    total_affected_field,
    total_field,
    total_unaffected_field)
from safe.definitions.hazard import hazard_generic
from safe.definitions.hazard_category import (
    hazard_category_single_event,
    hazard_category_multiple_event)
from safe.definitions.hazard_classifications import all_hazard_classes
from safe.reportv4.extractors.util import layer_definition_type, \
    round_affecter_number
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def analysis_result_extractor(impact_report, component_metadata):
    """
    Extracting analysis result from the impact layer

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    # figure out analysis report type
    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    debug_mode = impact_report.impact_function.debug_mode

    exposure_type = layer_definition_type(exposure_layer)
    is_rounded = (
        exposure_type == exposure_population and
        not debug_mode)

    # find hazard class
    hazard_classification = None
    summary = []

    analysis_feature = analysis_layer.getFeatures().next()
    analysis_inasafe_fields = analysis_layer.keywords['inasafe_fields']
    # in case there is a classification
    if 'classification' in hazard_layer.keywords:

        # retrieve hazard classification from hazard layer
        for classification in all_hazard_classes:
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
                hazard_label = hazard_count_field['name'] % (
                    hazard_class['name'], )
                hazard_value = round_affecter_number(
                    analysis_feature[field_index], is_rounded)
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'value': hazard_value
                }
            except KeyError:
                # in case the field was not found
                hazard_label = hazard_count_field['name'] % (
                    hazard_class['name'], )
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'value': 0,
                }

            hazard_stats.append(stats)

        summary.append({
            'header_label': tr('Hazard Zone'),
            # This should depend on exposure unit
            # TODO: Change this so it can take the unit dynamically
            'value_label': tr('Count'),
            'rows': hazard_stats
        })

    # retrieve affected column
    report_stats = []

    report_fields = [
        total_affected_field,
        total_unaffected_field,
        total_field
    ]
    for report_field in report_fields:
        if report_field['key'] in analysis_inasafe_fields:
            field_index = analysis_layer.fieldNameIndex(
                report_field['field_name'])
            row_label = report_field['name']
            row_value = round_affecter_number(
                analysis_feature[field_index], is_rounded)
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
        'value_label': tr('Count'),
        'rows': report_stats
    })

    # Proper title from reporting standard
    question_template = ''
    hazard_type = layer_definition_type(hazard_layer)
    exposure_title = exposure_layer.title() or exposure_type['name']
    if hazard_type['key'] == hazard_generic['key']:
        question_template = tr('%(exposure)s affected')
        analysis_title = question_template % {
            'exposure': exposure_title
        }
    else:
        hazard_category = hazard_layer.keywords['hazard_category']
        if hazard_category == hazard_category_single_event['key']:
            question_template = tr(
                '%(exposure)s affected by %(hazard)s event')
        elif hazard_category == hazard_category_multiple_event['key']:
            question_template = tr(
                '%(exposure)s affected by %(hazard)s hazard')
        hazard_title = hazard_layer.title() or hazard_type['name']
        analysis_title = question_template % {
            'exposure': exposure_title,
            'hazard': hazard_title
        }

    analysis_title = analysis_title.capitalize()

    context['header'] = tr('Analysis Results')
    context['summary'] = summary
    context['title'] = analysis_title

    return context
