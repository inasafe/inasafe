# coding=utf-8
from collections import OrderedDict

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    aggregation_name_field,
    population_count_field,
    affected_exposure_count_field,
    total_affected_field)
from safe.definitions.minimum_needs import minimum_needs_fields
from safe.definitions.post_processors import (
    age_postprocessors,
    female_postprocessors)
from safe.definitions.utilities import postprocessor_output_field
from safe.report.extractors.util import (
    value_from_field_name,
    resolve_from_dictionary)
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
    """
    context = {
        'sections': OrderedDict()
    }

    """Initializations"""

    extra_args = component_metadata.extra_args
    # Find out aggregation report type
    aggregation_impacted = impact_report.aggregation_impacted
    analysis_layer = impact_report.analysis
    debug_mode = impact_report.impact_function.debug_mode
    use_aggregation = bool(impact_report.impact_function.provenance[
        'aggregation_layer'])

    context['use_aggregation'] = use_aggregation
    if not use_aggregation:
        context['header'] = resolve_from_dictionary(
            extra_args, 'header')

    age_fields = [postprocessor_output_field(p) for p in age_postprocessors]
    gender_fields = [
        postprocessor_output_field(p) for p in female_postprocessors]

    age_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'age', 'header'])
    context['sections']['age'] = create_section(
        aggregation_impacted,
        analysis_layer,
        age_fields,
        age_section_header,
        use_aggregation=use_aggregation,
        debug_mode=debug_mode,
        population_rounding=True,
        extra_component_args=extra_args)

    gender_section_header = resolve_from_dictionary(
        extra_args, ['sections', 'gender', 'header'])
    context['sections']['gender'] = create_section(
        aggregation_impacted,
        analysis_layer,
        gender_fields,
        gender_section_header,
        use_aggregation=use_aggregation,
        debug_mode=debug_mode,
        population_rounding=True,
        extra_component_args=extra_args)

    # Only provides minimum needs breakdown if there is aggregation layer
    if use_aggregation:
        # minimum needs should provide unit for column headers
        units_label = []

        for field in minimum_needs_fields:
            need = field['need_parameter']
            if isinstance(need, ResourceParameter):
                unit = None
                unit_abbreviation = need.unit.abbreviation
                if unit_abbreviation:
                    unit_format = '{unit}'
                    unit = unit_format.format(
                        unit=unit_abbreviation)
                units_label.append(unit)

        minimum_needs_section_header = resolve_from_dictionary(
            extra_args, ['sections', 'minimum_needs', 'header'])
        context['sections']['minimum_needs'] = create_section(
            aggregation_impacted,
            analysis_layer,
            minimum_needs_fields,
            minimum_needs_section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            population_rounding=True,
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
        aggregation_impacted, analysis_layer, postprocessor_fields,
        section_header,
        use_aggregation=True,
        units_label=None,
        debug_mode=False,
        population_rounding=False,
        extra_component_args=None):
    """Create demographic section context.

    :param aggregation_impacted: Aggregation impacted
    :type aggregation_impacted: qgis.core.QgsVectorlayer

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

    :param population_rounding: flag population rounding, used when
        postprocessor represents population number
    :type population_rounding: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict
    """
    if use_aggregation:
        return create_section_with_aggregation(
            aggregation_impacted, analysis_layer, postprocessor_fields,
            section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            population_rounding=population_rounding,
            extra_component_args=extra_component_args)
    else:
        return create_section_without_aggregation(
            aggregation_impacted, analysis_layer, postprocessor_fields,
            section_header,
            units_label=units_label,
            debug_mode=debug_mode,
            population_rounding=population_rounding,
            extra_component_args=extra_component_args)


def create_section_with_aggregation(
        aggregation_impacted, analysis_layer, postprocessor_fields,
        section_header,
        units_label=None,
        debug_mode=False,
        population_rounding=False,
        extra_component_args=None):
    """Create demographic section context with aggregation breakdown.

    :param aggregation_impacted: Aggregation impacted
    :type aggregation_impacted: qgis.core.QgsVectorlayer

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

    :param population_rounding: flag population rounding, used when
        postprocessor represents population number
    :type population_rounding: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict
    """
    aggregation_impacted_fields = aggregation_impacted.keywords[
        'inasafe_fields']
    analysis_layer_fields = analysis_layer.keywords[
        'inasafe_fields']
    enable_rounding = not debug_mode

    # retrieving postprocessor
    postprocessors_fields_found = []
    for output_field in postprocessor_fields:
        if output_field['key'] in aggregation_impacted_fields:
            postprocessors_fields_found.append(output_field)

    if not postprocessors_fields_found:
        return {}

    # figuring out affected population field
    # for vector exposure dataset
    is_population_count_exist = (
        population_count_field['key'] in aggregation_impacted_fields and
        population_count_field['key'] in analysis_layer_fields)
    # for raster exposure dataset
    is_population_affected_count_exist = (
        affected_exposure_count_field['key'] % exposure_population['key']
        in aggregation_impacted_fields and
        total_affected_field['key'] in analysis_layer_fields)

    affected_population_field = None
    total_affected_population_field = None
    if is_population_count_exist:
        affected_population_field = population_count_field['key']
        total_affected_population_field = population_count_field['key']
    elif is_population_affected_count_exist:
        affected_population_field = affected_exposure_count_field['key'] % (
            exposure_population['key'], )
        total_affected_population_field = total_affected_field['key']

    if not affected_population_field or not total_affected_population_field:
        return {}

    """Generating header name for columns"""

    # First column header is aggregation title
    default_aggregation_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'aggregation_header'])
    total_population_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'total_population_header'])
    columns = [
        aggregation_impacted.title() or default_aggregation_header,
        total_population_header,
    ]
    row_values = []

    for idx, output_field in enumerate(postprocessors_fields_found):
        name = output_field['name']
        if units_label or output_field.get('unit'):
            unit = None
            if units_label:
                unit = units_label[idx]
            elif output_field.get('unit'):
                unit = output_field.get('unit').get('abbreviation')

            if unit:
                header_format = '{name} [{unit}]'
            else:
                header_format = '{name}'

            header = header_format.format(
                name=name,
                unit=unit)
        else:
            header_format = '{name}'
            header = header_format.format(name=name)

        columns.append(header)

    """Generating values for rows"""

    for feature in aggregation_impacted.getFeatures():

        aggregation_name_index = aggregation_impacted.fieldNameIndex(
            aggregation_name_field['field_name'])
        affected_population_name = aggregation_impacted_fields[
            affected_population_field]
        affected_population_index = aggregation_impacted.fieldNameIndex(
            affected_population_name)

        aggregation_name = feature[aggregation_name_index]
        total_affected = format_number(
            feature[affected_population_index],
            enable_rounding=enable_rounding)

        row = [
            aggregation_name,
            total_affected,
        ]

        all_zeros = True

        for output_field in postprocessors_fields_found:
            field_name = aggregation_impacted_fields[output_field['key']]
            field_index = aggregation_impacted.fieldNameIndex(field_name)
            value = format_number(
                feature[field_index],
                enable_rounding=enable_rounding)
            row.append(value)

            if not value == 0:
                all_zeros = False

        if not all_zeros:
            row_values.append(row)

    """Generating total rows """

    feature = analysis_layer.getFeatures().next()
    total_affected_population_name = analysis_layer_fields[
        total_affected_population_field]
    total_affected_population_index = analysis_layer.fieldNameIndex(
        total_affected_population_name)
    value = format_number(
        feature[total_affected_population_index],
        enable_rounding=enable_rounding)
    total_header = resolve_from_dictionary(
        extra_component_args, ['defaults', 'total_header'])
    totals = [
        total_header,
        value
    ]
    for output_field in postprocessors_fields_found:
        field_name = analysis_layer_fields[output_field['key']]
        field_index = analysis_layer.fieldNameIndex(field_name)
        value = format_number(
            feature[field_index],
            enable_rounding=enable_rounding)
        totals.append(value)

    notes = resolve_from_dictionary(
        extra_component_args, ['defaults', 'notes'])
    return {
        'notes': notes,
        'header': section_header,
        'columns': columns,
        'rows': row_values,
        'totals': totals,
    }


def create_section_without_aggregation(
        aggregation_impacted, analysis_layer, postprocessor_fields,
        section_header,
        units_label=None,
        debug_mode=False,
        population_rounding=False,
        extra_component_args=None):
    """Create demographic section context without aggregation.

    :param aggregation_impacted: Aggregation impacted
    :type aggregation_impacted: qgis.core.QgsVectorlayer

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

    :param population_rounding: flag population rounding, used when
        postprocessor represents population number
    :type population_rounding: bool

    :param extra_component_args: extra_args passed from report component
        metadata
    :type extra_component_args: dict

    :return: context for gender section
    :rtype: dict
    """
    aggregation_impacted_fields = aggregation_impacted.keywords[
        'inasafe_fields']
    analysis_layer_fields = analysis_layer.keywords[
        'inasafe_fields']
    enable_rounding = not debug_mode

    # retrieving postprocessor
    postprocessors_fields_found = []
    for output_field in postprocessor_fields:
        if output_field['key'] in aggregation_impacted_fields:
            postprocessors_fields_found.append(output_field)

    if not postprocessors_fields_found:
        return {}

    # figuring out affected population field
    # for vector exposure dataset
    is_population_count_exist = (
        population_count_field['key'] in aggregation_impacted_fields and
        population_count_field['key'] in analysis_layer_fields)
    # for raster exposure dataset
    is_population_affected_count_exist = (
        affected_exposure_count_field['key'] % exposure_population['key']
        in aggregation_impacted_fields and
        total_affected_field['key'] in analysis_layer_fields)

    affected_population_field = None
    total_affected_population_field = None
    if is_population_count_exist:
        affected_population_field = population_count_field['key']
        total_affected_population_field = population_count_field['key']
    elif is_population_affected_count_exist:
        affected_population_field = affected_exposure_count_field['key'] % (
            exposure_population['key'], )
        total_affected_population_field = total_affected_field['key']

    if not affected_population_field or not total_affected_population_field:
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
                header_format = '{name} [{unit}]'
            else:
                header_format = '{name}'

            header = header_format.format(
                name=name,
                unit=unit)
        else:
            header_format = '{name}'
            header = header_format.format(name=name)

        row.append(header)

        # if no aggregation layer, then aggregation impacted only contain one
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
