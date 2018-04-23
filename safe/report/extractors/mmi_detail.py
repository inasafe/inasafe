# coding=utf-8
"""Module used to generate context for MMI detail section."""
from builtins import range
from safe.definitions.exposure import exposure_population
from safe.definitions.hazard import hazard_earthquake
from safe.definitions.layer_geometry import (
    layer_geometry_raster,
    layer_geometry)
from safe.definitions.utilities import definition
from safe.report.extractors.util import (
    resolve_from_dictionary,
    value_from_field_name)
from safe.utilities.rounding import format_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def mmi_detail_extractor(impact_report, component_metadata):
    """Extracting MMI-related analysis result.

    This extractor should only be used for EQ Raster with Population.

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
    analysis_layer = impact_report.analysis
    analysis_layer_keywords = analysis_layer.keywords
    extra_args = component_metadata.extra_args
    use_rounding = impact_report.impact_function.use_rounding
    provenance = impact_report.impact_function.provenance
    hazard_keywords = provenance['hazard_keywords']
    exposure_keywords = provenance['exposure_keywords']

    # check if this is EQ raster with population
    hazard_type = definition(hazard_keywords['hazard'])
    if not hazard_type == hazard_earthquake:
        return context

    hazard_geometry = hazard_keywords[layer_geometry['key']]
    if not hazard_geometry == layer_geometry_raster['key']:
        return context

    exposure_type = definition(exposure_keywords['exposure'])
    if not exposure_type == exposure_population:
        return context

    header = resolve_from_dictionary(extra_args, 'header')

    context['header'] = header

    reported_fields = resolve_from_dictionary(extra_args, 'reported_fields')

    """Generate headers."""
    table_header = [
        resolve_from_dictionary(extra_args, 'mmi_header')
    ] + [v['header'] for v in reported_fields]

    """Extract MMI-related data"""
    # mmi is ranged from 1 to 10, which means: [1, 11)
    mmi_range = list(range(1, 11))
    rows = []
    roman_numeral = [
        'I',
        'II',
        'III',
        'IV',
        'V',
        'VI',
        'VII',
        'VIII',
        'IX',
        'X'
    ]
    for i in mmi_range:
        columns = [roman_numeral[i - 1]]
        for value in reported_fields:
            field = value['field']
            try:
                key_name = field['key'] % (i, )
                field_name = analysis_layer_keywords[key_name]
                # check field exists
                count = value_from_field_name(field_name, analysis_layer)
                if not count:
                    count = 0
            except KeyError:
                count = 0
            count = format_number(
                count,
                use_rounding=use_rounding,
                is_population=True)
            columns.append(count)

        rows.append(columns)

    """Extract total."""
    total_footer = [
        resolve_from_dictionary(extra_args, 'total_header')
    ]

    total_fields = resolve_from_dictionary(extra_args, 'total_fields')
    for field in total_fields:
        try:
            field_name = analysis_layer_keywords[field['key']]
            total = value_from_field_name(field_name, analysis_layer)
            if not total:
                total = 0
        except KeyError:
            total = 0
        total = format_number(
            total,
            use_rounding=use_rounding,
            is_population=True)
        total_footer.append(total)

    context['component_key'] = component_metadata.key
    context['mmi'] = {
        'header': table_header,
        'rows': rows,
        'footer': total_footer
    }

    return context
