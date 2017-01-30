# coding=utf-8
from safe.definitions.styles import green
from safe.definitions.fields import hazard_count_field, total_unaffected_field
from safe.definitions.hazard_classifications import hazard_classes_all
from safe.report.extractors.infographic_elements.svg_charts import \
    DonutChartContext
from safe.report.extractors.util import value_from_field_name
from safe.utilities.i18n import tr
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
    """
    context = {}

    hazard_layer = impact_report.hazard
    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']

    """Generate Donut chart for affected population"""

    # create context for the donut chart

    # retrieve hazard classification from hazard layer
    for classification in hazard_classes_all:
        classification_name = hazard_layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break
    else:
        hazard_classification = None

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
                enable_rounding=True,
                use_population_rounding=True)
        except KeyError:
            # in case the field was not found
            continue

        data.append(hazard_value)
        labels.append(hazard_class['name'])
        colors.append(hazard_class['color'].name())

    # add total unaffected
    field_name = analysis_layer_fields[total_unaffected_field['key']]
    hazard_value = value_from_field_name(field_name, analysis_layer)
    hazard_value = round_affected_number(
        hazard_value,
        enable_rounding=True,
        use_population_rounding=True)

    data.append(hazard_value)
    labels.append(total_unaffected_field['name'])
    colors.append(green.name())

    # add number for total unaffected
    donut_context = DonutChartContext(
        data=data,
        labels=labels,
        colors=colors,
        inner_radius_ratio=0.5,
        stroke_color='#fff',
        title=tr('Estimated total population'),
        total_header=tr('Population'),
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
    """
    context = {}

    population_donut_path = impact_report.component_absolute_output_path(
        'population-chart')

    if not population_donut_path:
        return context

    context['filepath'] = population_donut_path

    return context
