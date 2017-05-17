# coding=utf-8
"""Module used to generate context for analysis provenance details."""
from __future__ import absolute_import

from collections import OrderedDict

from safe.report.extractors.util import resolve_from_dictionary
from safe.utilities.keyword_io import KeywordIO

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

    # we define dict here to create a different object of keyword
    hazard_keywords = dict(impact_report.impact_function.provenance[
        'hazard_keywords'])
    header = resolve_from_dictionary(
        provenance_format_args, 'hazard_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'hazard_format')
    hazard_provenance = {
        'header': header,
        'provenances': headerize(hazard_keywords)
    }

    # convert value if there is dict_keywords
    provenances = hazard_provenance['provenances']
    hazard_provenance['provenances'] = resolve_dict_keywords(provenances)

    # we define dict here to create a different object of keyword
    exposure_keywords = dict(impact_report.impact_function.provenance[
        'exposure_keywords'])
    header = resolve_from_dictionary(
        provenance_format_args, 'exposure_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'exposure_format')
    exposure_provenance = {
        'header': header,
        'provenances': headerize(exposure_keywords)
    }

    # convert value if there is dict_keywords
    provenances = exposure_provenance['provenances']
    exposure_provenance['provenances'] = resolve_dict_keywords(provenances)

    # aggregation keywords could be None so we don't define dict here
    aggregation_keywords = impact_report.impact_function.provenance[
        'aggregation_keywords']
    header = resolve_from_dictionary(
        provenance_format_args, 'aggregation_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'aggregation_format')

    aggregation_provenance = {
        'header': header,
        'provenances': None
    }

    # only if aggregation layer used
    if aggregation_keywords:
        # we define dict here to create a different object of keyword
        aggregation_keywords = dict(aggregation_keywords)
        aggregation_provenance['provenances'] = headerize(aggregation_keywords)

        # convert value if there is dict_keywords
        provenances = aggregation_provenance['provenances']
        aggregation_provenance['provenances'] = resolve_dict_keywords(provenances)

    else:
        aggregation_not_used = resolve_from_dictionary(
            extra_args, ['defaults', 'aggregation_not_used'])
        aggregation_provenance['provenances'] = aggregation_not_used

    header = resolve_from_dictionary(
        provenance_format_args, 'analysis_environment_header')
    analysis_environment_provenance_items = {}
    analysis_environment_provenance_keys = [
        'os',
        'inasafe_version',
        'qgis_version',
        'qt_version',
        'gdal_version',
        'pyqt_version']

    for item in analysis_environment_provenance_keys:
        analysis_environment_provenance_items.update({
            item: impact_report.impact_function.provenance[item]
        })

    analysis_environment_provenance = {
        'header': header,
        'provenances': headerize(analysis_environment_provenance_items)
    }

    impact_function_name = impact_report.impact_function.name
    header = resolve_from_dictionary(
        provenance_format_args, 'impact_function_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'impact_function_format')
    impact_function_provenance = {
        'header': header,
        'provenances': impact_function_name
    }

    provenance_detail = OrderedDict()
    provenance_detail['impact_function'] = impact_function_provenance
    provenance_detail['hazard'] = hazard_provenance
    provenance_detail['exposure'] = exposure_provenance
    provenance_detail['aggregation'] = aggregation_provenance
    provenance_detail['analysis_environment'] = analysis_environment_provenance

    analysis_details_header = resolve_from_dictionary(
        extra_args, ['header', 'analysis_detail'])

    context.update({
        'header': analysis_details_header,
        'details': provenance_detail
    })

    return context


def headerize(provenances):

    for key, value in provenances.iteritems():
        if '_' in key:
            header = key.replace('_', ' ')
        else:
            header = key
        provenances.update(
            {
                key: {
                    'header': '{header} '.format(header=header),
                    'content': value
                }
            })

    return provenances


def resolve_dict_keywords(keywords):

    dict_to_row_keywords = [
        'value_map', 'inasafe_fields', 'inasafe_default_fields']
    for keyword in dict_to_row_keywords:
        value = keywords.get(keyword)
        if value:
            value = value.get('content')
            value = KeywordIO._dict_to_row(value).to_html()
            keywords[keyword]['content'] = value

    value_maps = keywords.get('value_maps')
    thresholds = keywords.get('thresholds')
    if value_maps:
        value_maps = value_maps.get('content')
        value_maps = KeywordIO._value_maps_row(value_maps).to_html()
        # for key, value in value_maps.iteritems():
        #     value_maps[key] = KeywordIO._dict_to_row(value).to_html()
        keywords['value_maps']['content'] = value_maps
    if thresholds:
        thresholds = thresholds.get('content')
        thresholds = KeywordIO._threshold_to_row(thresholds).to_html()
        # for key, value in thresholds.iteritems():
        #     thresholds[key] = KeywordIO._dict_to_row(value)
        keywords['thresholds']['content'] = thresholds

    return keywords


def keywords_to_html_table(keywords):
    """Turn value maps and thresholds keywords to html table"""
