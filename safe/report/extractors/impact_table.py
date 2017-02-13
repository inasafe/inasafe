# coding=utf-8

from __future__ import absolute_import

from collections import OrderedDict

from safe.common.utilities import safe_dir
from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    jinja2_output_as_string,
    resolve_from_dictionary)
from safe.utilities.resources import (
    resource_url,
    resources_path)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def impact_table_extractor(impact_report, component_metadata):
    """Extracting impact summary of the impact layer.

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

    # Imported here to avoid cyclic dependencies
    from safe.definitions.report import (
        analysis_result_component,
        analysis_breakdown_component,
        action_checklist_component,
        notes_assumptions_component,
        minimum_needs_component,
        aggregation_result_component,
        aggregation_postprocessors_component)

    analysis_result = jinja2_output_as_string(
        impact_report, analysis_result_component['key'])
    analysis_breakdown = jinja2_output_as_string(
        impact_report, analysis_breakdown_component['key'])
    action_checklist = jinja2_output_as_string(
        impact_report, action_checklist_component['key'])
    notes_assumptions = jinja2_output_as_string(
        impact_report, notes_assumptions_component['key'])
    minimum_needs = jinja2_output_as_string(
        impact_report, minimum_needs_component['key'])
    aggregation_result = jinja2_output_as_string(
        impact_report, aggregation_result_component['key'])
    aggregation_postprocessors = jinja2_output_as_string(
        impact_report, aggregation_postprocessors_component['key'])

    context['brand_logo'] = resource_url(
            resources_path('img', 'logos', 'inasafe-logo-white.png'))
    context['analysis_result'] = analysis_result
    context['analysis_breakdown'] = analysis_breakdown
    context['action_checklist'] = action_checklist
    context['notes_assumptions'] = notes_assumptions
    context['minimum_needs'] = minimum_needs
    context['aggregation_result'] = aggregation_result
    context['aggregation_postprocessors'] = aggregation_postprocessors

    default_source = resolve_from_dictionary(
        extra_args, ['defaults', 'source'])
    default_reference = resolve_from_dictionary(
        extra_args, ['defaults', 'reference'])
    provenance_format_args = resolve_from_dictionary(
        extra_args, 'provenance_format')

    hazard_keywords = impact_report.impact_function.provenance[
        'hazard_keywords']
    header = resolve_from_dictionary(
        provenance_format_args, 'hazard_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'hazard_format')
    hazard_provenance = {
        'header': header,
        'provenance': provenance_format.format(
            layer_name=hazard_keywords.get('title'),
            source=hazard_keywords.get('source') or default_source)
    }

    exposure_keywords = impact_report.impact_function.provenance[
        'exposure_keywords']
    header = resolve_from_dictionary(
        provenance_format_args, 'exposure_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'exposure_format')
    exposure_provenance = {
        'header': header,
        'provenance': provenance_format.format(
            layer_name=exposure_keywords.get('title'),
            source=exposure_keywords.get('source') or default_source)
    }

    aggregation_keywords = impact_report.impact_function.provenance[
        'aggregation_keywords']
    # only if aggregation layer used
    if aggregation_keywords:
        header = resolve_from_dictionary(
            provenance_format_args, 'aggregation_header')
        provenance_format = resolve_from_dictionary(
            provenance_format_args, 'aggregation_format')
        aggregation_provenance = {
            'header': header,
            'provenance': provenance_format.format(
                layer_name=aggregation_keywords.get('title'),
                source=aggregation_keywords.get('source') or default_source)
        }
    else:
        aggregation_provenance = None

    impact_function_name = impact_report.impact_function.name
    header = resolve_from_dictionary(
        provenance_format_args, 'impact_function_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'impact_function_format')
    impact_function_provenance = {
        'header': header,
        'provenance': provenance_format.format(
            impact_function_name=impact_function_name,
            reference=default_reference)
    }

    provenance_detail = OrderedDict()
    provenance_detail['hazard'] = hazard_provenance
    provenance_detail['exposure'] = exposure_provenance
    provenance_detail['aggregation'] = aggregation_provenance
    provenance_detail['impact_function'] = impact_function_provenance

    context['analysis_details'] = provenance_detail

    resources_dir = safe_dir(sub_dir='../resources')
    context['inasafe_resources_base_dir'] = resources_dir

    return context


def impact_table_pdf_extractor(impact_report, component_metadata):
    """Extracting impact summary of the impact layer.

    For PDF generations

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.ReportMetadata

    :return: context for rendering phase
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    context = QGISComposerContext()

    # we only have html elements for this
    html_frame_elements = [
        {
            'id': 'impact-report',
            'mode': 'text',
            'text': jinja2_output_as_string(
                impact_report, 'impact-report'),
            'margin_left': 10,
            'margin_right': 10,
        }
    ]
    context.html_frame_elements = html_frame_elements
    return context
