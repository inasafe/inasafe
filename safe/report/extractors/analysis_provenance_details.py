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

    keywords_order = [
        'title',
        'source',
        'layer_purpose',
        'layer_geometry',
        'hazard',
        'exposure',
        'hazard_category',
        'exposure_unit',
        'value_map',
        'value_maps',
        'inasafe_fields',
        'inasafe_default_values',
        'layer_mode',
        'hazard_layer',
        'exposure_layer',
        'aggregation_layer',
        'keywords_version']

    debug_mode = impact_report.impact_function.debug_mode

    # we define dict here to create a different object of keyword
    hazard_keywords = dict(impact_report.impact_function.provenance[
        'hazard_keywords'])

    # hazard_keywords doesn't have hazard_layer path information
    hazard_layer = impact_report.impact_function.provenance.get('hazard_layer')
    hazard_keywords['hazard_layer'] = hazard_layer

    # keep only value maps with IF exposure
    for keyword in ['value_maps', 'thresholds']:
        if hazard_keywords.get(keyword):
            temp_keyword = dict(hazard_keywords[keyword])
            for key in temp_keyword:
                if key not in impact_report.impact_function.provenance[
                        'exposure_keywords']['exposure']:
                    del hazard_keywords[keyword][key]

    header = resolve_from_dictionary(
        provenance_format_args, 'hazard_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'hazard_format')
    hazard_provenance = {
        'header': header.title(),
        'provenances': headerize(
            sorted_keywords_by_order(hazard_keywords, keywords_order))
    }

    # convert value if there is dict_keywords
    provenances = hazard_provenance['provenances']
    hazard_provenance['provenances'] = resolve_dict_keywords(provenances)

    # we define dict here to create a different object of keyword
    exposure_keywords = dict(impact_report.impact_function.provenance[
        'exposure_keywords'])

    # exposure_keywords doesn't have exposure_layer path information
    exposure_layer = impact_report.impact_function.provenance.get(
        'exposure_layer')
    exposure_keywords['exposure_layer'] = exposure_layer

    header = resolve_from_dictionary(
        provenance_format_args, 'exposure_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'exposure_format')
    exposure_provenance = {
        'header': header.title(),
        'provenances': headerize(
            sorted_keywords_by_order(exposure_keywords, keywords_order))
    }

    # convert value if there is dict_keywords
    provenances = exposure_provenance['provenances']
    exposure_provenance['provenances'] = resolve_dict_keywords(provenances)

    # aggregation keywords could be None so we don't define dict here
    aggregation_keywords = impact_report.impact_function.provenance[
        'aggregation_keywords']

    # aggregation_keywords doesn't have aggregation_layer path information
    aggregation_layer = impact_report.impact_function.provenance.get(
        'aggregation_layer')
    aggregation_keywords['aggregation_layer'] = aggregation_layer

    header = resolve_from_dictionary(
        provenance_format_args, 'aggregation_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'aggregation_format')

    aggregation_provenance = {
        'header': header.title(),
        'provenances': None
    }

    # only if aggregation layer used
    if aggregation_keywords:
        # we define dict here to create a different object of keyword
        aggregation_keywords = dict(aggregation_keywords)
        aggregation_provenance['provenances'] = headerize(
            sorted_keywords_by_order(aggregation_keywords, keywords_order))

        # convert value if there is dict_keywords
        provenances = aggregation_provenance['provenances']
        aggregation_provenance['provenances'] = resolve_dict_keywords(
            provenances)

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
        'header': header.title(),
        'provenances': headerize(analysis_environment_provenance_items)
    }

    impact_function_name = impact_report.impact_function.name
    header = resolve_from_dictionary(
        provenance_format_args, 'impact_function_header')
    provenance_format = resolve_from_dictionary(
        provenance_format_args, 'impact_function_format')
    impact_function_provenance = {
        'header': header.title(),
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
    """Create a header for each keyword.

    :param provenances: The keywords.
    :type provenances: dict

    :return: New keywords with header for every keyword.
    :rtype: dict
    """

    special_case = {
        'Inasafe': 'InaSAFE',
        'Qgis': 'QGIS',
        'Pyqt': 'PyQt',
        'Os': 'OS',
        'Gdal': 'GDAL',
        'Maps': 'Map'
    }
    for key, value in provenances.iteritems():
        if '_' in key:
            header = key.replace('_', ' ').title()
        else:
            header = key.title()

        header_list = header.split(' ')
        proper_word = None
        proper_word_index = None
        for index, word in enumerate(header_list):
            if word in special_case.keys():
                proper_word = special_case[word]
                proper_word_index = index

        if proper_word:
            header_list[proper_word_index] = proper_word

        header = ' '.join(header_list)

        provenances.update(
            {
                key: {
                    'header': '{header} '.format(header=header),
                    'content': value
                }
            })

    return provenances


def resolve_dict_keywords(keywords):
    """Replace dictionary content with html.

    :param keywords: The keywords.
    :type keywords: dict

    :return: New keywords with updated content.
    :rtype: dict
    """

    for keyword in ['value_map', 'inasafe_fields', 'inasafe_default_values']:
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
        keywords['value_maps']['content'] = value_maps
    if thresholds:
        thresholds = thresholds.get('content')
        thresholds = KeywordIO._threshold_to_row(thresholds).to_html()
        keywords['thresholds']['content'] = thresholds

    return keywords


def sorted_keywords_by_order(keywords, order):
    """Sort keywords based on defined order.

    :param keywords: Keyword to be sorted.
    :type keywords: dict

    :param order: Ordered list of key.
    :type order: list

    :return: Ordered dictionary based on order list.
    :rtype: OrderedDict
    """

    ordered_keywords = OrderedDict()
    for key in order:
        if key in keywords.keys():
            ordered_keywords[key] = keywords.get(key)

    for keyword in keywords:
        if keyword not in order:
            ordered_keywords[keyword] = keywords.get(keyword)

    return ordered_keywords
