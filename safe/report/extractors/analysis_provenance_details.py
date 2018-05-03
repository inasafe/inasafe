# coding=utf-8
"""Module used to generate context for analysis provenance details."""


from collections import OrderedDict

from qgis.core import QgsDataSourceUri

from safe.definitions.provenance import (
    provenance_exposure_layer,
    provenance_hazard_layer,
    provenance_aggregation_layer,
    provenance_use_rounding,
)
from safe.gis.tools import decode_full_layer_uri
from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    resolve_from_dictionary,
    jinja2_output_as_string)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import resource_url, resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def analysis_provenance_details_extractor(impact_report, component_metadata):
    """Extracting provenance details of layers.

    This extractor would be the main provenance details extractor which produce
    tree view provenance details.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.1
    """
    context = {}
    extra_args = component_metadata.extra_args

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
        'keyword_version',
        'classification',
    ]

    use_rounding = impact_report.impact_function.use_rounding
    debug_mode = impact_report.impact_function.debug_mode

    # we define dict here to create a different object of keyword
    hazard_keywords = dict(impact_report.impact_function.provenance[
        'hazard_keywords'])

    # hazard_keywords doesn't have hazard_layer path information
    hazard_layer = QgsDataSourceUri.removePassword(
        decode_full_layer_uri(
            impact_report.impact_function.provenance.get(
                provenance_hazard_layer['provenance_key']))[0])
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
    exposure_layer = QgsDataSourceUri.removePassword(
        decode_full_layer_uri(
            impact_report.impact_function.provenance.get(
                provenance_exposure_layer['provenance_key']))[0])
    exposure_keywords['exposure_layer'] = exposure_layer

    header = resolve_from_dictionary(
        provenance_format_args, 'exposure_header')
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

    header = resolve_from_dictionary(
        provenance_format_args, 'aggregation_header')

    aggregation_provenance = {
        'header': header.title(),
        'provenances': None
    }

    # only if aggregation layer used
    if aggregation_keywords:
        # we define dict here to create a different object of keyword
        aggregation_keywords = dict(aggregation_keywords)

        # aggregation_keywords doesn't have aggregation_layer path information
        aggregation_layer = QgsDataSourceUri.removePassword(
            decode_full_layer_uri(
                impact_report.impact_function.provenance.get(
                    provenance_aggregation_layer['provenance_key']))[0])
        aggregation_keywords['aggregation_layer'] = aggregation_layer

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

    all_provenance_keywords = dict(impact_report.impact_function.provenance)

    # we add debug mode information to the provenance
    all_provenance_keywords[
        provenance_use_rounding['provenance_key']] = (
        'On' if use_rounding else 'Off')
    all_provenance_keywords['debug_mode'] = 'On' if debug_mode else 'Off'

    header = resolve_from_dictionary(
        provenance_format_args, 'analysis_environment_header')
    analysis_environment_provenance_items = OrderedDict()
    analysis_environment_provenance_keys = [
        'os',
        'inasafe_version',
        provenance_use_rounding['provenance_key'],
        'debug_mode',
        'qgis_version',
        'qt_version',
        'gdal_version',
        'pyqt_version']

    for item in analysis_environment_provenance_keys:
        analysis_environment_provenance_items[item] = (
            all_provenance_keywords[item])

    analysis_environment_provenance = {
        'header': header.title(),
        'provenances': headerize(analysis_environment_provenance_items)
    }

    impact_function_name = impact_report.impact_function.name
    header = resolve_from_dictionary(
        provenance_format_args, 'impact_function_header')
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


def analysis_provenance_details_simplified_extractor(
        impact_report, component_metadata):
    """Extracting simplified version of provenance details of layers.

    This extractor will produce provenance details which will be displayed in
    the main report.

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
            source=QgsDataSourceUri.removePassword(
                decode_full_layer_uri(hazard_keywords.get('source'))[0] or
                default_source))
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
            source=QgsDataSourceUri.removePassword(
                decode_full_layer_uri(exposure_keywords.get('source'))[0] or
                default_source))
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
            source=QgsDataSourceUri.removePassword(
                decode_full_layer_uri(aggregation_keywords.get('source'))[0] or
                default_source))
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


def analysis_provenance_details_report_extractor(
        impact_report, component_metadata):
    """Extracting the main provenance details to its own report.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.1
    """
    context = {}
    extra_args = component_metadata.extra_args

    components_list = resolve_from_dictionary(
        extra_args, 'components_list')

    context['brand_logo'] = resource_url(
        resources_path('img', 'logos', 'inasafe-logo-white.png'))
    for key, component in list(components_list.items()):
        context[key] = jinja2_output_as_string(
            impact_report, component['key'])

    context['inasafe_resources_base_dir'] = resources_path()

    return context


def analysis_provenance_details_pdf_extractor(
        impact_report, component_metadata):
    """Extracting the main provenance details to its own pdf report.

    For PDF generations

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.1
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    context = QGISComposerContext()

    # we only have html elements for this
    html_frame_elements = [
        {
            'id': 'analysis-provenance-details-report',
            'mode': 'text',
            'text': jinja2_output_as_string(
                impact_report, 'analysis-provenance-details-report'),
            'margin_left': 10,
            'margin_top': 10,
        }
    ]
    context.html_frame_elements = html_frame_elements
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
    for key, value in list(provenances.items()):
        if '_' in key:
            header = key.replace('_', ' ').title()
        else:
            header = key.title()

        header_list = header.split(' ')
        proper_word = None
        proper_word_index = None
        for index, word in enumerate(header_list):
            if word in list(special_case.keys()):
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

    # we need to delete item with no value
    for key, value in list(keywords.items()):
        if value is None:
            del keywords[key]

    ordered_keywords = OrderedDict()
    for key in order:
        if key in list(keywords.keys()):
            ordered_keywords[key] = keywords.get(key)

    for keyword in keywords:
        if keyword not in order:
            ordered_keywords[keyword] = keywords.get(keyword)

    return ordered_keywords
