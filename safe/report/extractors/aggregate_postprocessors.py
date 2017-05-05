# coding=utf-8
"""Module used to generate context for aggregation postprocessors sections.
"""

from PyQt4.QtCore import QPyNullVariant
from collections import OrderedDict

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    aggregation_name_field,
    displaced_field,
    male_displaced_count_field)
from safe.definitions.field_groups import (
    age_displaced_count_group,
    gender_displaced_count_group,
    vulnerability_displaced_count_group)
from safe.definitions.minimum_needs import minimum_needs_fields
from safe.definitions.post_processors import (
    age_postprocessors,
    female_postprocessors,
    gender_postprocessors,
    vulnerability_postprocessors)
from safe.definitions.utilities import postprocessor_output_field
from safe.report.extractors.util import (
    value_from_field_name,
    resolve_from_dictionary, layer_definition_type)
from safe.utilities.rounding import format_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def aggregation_postprocessors_extractor(impact_report, component_metadata):
    """Extracting aggregate result of demographic.

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
    context = {
        'sections': OrderedDict()
    }

    """Initializations"""

    extra_args = component_metadata.extra_args
    # Find out aggregation report type
    exposure_layer = impact_report.exposure
    aggregation_summary = impact_report.aggregation_summary
    analysis_layer = impact_report.analysis
    analysis_layer_fields = impact_report.analysis.keywords['inasafe_fields']
    debug_mode = impact_report.impact_function.debug_mode
    use_aggregation = bool(impact_report.impact_function.provenance[
        'aggregation_layer'])

    # Get exposure type definition
    exposure_type = layer_definition_type(exposure_layer)

    # this entire section is only for population exposure type
    if not exposure_type == exposure_population:
        return context

    # check zero displaced (there will be no output to display)
    try:
        displaced_field_name = analysis_layer_fields[displaced_field['key']]
        total_displaced = value_from_field_name(
            displaced_field_name, analysis_layer)

        zero_displaced = False
        if total_displaced == 0:
            zero_displaced = True
    except KeyError:
        # in case no displaced field
        # let each section handled itself
        zero_displaced = False

    context['use_aggregation'] = use_aggregation
    if not use_aggregation:
        context['header'] = resolve_from_dictionary(
            extra_args, 'header')

    age_items = {
        'group': age_displaced_count_group,
        'group_header': u'Age breakdown (in affected area)',
        'fields': [postprocessor_output_field(p) for p in age_postprocessors]
    }
    gender_items = {
        'group': gender_displaced_count_group,
        'group_header': u'Gender breakdown (in affected area)',
        'fields': [
            postprocessor_output_field(p) for p in gender_postprocessors]
    }
    vulnerability_items = {
        'group': vulnerability_displaced_count_group,
        'group_header': u'Vulnerability breakdown (in affected area)',
        'fields': [
            postprocessor_output_field(p) for p in (
                vulnerability_postprocessors)]
    }

    # check age_fields exists
    for field in age_items['fields']:
        if field['key'] in analysis_layer_fields:
            no_age_field = False
            break
    else:
        no_age_field = True

    # check gender_fields exists
    for field in gender_items['fields']:
        if field['key'] in analysis_layer_fields:
            no_gender_field = False
            break
    else:
        no_gender_field = True

    # check vulnerability_fields exists
    for field in vulnerability_items['fields']:
        if field['key'] in analysis_layer_fields:
            no_vulnerability_field = False
            break
    else:
        no_vulnerability_field = True

    age_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'age', 'header'])
    if zero_displaced:
        context['sections']['age'] = {
            'header': age_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'zero_displaced_message'])
        }
    elif no_age_field:
        context['sections']['age'] = {
            'header': age_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'no_age_rate_message'])
        }
    else:
        context['sections']['age'] = create_section(
            aggregation_summary,
            analysis_layer,
            age_items,
            age_section_header,
            use_aggregation=use_aggregation,
            debug_mode=debug_mode,
            extra_component_args=extra_args)

    gender_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'gender', 'header'])
    if zero_displaced:
        context['sections']['gender'] = {
            'header': gender_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'zero_displaced_message'])
        }
    elif no_gender_field:
        context['sections']['gender'] = {
            'header': gender_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'no_gender_rate_message'])
        }
    else:
        context['sections']['gender'] = create_section(
            aggregation_summary,
            analysis_layer,
            gender_items,
            gender_section_header,
            use_aggregation=use_aggregation,
            debug_mode=debug_mode,
            extra_component_args=extra_args)

    vulnerability_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'vulnerability', 'header'])
    if zero_displaced:
        context['sections']['vulnerability'] = {
            'header': vulnerability_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'zero_displaced_message'])
        }
    elif no_vulnerability_field:
        context['sections']['vulnerability'] = {
            'header': vulnerability_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'no_vulnerability_rate_message'])
        }
    else:
        context['sections']['vulnerability'] = create_section(
            aggregation_summary,
            analysis_layer,
            vulnerability_items,
            vulnerability_section_header,
            use_aggregation=use_aggregation,
            debug_mode=debug_mode,
            extra_component_args=extra_args)

    minimum_needs_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'minimum_needs', 'header'])
    # Don't show minimum needs if there is no displaced
    if zero_displaced:
        context['sections']['minimum_needs'] = {
            'header': minimum_needs_section_header,
            'empty': True,
            'message': resolve_from_dictionary(
                extra_args, ['defaults', 'zero_displaced_message'])
        }
    # Only provides minimum needs breakdown if there is aggregation layer
    elif use_aggregation:
        # minimum needs should provide unit for column headers
        units_label = []
        minimum_needs_items = {
            'group_header': u'Minimum needs breakdown (in affected area)',
            'fields': minimum_needs_fields
        }

        for field in minimum_needs_items['fields']:
            need = field['need_parameter']
            if isinstance(need, ResourceParameter):
                unit = None
                unit_abbreviation = need.unit.abbreviation
                if unit_abbreviation:
                    unit_format = '{unit}'
                    unit = unit_format.format(
                        unit=unit_abbreviation)
                units_label.append(unit)

        context['sections']['minimum_needs'] = create_section(
            aggregation_summary,
            analysis_layer,
            minimum_needs_items,
            minimum_needs_section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            extra_component_args=extra_args)
    else:
        sections_not_empty = True
        for _, value in context['sections'].iteritems():
            if value.get('rows'):
                break
        else:
            sections_not_empty = False

        context['sections_not_empty'] = sections_not_empty

    return context


def create_section(
        aggregation_summary, analysis_layer, postprocessor_fields,
        section_header,
        use_aggregation=True,
        units_label=None,
        debug_mode=False,
        extra_component_args=None):
    """Create demographic section context.

    :param aggregation_summary: Aggregation summary
    :type aggregation_summary: qgis.core.QgsVectorlayer

    :param analysis_layer: Analysis layer
    :type analysis_layer: qgis.core.QgsVectorLayer

    :param postprocessor_fields: Postprocessor fields to extract
    :type postprocessor_fields: list[dict]

    :param section_header: Section header text
    :type section_header: qgis.core.QgsVectorLayer

    :param use_aggregation: Flag, if using aggregation layer
    :type use_aggregation: bool

    :param units_label: Unit label for each column
    :type units_label: list[str]

    :param debug_mode: flag for debug_mode, affect number representations
    :type debug_mode: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict

    .. versionadded:: 4.0
    """
    if use_aggregation:
        return create_section_with_aggregation(
            aggregation_summary, analysis_layer, postprocessor_fields,
            section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            extra_component_args=extra_component_args)
    else:
        return create_section_without_aggregation(
            aggregation_summary, analysis_layer, postprocessor_fields,
            section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            extra_component_args=extra_component_args)


def create_section_with_aggregation(
        aggregation_summary, analysis_layer, postprocessor_fields,
        section_header,
        units_label=None,
        debug_mode=False,
        extra_component_args=None):
    """Create demographic section context with aggregation breakdown.

    :param aggregation_summary: Aggregation summary
    :type aggregation_summary: qgis.core.QgsVectorlayer

    :param analysis_layer: Analysis layer
    :type analysis_layer: qgis.core.QgsVectorLayer

    :param postprocessor_fields: Postprocessor fields to extract
    :type postprocessor_fields: list[dict]

    :param section_header: Section header text
    :type section_header: qgis.core.QgsVectorLayer

    :param units_label: Unit label for each column
    :type units_label: list[str]

    :param debug_mode: flag for debug_mode, affect number representations
    :type debug_mode: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict

    .. versionadded:: 4.0
    """
    aggregation_summary_fields = aggregation_summary.keywords[
        'inasafe_fields']
    analysis_layer_fields = analysis_layer.keywords[
        'inasafe_fields']
    enable_rounding = not debug_mode

    # retrieving postprocessor
    postprocessors_fields_found = []

    if type(postprocessor_fields) is dict:
        output_fields = postprocessor_fields['fields']
    else:
        output_fields = postprocessor_fields

    for output_field in output_fields:
        if output_field['key'] in aggregation_summary_fields:
            postprocessors_fields_found.append(output_field)

    if not postprocessors_fields_found:
        return {}

    # figuring out displaced field
    # no displaced field, can't show result
    if displaced_field['key'] not in analysis_layer_fields:
        return {}
    if displaced_field['key'] not in aggregation_summary_fields:
        return {}

    """Generating header name for columns"""

    # First column header is aggregation title
    default_aggregation_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'aggregation_header'])
    total_population_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'total_population_header'])
    columns = [
        aggregation_summary.title() or default_aggregation_header,
        total_population_header,
    ]
    row_values = []

    group_fields_found = []
    start_group_header = True
    for idx, output_field in enumerate(postprocessors_fields_found):
        name = output_field['name']
        if units_label or output_field.get('unit'):
            unit = None
            if units_label:
                unit = units_label[idx]
            elif output_field.get('unit'):
                unit = output_field.get('unit').get('abbreviation')

            if unit:
                header_format = u'{name} [{unit}]'
            else:
                header_format = u'{name}'

            header = header_format.format(
                name=name,
                unit=unit)
        else:
            header_format = u'{name}'
            header = header_format.format(name=name)

        if type(postprocessor_fields) is dict:
            try:
                group_header = postprocessor_fields['group_header']
                group_fields = postprocessor_fields['group']['fields']
                if output_field in group_fields:
                    group_fields_found.append(output_field)
                else:
                    columns.append(header)
                    continue
            except KeyError:
                group_fields_found.append(output_field)

        header_dict = {
            'name': header,
            'group_header': group_header,
            'start_group_header': start_group_header
        }

        start_group_header = False
        columns.append(header_dict)

    """Generating values for rows"""

    for feature in aggregation_summary.getFeatures():

        aggregation_name_index = aggregation_summary.fieldNameIndex(
            aggregation_name_field['field_name'])
        displaced_field_name = aggregation_summary_fields[
            displaced_field['key']]
        displaced_field_index = aggregation_summary.fieldNameIndex(
            displaced_field_name)

        aggregation_name = feature[aggregation_name_index]
        total_displaced = feature[displaced_field_index]

        if not total_displaced or isinstance(total_displaced, QPyNullVariant):
            # skip if total displaced null
            continue

        total_displaced = format_number(
            feature[displaced_field_index],
            enable_rounding=enable_rounding)

        row = [
            aggregation_name,
            total_displaced,
        ]

        if total_displaced == '0' and not debug_mode:
            continue

        for output_field in postprocessors_fields_found:
            field_name = aggregation_summary_fields[output_field['key']]
            field_index = aggregation_summary.fieldNameIndex(field_name)
            value = feature[field_index]

            value = format_number(
                value,
                enable_rounding=enable_rounding)
            row.append(value)

        row_values.append(row)

    """Generating total rows """

    total_displaced_field_name = analysis_layer_fields[
        displaced_field['key']]
    value = value_from_field_name(
        total_displaced_field_name, analysis_layer)
    value = format_number(
        value,
        enable_rounding=enable_rounding)
    total_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'total_header'])
    totals = [
        total_header,
        value
    ]
    for output_field in postprocessors_fields_found:
        field_name = analysis_layer_fields[output_field['key']]
        value = value_from_field_name(field_name, analysis_layer)
        value = format_number(
            value,
            enable_rounding=enable_rounding)
        totals.append(value)

    notes = resolve_from_dictionary(
        extra_component_args, ['defaults', 'notes'])

    if type(notes) is not list:
        notes = [notes]

    try:
        notes += postprocessor_fields['group']['notes']
    except (TypeError, KeyError):
        pass

    return {
        'notes': notes,
        'header': section_header,
        'columns': columns,
        'rows': row_values,
        'totals': totals,
        'group_header_colspan': len(group_fields_found)
    }


def create_section_without_aggregation(
        aggregation_summary, analysis_layer, postprocessor_fields,
        section_header,
        units_label=None,
        debug_mode=False,
        extra_component_args=None):
    """Create demographic section context without aggregation.

    :param aggregation_summary: Aggregation summary
    :type aggregation_summary: qgis.core.QgsVectorlayer

    :param analysis_layer: Analysis layer
    :type analysis_layer: qgis.core.QgsVectorLayer

    :param postprocessor_fields: Postprocessor fields to extract
    :type postprocessor_fields: list[dict]

    :param section_header: Section header text
    :type section_header: qgis.core.QgsVectorLayer

    :param units_label: Unit label for each column
    :type units_label: list[str]

    :param debug_mode: flag for debug_mode, affect number representations
    :type debug_mode: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict
    """
    aggregation_summary_fields = aggregation_summary.keywords[
        'inasafe_fields']
    analysis_layer_fields = analysis_layer.keywords[
        'inasafe_fields']
    enable_rounding = not debug_mode

    # retrieving postprocessor
    postprocessors_fields_found = []
    for output_field in postprocessor_fields['fields']:
        if output_field['key'] in aggregation_summary_fields:
            postprocessors_fields_found.append(output_field)

    if not postprocessors_fields_found:
        return {}

    # figuring out displaced field
    try:
        displaced_field_name = analysis_layer_fields[
            displaced_field['key']]
        displaced_field_name = aggregation_summary_fields[
            displaced_field['key']]
    except KeyError:
        # no displaced field, can't show result
        return {}

    """Generating header name for columns"""

    # First column header is aggregation title
    total_population_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'total_population_header'])
    columns = [
        section_header,
        total_population_header,
    ]

    """Generating values for rows"""
    row_values = []

    for idx, output_field in enumerate(postprocessors_fields_found):
        name = output_field['name']
        row = []
        if units_label or output_field.get('unit'):
            unit = None
            if units_label:
                unit = units_label[idx]
            elif output_field.get('unit'):
                unit = output_field.get('unit').get('abbreviation')

            if unit:
                header_format = u'{name} [{unit}]'
            else:
                header_format = u'{name}'

            header = header_format.format(
                name=name,
                unit=unit)
        else:
            header_format = u'{name}'
            header = header_format.format(name=name)

        row.append(header)

        # if no aggregation layer, then aggregation summary only contain one
        # feature
        field_name = analysis_layer_fields[output_field['key']]
        value = value_from_field_name(
            field_name,
            analysis_layer)
        value = format_number(
            value,
            enable_rounding=enable_rounding)
        row.append(value)

        row_values.append(row)

    return {
        'columns': columns,
        'rows': row_values,
    }
