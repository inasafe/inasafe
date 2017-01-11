# coding=utf-8

from safe.reportv4.extractors.util import layer_definition_type
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def action_checklist_extractor(impact_report, component_metadata):
    """Extracting action checklist of the exposure layer.

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

    # figure out exposure type
    exposure_type = layer_definition_type(impact_report.exposure)

    context['header'] = tr('Action Checklist')
    context['items'] = exposure_type['actions']

    return context


def notes_assumptions_extractor(impact_report, component_metadata):
    """
    Extracting notes and assumptions of the exposure layer

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

    # figure out exposure type
    exposure_type = layer_definition_type(impact_report.exposure)

    context['header'] = tr('Notes and assumptions')
    context['items'] = exposure_type['notes']

    return context
