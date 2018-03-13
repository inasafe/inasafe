# coding=utf-8
"""Module used to generate context for analysis question section."""
from safe.report.extractors.util import resolve_from_dictionary

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def analysis_question_extractor(impact_report, component_metadata):
    """Extracting analysis question from the impact layer.

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
    multi_exposure = impact_report.multi_exposure_impact_function
    if multi_exposure:
        return multi_exposure_analysis_question_extractor(
            impact_report, component_metadata)

    context = {}
    extra_args = component_metadata.extra_args
    provenance = impact_report.impact_function.provenance

    header = resolve_from_dictionary(extra_args, 'header')
    analysis_question = provenance['analysis_question']

    context['header'] = header
    context['analysis_questions'] = [analysis_question]

    return context


def multi_exposure_analysis_question_extractor(
        impact_report, component_metadata):
    """Extracting analysis question from the impact layer.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.3
    """
    context = {}
    extra_args = component_metadata.extra_args

    multi_exposure = impact_report.multi_exposure_impact_function
    provenance = multi_exposure.provenance

    header = resolve_from_dictionary(extra_args, 'header')
    analysis_questions = []

    analysis_question = provenance['analysis_question']
    analysis_questions.append(analysis_question)

    context['header'] = header
    context['analysis_questions'] = analysis_questions

    return context
