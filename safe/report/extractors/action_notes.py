# coding=utf-8

from safe.report.extractors.util import resolve_from_dictionary

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def action_checklist_extractor(impact_report, component_metadata):
    """Extracting action checklist of the exposure layer.

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
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['action_checklist']

    return context


def notes_assumptions_extractor(impact_report, component_metadata):
    """
    Extracting notes and assumptions of the exposure layer

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
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['notes']

    return context
