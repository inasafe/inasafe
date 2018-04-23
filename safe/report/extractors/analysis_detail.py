# coding=utf-8

"""Module used to generate context for analysis detail section."""
from builtins import range

import logging
from copy import deepcopy

from safe.definitions.exposure import (
    exposure_all, exposure_population, exposure_place)
from safe.definitions.fields import (
    exposure_type_field,
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_not_affected_field,
    total_field,
    total_not_exposed_field,
    affected_field,
    exposed_population_count_field,
    population_count_field)
from safe.definitions.utilities import definition
from safe.report.extractors.util import (
    resolve_from_dictionary,
    value_from_field_name,
    retrieve_exposure_classes_lists)
from safe.utilities.i18n import tr
from safe.utilities.metadata import active_classification
from safe.utilities.rounding import format_number
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'

LOGGER = logging.getLogger('InaSAFE')


def analysis_detail_extractor(impact_report, component_metadata):
    """Extracting analysis result from the impact layer.

    :param impact_report: The impact report that acts as a proxy to fetch
        all the data that extractor needed.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: The component metadata. Used to obtain
        information about the component we want to render.
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: Context for rendering phase.
    :rtype: dict

    .. versionadded:: 4.0
    """
    context = {}
    extra_args = component_metadata.extra_args

    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    analysis_feature = next(analysis_layer.getFeatures())
    exposure_summary_table = impact_report.exposure_summary_table
    if exposure_summary_table:
        exposure_summary_table_fields = exposure_summary_table.keywords[
            'inasafe_fields']
    provenance = impact_report.impact_function.provenance
    use_rounding = impact_report.impact_function.use_rounding
    hazard_keywords = provenance['hazard_keywords']
    exposure_keywords = provenance['exposure_keywords']

    """Initializations."""

    # Get hazard classification
    hazard_classification = definition(
        active_classification(hazard_keywords, exposure_keywords['exposure']))

    # Get exposure type definition
    exposure_type = definition(exposure_keywords['exposure'])
    # Only round the number when it is population exposure and we use rounding
    is_population = exposure_type is exposure_population

    # action for places with poopulation exposure
    is_place_with_population = False
    if exposure_type is exposure_place:
        exposure_fields = exposure_keywords['inasafe_fields']
        if exposure_fields.get(population_count_field['key']):
            is_place_with_population = True

    # Analysis detail only applicable for breakable exposure types:
    itemizable_exposures_all = [
        exposure for exposure in exposure_all
        if exposure.get('classifications')]
    if exposure_type not in itemizable_exposures_all:
        return context

    # Get breakdown field
    breakdown_field = None
    # I'm not sure what's the difference
    # It is possible to have exposure_type_field or exposure_class_field
    # at the moment
    breakdown_fields = [
        exposure_type_field,
        exposure_class_field
    ]
    for field in breakdown_fields:
        if field['key'] in exposure_summary_table_fields:
            breakdown_field = field
            break

    """Create detail header."""
    headers = []

    # breakdown header
    breakdown_header_template = ''
    if breakdown_field == exposure_type_field:
        breakdown_header_template = resolve_from_dictionary(
            extra_args, 'breakdown_header_type_format')
    elif breakdown_field == exposure_class_field:
        breakdown_header_template = resolve_from_dictionary(
            extra_args, 'breakdown_header_class_format')

    # check if there is header type associations
    type_header_mapping = resolve_from_dictionary(
        extra_args, 'exposure_type_header_mapping')

    if exposure_type['key'] in type_header_mapping:
        exposure_header = type_header_mapping[exposure_type['key']]
    else:
        exposure_header = exposure_type['name']

    headers.append(
        breakdown_header_template.format(exposure=exposure_header))

    # this is mapping for customizing double header for
    # affected/not affected hazard classes
    hazard_class_header_mapping = resolve_from_dictionary(
        extra_args,
        'hazard_class_header_mapping')
    # hazard header
    # TODO: we need to get affected and not_affected key from
    # definitions concept
    header_hazard_group = {
        'affected': {
            'hazards': [],
            'total': []
        },
        'not_affected': {
            'hazards': [],
            'total': []
        }
    }
    for key, group in header_hazard_group.items():
        if key in hazard_class_header_mapping:
            header_hazard_group[key].update(hazard_class_header_mapping[key])

    affected_header_index = None
    for index, hazard_class in enumerate(hazard_classification['classes']):
        # the tuple format would be:
        # (class name, is it affected, header background color

        hazard_class_name = hazard_class['name']
        affected = hazard_class.get('affected')

        if not affected and not affected_header_index:
            affected_header_index = index + 1
            affected_status = 'not_affected'
        elif affected:
            affected_status = 'affected'
        else:
            affected_status = 'not_affected'

        header_hazard_group[affected_status]['hazards'].append(
            hazard_class_name)
        headers.append(hazard_class_name)

    if affected_header_index:
        not_affected_header_index = len(hazard_classification['classes']) + 2
    else:
        affected_header_index = len(hazard_classification['classes']) + 1
        not_affected_header_index = affected_header_index + 2

    report_fields = []

    headers.insert(affected_header_index, total_affected_field['name'])
    header_hazard_group['affected']['total'].append(
        total_affected_field['name'])
    report_fields.append(total_affected_field)

    headers.insert(not_affected_header_index, total_not_affected_field['name'])
    header_hazard_group['not_affected']['total'].append(
        total_not_affected_field['name'])
    report_fields.append(total_not_affected_field)

    # affected, not affected, population (if applicable), not exposed,
    # total header
    report_fields += [total_not_exposed_field, total_field]

    place_pop_name = resolve_from_dictionary(
        extra_args, ['place_with_population', 'header'])
    if is_place_with_population:
        # we want to change header name for population
        duplicated_population_count_field = deepcopy(
            exposed_population_count_field)
        duplicated_population_count_field['name'] = place_pop_name
        report_fields.append(duplicated_population_count_field)

    report_fields_index = -2 + -(int(is_place_with_population))
    for report_field in report_fields[report_fields_index:]:
        headers.append(report_field['name'])

    """Create detail rows."""
    details = []
    for feat in exposure_summary_table.getFeatures():
        row = []

        # Get breakdown name
        exposure_summary_table_field_name = breakdown_field['field_name']
        field_index = exposure_summary_table.fieldNameIndex(
            exposure_summary_table_field_name)
        class_key = feat[field_index]

        row.append(class_key)

        # Get hazard count
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )

            group_key = None
            for key, group in header_hazard_group.items():
                if hazard_class['name'] in group['hazards']:
                    group_key = key
                    break

            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = exposure_summary_table_fields[field_key_name]
                field_index = exposure_summary_table.fieldNameIndex(field_name)
                # exposure summary table is in csv format, so the field
                # returned is always in text format
                count_value = int(float(feat[field_index]))
                count_value = format_number(
                    count_value,
                    use_rounding=use_rounding,
                    is_population=is_population)
                row.append({
                    'value': count_value,
                    'header_group': group_key
                })
            except KeyError:
                # in case the field was not found
                # assume value 0
                row.append({
                    'value': 0,
                    'header_group': group_key
                })

        skip_row = False

        for field in report_fields:
            group_key = None
            for key, group in header_hazard_group.items():
                if field['name'] in group['total']:
                    group_key = key
                    break

            field_index = exposure_summary_table.fieldNameIndex(
                field['field_name'])
            total_count = int(float(feat[field_index]))
            total_count = format_number(
                total_count,
                use_rounding=use_rounding,
                is_population=is_population)

            # we comment below code because now we want to show all rows,
            # we can uncomment if we want to remove the rows with zero total

            # if total_count == '0' and field == total_affected_field:
            #     skip_row = True
            #     break

            if group_key:
                if field == total_affected_field:
                    row.insert(
                        affected_header_index,
                        {
                            'value': total_count,
                            'header_group': group_key
                        })
                elif field == total_not_affected_field:
                    row.insert(
                        not_affected_header_index,
                        {
                            'value': total_count,
                            'header_group': group_key
                        })
                else:
                    row.append({
                        'value': total_count,
                        'header_group': group_key
                    })
            else:
                row.append(total_count)

        if skip_row:
            continue

        details.append(row)

    # retrieve classes definitions
    exposure_classes_lists = retrieve_exposure_classes_lists(exposure_keywords)

    # sort detail rows based on class order
    # create function to sort
    def sort_classes(_row):
        """Sort method to retrieve exposure class key index."""
        # class key is first column
        _class_key = _row[0]
        # find index in class list
        for i, _exposure_class in enumerate(exposure_classes_lists):
            if _class_key == _exposure_class['key']:
                index = i
                break
        else:
            index = -1

        return index

    # sort
    details = sorted(details, key=sort_classes)

    # retrieve breakdown name from classes list
    for row in details:
        class_key = row[0]
        for exposure_class in exposure_classes_lists:
            if class_key == exposure_class['key']:
                breakdown_name = exposure_class['name']
                break
        else:
            # attempt for dynamic translations
            breakdown_name = tr(class_key.capitalize())

        # replace class_key with the class name
        row[0] = breakdown_name

    """create total footers."""
    # create total header
    footers = [total_field['name']]
    # total for hazard
    save_total_affected_field = False
    for hazard_class in hazard_classification['classes']:
        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'],)
        if not hazard_class.get('affected'):
            save_total_affected_field = True

        group_key = None
        for key, group in header_hazard_group.items():
            if hazard_class['name'] in group['hazards']:
                group_key = key
                break

        try:
            # retrieve dynamic field name from analysis_fields keywords
            # will cause key error if no hazard count for that particular
            # class
            field_name = analysis_layer_fields[field_key_name]
            field_index = analysis_layer.fieldNameIndex(field_name)
            count_value = format_number(
                analysis_feature[field_index],
                use_rounding=use_rounding,
                is_population=is_population)
        except KeyError:
            # in case the field was not found
            # assume value 0
            count_value = '0'

        if count_value == '0':
            # if total affected for hazard class is zero, delete entire
            # column
            column_index = len(footers) + int(save_total_affected_field)
            # delete header column
            headers = headers[:column_index] + headers[column_index + 1:]
            for row_idx in range(0, len(details)):
                row = details[row_idx]
                row = row[:column_index] + row[column_index + 1:]
                details[row_idx] = row
            # reduce total affected and not affected column index by 1
            # since we are removing a column
            if group_key == affected_field['field_name']:
                affected_header_index -= 1
            else:
                not_affected_header_index -= 1
            continue
        footers.append({
            'value': count_value,
            'header_group': group_key
        })

    # for footers
    for field in report_fields:

        total_count = value_from_field_name(
            field['field_name'], analysis_layer)

        if not total_count and field['name'] == place_pop_name:
            field = population_count_field
            field['name'] = place_pop_name
            total_count = value_from_field_name(
                field['field_name'], analysis_layer)

        group_key = None
        for key, group in header_hazard_group.items():
            if field['name'] in group['total']:
                group_key = key
                break

        total_count = format_number(
            total_count,
            use_rounding=use_rounding,
            is_population=is_population)
        if group_key:
            if field == total_affected_field:
                footers.insert(
                    affected_header_index,
                    {
                        'value': total_count,
                        'header_group': group_key
                    })
            elif field == total_not_affected_field:
                footers.insert(
                    not_affected_header_index,
                    {
                        'value': total_count,
                        'header_group': group_key
                    })
            else:
                footers.append({
                    'value': total_count,
                    'header_group': group_key
                })
        else:
            footers.append(total_count)

    header = resolve_from_dictionary(
        extra_args, 'header')
    notes = resolve_from_dictionary(
        extra_args, 'notes')

    context['header'] = header
    context['group_border_color'] = resolve_from_dictionary(
        extra_args, 'group_border_color')
    context['notes'] = notes

    breakdown_header_index = 0

    # we want to include total affected and not affected as a group
    # to its class so len(report_fields) - 2
    total_header_index = len(headers) - (len(report_fields) - 2)
    context['detail_header'] = {
        'header_hazard_group': header_hazard_group,
        'breakdown_header_index': breakdown_header_index,
        'total_header_index': total_header_index
    }

    # modify headers to include double header
    affected_headers = []
    last_group = 0
    for i in range(breakdown_header_index, total_header_index):
        hazard_class_name = headers[i]
        group_key = None
        for key, group in header_hazard_group.items():
            if hazard_class_name in group['hazards'] or (
                    hazard_class_name in group['total']):
                group_key = key
                break

        if group_key and group_key not in affected_headers:
            affected_headers.append(group_key)
            headers[i] = {
                'name': hazard_class_name,
                'start': True,
                'header_group': group_key,
                'colspan': 1
            }
            last_group = i
            header_hazard_group[group_key]['start_index'] = i
        elif group_key:
            colspan = headers[last_group]['colspan']
            headers[last_group]['colspan'] = colspan + 1
            headers[i] = {
                'name': hazard_class_name,
                'start': False,
                'header_group': group_key
            }

    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')

    # check unit
    units = exposure_type['units']
    if units:
        unit = units[0]
        abbreviation = unit['abbreviation']
        if abbreviation:
            unit_string = '({abbreviation})'.format(abbreviation=abbreviation)
        else:
            unit_string = ''
    else:
        unit_string = ''

    table_header = table_header_format.format(
        title=provenance['map_legend_title'],
        unit=unit_string,
        exposure=exposure_header)
    table_header = ' '.join(table_header.split())

    context['detail_table'] = {
        'table_header': table_header,
        'headers': headers,
        'details': details,
        'footers': footers,
    }

    context['extra_table'] = {}

    # extra table for specific exposure if exist
    extra_fields = resolve_from_dictionary(extra_args, 'exposure_extra_fields')
    if exposure_type['key'] in list(extra_fields.keys()):

        # create header for the extra table
        extra_table_header_format = resolve_from_dictionary(
            extra_args, 'extra_table_header_format')
        extra_table_header = extra_table_header_format.format(
            exposure=exposure_header)

        # headers
        headers = []
        headers.append(
            breakdown_header_template.format(exposure=exposure_header))

        current_unit = None
        currency_unit = setting('currency', expected_type=str)
        for field in extra_fields[exposure_type['key']]:
            field_index = exposure_summary_table.fieldNameIndex(
                field['field_name'])
            if field_index < 0:
                LOGGER.debug(
                    'Field name not found: %s, field index: %s' % (
                        field['field_name'], field_index))
                continue

            units = field.get('units')
            if units:
                for unit in units:
                    if currency_unit == unit['key']:
                        current_unit = unit['name']
                        break
                if not current_unit:
                    current_unit = units[0]['name']

            header_format = '{header} ({unit})'
            headers.append(header_format.format(
                header=field['header_name'], unit=current_unit))

        # rows
        details = []
        for feat in exposure_summary_table.getFeatures():
            row = []

            # Get breakdown name
            exposure_summary_table_field_name = breakdown_field['field_name']
            field_index = exposure_summary_table.fieldNameIndex(
                exposure_summary_table_field_name)
            class_key = feat[field_index]

            row.append(class_key)

            for field in extra_fields[exposure_type['key']]:
                field_index = exposure_summary_table.fieldNameIndex(
                    field['field_name'])
                # noinspection PyBroadException
                try:
                    total_count = int(float(feat[field_index]))
                except:
                    LOGGER.debug(
                        'Field name not found: %s, field index: %s' % (
                            field['field_name'], field_index))
                    continue
                total_count = format_number(
                    total_count,
                    use_rounding=use_rounding,
                    is_population=is_population)
                row.append(total_count)

            details.append(row)

        details = sorted(details, key=sort_classes)

        context['extra_table'] = {
            'table_header': extra_table_header,
            'headers': headers,
            'details': details,
        }

    return context
