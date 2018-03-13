# coding=utf-8
"""Infographic extractor class for standard reporting.
"""
from safe.common.utilities import safe_dir
from safe.definitions.concepts import concepts
from safe.report.extractors.util import (
    resolve_from_dictionary,
    layer_hazard_classification)
from safe.utilities.resources import resource_url, resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def population_chart_legend_extractor(impact_report, component_metadata):
    """Extracting legend of population chart.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.2
    """
    context = {}

    context['inasafe_resources_base_dir'] = resources_path()

    """Population Charts"""

    population_donut_path = impact_report.component_absolute_output_path(
        'population-chart-png')

    css_label_classes = []
    try:
        population_chart_context = impact_report.metadata.component_by_key(
            'population-chart').context['context']
        """
        :type: safe.report.extractors.infographic_elements.svg_charts.
            DonutChartContext
        """
        for pie_slice in population_chart_context.slices:
            label = pie_slice['label']
            if not label:
                continue
            css_class = label.replace(' ', '').lower()
            css_label_classes.append(css_class)
    except KeyError:
        population_chart_context = None

    context['population_chart'] = {
        'img_path': resource_url(population_donut_path),
        'context': population_chart_context,
        'css_label_classes': css_label_classes
    }

    return context


def infographic_people_section_notes_extractor(
        impact_report, component_metadata):
    """Extracting notes for people section in the infographic.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.2
    """
    hazard_layer = impact_report.hazard
    extra_args = component_metadata.extra_args

    context = {}
    context['notes'] = []

    note = {
        'title': None,
        'description': resolve_from_dictionary(extra_args, 'extra_note'),
        'citations': None
    }
    context['notes'].append(note)

    concept_keys = ['affected_people', 'displaced_people']
    for key in concept_keys:
        note = {
            'title': concepts[key].get('name'),
            'description': concepts[key].get('description'),
            'citations': concepts[key].get('citations')[0]['text']
        }
        context['notes'].append(note)

    hazard_classification = layer_hazard_classification(hazard_layer)

    # generate rate description
    displacement_rates_note_format = resolve_from_dictionary(
        extra_args, 'hazard_displacement_rates_note_format')
    displacement_rates_note = []
    for hazard_class in hazard_classification['classes']:
        hazard_class['classification_unit'] = (
            hazard_classification['classification_unit'])
        displacement_rates_note.append(
            displacement_rates_note_format.format(**hazard_class))

    rate_description = ', '.join(displacement_rates_note)

    note = {
        'title': concepts['displacement_rate'].get('name'),
        'description': rate_description,
        'citations': concepts['displacement_rate'].get('citations')[0]['text']
    }

    context['notes'].append(note)

    return context
