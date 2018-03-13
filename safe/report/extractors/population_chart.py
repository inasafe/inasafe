# coding=utf-8
"""Module used to generate context for population chart."""
from safe.definitions.fields import (
    hazard_count_field, total_not_affected_field)
from safe.definitions.styles import green
from safe.definitions.utilities import definition
from safe.report.extractors.infographic_elements.svg_charts import \
    DonutChartContext
from safe.report.extractors.util import (
    value_from_field_name,
    resolve_from_dictionary)
from safe.utilities.metadata import active_classification
from safe.utilities.rounding import round_affected_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def population_chart_extractor(impact_report, component_metadata):
    """Creating population donut chart.

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

    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    provenance = impact_report.impact_function.provenance
    hazard_keywords = provenance['hazard_keywords']
    exposure_keywords = provenance['exposure_keywords']

    """Generate Donut chart for affected population."""

    # create context for the donut chart

    # retrieve hazard classification from hazard layer
    hazard_classification = definition(
        active_classification(hazard_keywords, exposure_keywords['exposure']))

    if not hazard_classification:
        return context

    data = []
    labels = []
    colors = []

    for hazard_class in hazard_classification['classes']:

        # Skip if it is not affected hazard class
        if not hazard_class['affected']:
            continue

        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'],)

        try:
            # retrieve dynamic field name from analysis_fields keywords
            # will cause key error if no hazard count for that particular
            # class
            field_name = analysis_layer_fields[field_key_name]
            # Hazard label taken from translated hazard count field
            # label, string-formatted with translated hazard class label
            hazard_value = value_from_field_name(field_name, analysis_layer)
            hazard_value = round_affected_number(
                hazard_value,
                use_rounding=True,
                use_population_rounding=True)
        except KeyError:
            # in case the field was not found
            continue

        data.append(hazard_value)
        labels.append(hazard_class['name'])
        colors.append(hazard_class['color'].name())

    # add total not affected
    try:
        field_name = analysis_layer_fields[total_not_affected_field['key']]
        hazard_value = value_from_field_name(field_name, analysis_layer)
        hazard_value = round_affected_number(
            hazard_value,
            use_rounding=True,
            use_population_rounding=True)

        data.append(hazard_value)
        labels.append(total_not_affected_field['name'])
        colors.append(green.name())
    except KeyError:
        # in case the field is not there
        pass

    # add number for total not affected
    chart_title = resolve_from_dictionary(extra_args, 'chart_title')
    total_header = resolve_from_dictionary(extra_args, 'total_header')
    donut_context = DonutChartContext(
        data=data,
        labels=labels,
        colors=colors,
        inner_radius_ratio=0.5,
        stroke_color='#fff',
        title=chart_title,
        total_header=total_header,
        as_file=True)

    context['context'] = donut_context

    return context


def population_chart_to_png_extractor(impact_report, component_metadata):
    """Creating population donut chart.

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

    population_donut_path = impact_report.component_absolute_output_path(
        'population-chart')

    if not population_donut_path:
        return context

    context['filepath'] = population_donut_path

    return context
