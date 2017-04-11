# coding=utf-8
"""Module used to generate context for analysis provenance details."""
from __future__ import absolute_import

from collections import OrderedDict

from safe.report.extractors.util import resolve_from_dictionary

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def analysis_provenance_details_extractor(impact_report, component_metadata):
    """Extracting provenance details of layers.

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
    header = resolve_from_dictionary(
        provenance_format_args, 'aggregation_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'aggregation_format')
    # only if aggregation layer used
    if aggregation_keywords:
        provenance_string = provenance_format.format(
            layer_name=aggregation_keywords.get('title'),
            source=aggregation_keywords.get('source') or default_source)
    else:
        aggregation_not_used = resolve_from_dictionary(
            extra_args, ['defaults', 'aggregation_not_used'])
        provenance_string = aggregation_not_used

    aggregation_provenance = {
        'header': header,
        'provenance': provenance_string
    }

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

    analysis_details_header = resolve_from_dictionary(
        extra_args, ['header', 'analysis_detail'])

    context.update({
        'header': analysis_details_header,
        'details': provenance_detail
    })

    return context
