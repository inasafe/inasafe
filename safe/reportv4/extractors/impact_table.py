# coding=utf-8

from __future__ import absolute_import
from safe.common.utilities import safe_dir
from safe.reportv4.extractors.composer import QGISComposerContext
from safe.reportv4.extractors.util import jinja2_output_as_string
from safe.utilities.i18n import tr
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
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    # Imported here to avoid cyclic dependencies
    from safe.definitions.report import (
        analysis_result_component,
        population_infographic_component,
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

    # TODO: taken from hazard and exposure provenance
    hazard_provenance = tr('an unknown source')
    exposure_provenance = tr('an unknown source')
    provenance_details = {
        'hazard_provenance': hazard_provenance,
        'exposure_provenance': exposure_provenance
    }
    context['analysis_details'] = tr(
        'Hazard details'
        '<p>%(hazard_provenance)s</p>'
        'Exposure details'
        '<p>%(exposure_provenance)s</p>') % provenance_details

    resources_dir = safe_dir(sub_dir='../resources')
    context['inasafe_resources_base_dir'] = resources_dir

    return context


def impact_table_pdf_extractor(impact_report, component_metadata):
    """Extracting impact summary of the impact layer.

    For PDF generations

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

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
