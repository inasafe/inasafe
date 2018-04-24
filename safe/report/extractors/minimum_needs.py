# coding=utf-8
"""Module used to generate context for minimum needs section."""
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitions.fields import displaced_field, additional_minimum_needs
from safe.definitions.minimum_needs import (
    minimum_needs_fields,
    minimum_needs_namespace)
from safe.report.extractors.util import (
    resolve_from_dictionary,
    value_from_field_name)
from safe.utilities.i18n import tr
from safe.utilities.rounding import format_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def minimum_needs_extractor(impact_report, component_metadata):
    """Extracting minimum needs of the impact layer.

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
    analysis_layer = impact_report.analysis
    analysis_keywords = analysis_layer.keywords['inasafe_fields']
    use_rounding = impact_report.impact_function.use_rounding

    header = resolve_from_dictionary(extra_args, 'header')
    context['header'] = header

    # check if displaced is not zero
    try:
        displaced_field_name = analysis_keywords[displaced_field['key']]
        total_displaced = value_from_field_name(
            displaced_field_name, analysis_layer)
        if total_displaced == 0:
            zero_displaced_message = resolve_from_dictionary(
                extra_args, 'zero_displaced_message')
            context['zero_displaced'] = {
                'status': True,
                'message': zero_displaced_message
            }
            return context
    except KeyError:
        # in case no displaced field
        pass

    # minimum needs calculation only affect population type exposure
    # check if analysis keyword have minimum_needs keywords
    have_minimum_needs_field = False
    for field_key in analysis_keywords:
        if field_key.startswith(minimum_needs_namespace):
            have_minimum_needs_field = True
            break

    if not have_minimum_needs_field:
        return context

    frequencies = {}
    # map each needs to its frequency groups
    for field in (minimum_needs_fields + additional_minimum_needs):
        need_parameter = field.get('need_parameter')
        if isinstance(need_parameter, ResourceParameter):
            frequency = need_parameter.frequency
        else:
            frequency = field.get('frequency')

        if frequency:
            if frequency not in frequencies:
                frequencies[frequency] = [field]
            else:
                frequencies[frequency].append(field)

    needs = []
    analysis_feature = next(analysis_layer.getFeatures())
    header_frequency_format = resolve_from_dictionary(
        extra_args, 'header_frequency_format')
    total_header = resolve_from_dictionary(extra_args, 'total_header')
    need_header_format = resolve_from_dictionary(
        extra_args, 'need_header_format')
    # group the needs by frequency
    for key, frequency in list(frequencies.items()):
        group = {
            'header': header_frequency_format.format(frequency=tr(key)),
            'total_header': total_header,
            'needs': []
        }
        for field in frequency:
            # check value exists in the field
            field_idx = analysis_layer.fields().lookupField(field['field_name'])
            if field_idx == -1:
                # skip if field doesn't exists
                continue
            value = format_number(
                analysis_feature[field_idx],
                use_rounding=use_rounding,
                is_population=True)

            unit_abbreviation = ''
            if field.get('need_parameter'):
                need_parameter = field['need_parameter']
                """:type: ResourceParameter"""
                name = tr(need_parameter.name)
                unit_abbreviation = need_parameter.unit.abbreviation

            else:
                if field.get('header_name'):
                    name = field.get('header_name')
                else:
                    name = field.get('name')

                need_unit = field.get('unit')
                if need_unit:
                    unit_abbreviation = need_unit.get('abbreviation')

            if unit_abbreviation:
                header = need_header_format.format(
                    name=name,
                    unit_abbreviation=unit_abbreviation)
            else:
                header = name

            item = {
                'header': header,
                'value': value
            }
            group['needs'].append(item)
        needs.append(group)

    context['component_key'] = component_metadata.key
    context['needs'] = needs

    return context
