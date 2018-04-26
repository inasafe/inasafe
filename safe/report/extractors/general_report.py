# coding=utf-8
"""Module used to extract context for general summary."""
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    hazard_count_field,
    fatalities_field,
    total_exposed_field,
    exposure_hazard_count_field,
    exposure_total_exposed_field,
    displaced_field)
from safe.definitions.utilities import definition
from safe.report.extractors.util import (
    resolve_from_dictionary,
    value_from_field_name)
from safe.utilities.metadata import active_classification
from safe.utilities.rounding import format_number, fatalities_range

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def general_report_extractor(impact_report, component_metadata):
    """Extracting general analysis result from the impact layer.

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
        return multi_exposure_general_report_extractor(
            impact_report, component_metadata)

    context = {}
    extra_args = component_metadata.extra_args

    # figure out analysis report type
    analysis_layer = impact_report.analysis
    provenance = impact_report.impact_function.provenance
    use_rounding = impact_report.impact_function.use_rounding
    hazard_keywords = provenance['hazard_keywords']
    exposure_keywords = provenance['exposure_keywords']

    exposure_type = definition(exposure_keywords['exposure'])
    # Only round the number when it is population exposure and we use rounding
    is_population = exposure_type is exposure_population

    # find hazard class
    summary = []

    analysis_feature = next(analysis_layer.getFeatures())
    analysis_inasafe_fields = analysis_layer.keywords['inasafe_fields']

    exposure_unit = exposure_type['units'][0]
    hazard_header = resolve_from_dictionary(extra_args, 'hazard_header')
    if exposure_unit['abbreviation']:
        value_header = '{measure} ({abbreviation})'.format(**exposure_unit)
    else:
        value_header = '{name}'.format(**exposure_unit)

    # Get hazard classification
    hazard_classification = definition(
        active_classification(hazard_keywords, exposure_keywords['exposure']))

    # in case there is a classification
    if hazard_classification:

        # classified hazard must have hazard count in analysis layer
        hazard_stats = []
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )
            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = analysis_inasafe_fields[field_key_name]
                field_index = analysis_layer.fields().lookupField(field_name)
                # Hazard label taken from translated hazard count field
                # label, string-formatted with translated hazard class label
                hazard_label = hazard_class['name']

                hazard_value = format_number(
                    analysis_feature[field_index],
                    use_rounding=use_rounding,
                    is_population=is_population)
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'numbers': [hazard_value]
                }
            except KeyError:
                # in case the field was not found
                hazard_label = hazard_class['name']
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_label,
                    'numbers': ['0'],
                }

            hazard_stats.append(stats)

        # find total field
        try:
            field_name = analysis_inasafe_fields[total_exposed_field['key']]
            total = value_from_field_name(field_name, analysis_layer)
            total = format_number(
                total, use_rounding=use_rounding, is_population=is_population)
            stats = {
                'key': total_exposed_field['key'],
                'name': total_exposed_field['name'],
                'as_header': True,
                'numbers': [total]
            }
            hazard_stats.append(stats)
        except KeyError:
            pass

        summary.append({
            'header_label': hazard_header,
            'value_labels': [value_header],
            'rows': hazard_stats
        })

    # retrieve affected column
    report_stats = []

    reported_fields = resolve_from_dictionary(
        extra_args, 'reported_fields')
    for item in reported_fields:
        header = item['header']
        field = item['field']
        if field['key'] in analysis_inasafe_fields:
            field_index = analysis_layer.fields().lookupField(
                field['field_name'])
            if field == fatalities_field:
                # For fatalities field, we show a range of number
                # instead
                row_value = fatalities_range(analysis_feature[field_index])
            else:
                row_value = format_number(
                    analysis_feature[field_index],
                    use_rounding=use_rounding,
                    is_population=is_population)
            row_stats = {
                'key': field['key'],
                'name': header,
                'numbers': [row_value]
            }
            report_stats.append(row_stats)

    # Give report section
    header_label = exposure_type['name']
    summary.append({
        'header_label': header_label,
        # This should depend on exposure unit
        # TODO: Change this so it can take the unit dynamically
        'value_labels': [value_header],
        'rows': report_stats
    })

    header = resolve_from_dictionary(extra_args, ['header'])
    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')
    table_header = table_header_format.format(
        title=provenance['map_legend_title'],
        unit=hazard_classification['classification_unit'])

    # Section notes
    note_format = resolve_from_dictionary(
        extra_args, ['concept_notes', 'note_format'])

    if is_population:
        concepts = resolve_from_dictionary(
            extra_args, ['concept_notes', 'population_concepts'])
    else:
        concepts = resolve_from_dictionary(
            extra_args, ['concept_notes', 'general_concepts'])

    notes = []
    for concept in concepts:
        note = note_format.format(**concept)
        notes.append(note)

    context['component_key'] = component_metadata.key
    context['header'] = header
    context['summary'] = summary
    context['table_header'] = table_header
    context['notes'] = notes

    return context


def multi_exposure_general_report_extractor(impact_report, component_metadata):
    """Extracting general analysis result from the impact layer.

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
    analysis_layer = impact_report.analysis
    provenances = [
        impact_function.provenance for impact_function in (
            multi_exposure.impact_functions)]
    debug_mode = multi_exposure.debug
    population_exist = False

    hazard_keywords = provenances[0]['hazard_keywords']
    hazard_header = resolve_from_dictionary(extra_args, 'hazard_header')

    reported_fields = resolve_from_dictionary(extra_args, 'reported_fields')

    # Summarize every value needed for each exposure and extract later to the
    # context.
    summary = []
    map_legend_titles = []
    hazard_classifications = {}
    exposures_stats = []
    for provenance in provenances:
        map_legend_title = provenance['map_legend_title']
        map_legend_titles.append(map_legend_title)
        exposure_stats = {}
        exposure_keywords = provenance['exposure_keywords']
        exposure_type = definition(exposure_keywords['exposure'])
        exposure_stats['exposure'] = exposure_type
        # Only round the number when it is population exposure and it is not
        # in debug mode
        is_rounded = not debug_mode
        is_population = exposure_type is exposure_population
        if is_population:
            population_exist = True

        analysis_feature = next(analysis_layer.getFeatures())
        analysis_inasafe_fields = analysis_layer.keywords['inasafe_fields']

        exposure_unit = exposure_type['units'][0]
        if exposure_unit['abbreviation']:
            value_header = '{measure} ({abbreviation})'.format(
                measure=map_legend_title,
                abbreviation=exposure_unit['abbreviation'])
        else:
            value_header = '{name}'.format(name=map_legend_title)

        exposure_stats['value_header'] = value_header

        # Get hazard classification
        hazard_classification = definition(
            active_classification(hazard_keywords,
                                  exposure_keywords['exposure']))
        hazard_classifications[exposure_type['key']] = hazard_classification

        # in case there is a classification
        if hazard_classification:
            classification_result = {}
            reported_fields_result = {}
            for hazard_class in hazard_classification['classes']:
                # hazard_count_field is a dynamic field with hazard class
                # as parameter
                field_key_name = exposure_hazard_count_field['key'] % (
                    exposure_type['key'], hazard_class['key'])
                try:
                    # retrieve dynamic field name from analysis_fields keywords
                    # will cause key error if no hazard count for that
                    # particular class
                    field_name = analysis_inasafe_fields[field_key_name]
                    field_index = analysis_layer.fields().lookupField(field_name)
                    hazard_value = format_number(
                        analysis_feature[field_index],
                        use_rounding=is_rounded,
                        is_population=is_population)
                except KeyError:
                    # in case the field was not found
                    hazard_value = 0

                classification_result[hazard_class['key']] = hazard_value

            # find total field
            try:
                field_key_name = exposure_total_exposed_field['key'] % (
                    exposure_type['key'])
                field_name = analysis_inasafe_fields[field_key_name]
                total = value_from_field_name(field_name, analysis_layer)
                total = format_number(
                    total, use_rounding=is_rounded,
                    is_population=is_population)
                classification_result[total_exposed_field['key']] = total
            except KeyError:
                pass

            exposure_stats['classification_result'] = classification_result

        for item in reported_fields:
            field = item.get('field')
            multi_exposure_field = item.get('multi_exposure_field')
            row_value = '-'
            if multi_exposure_field:
                field_key = (
                    multi_exposure_field['key'] % (exposure_type['key']))
                field_name = (
                    multi_exposure_field['field_name'] % (
                        exposure_type['key']))
                if field_key in analysis_inasafe_fields:
                    field_index = analysis_layer.fields().lookupField(field_name)
                    row_value = format_number(
                        analysis_feature[field_index],
                        use_rounding=is_rounded,
                        is_population=is_population)

            elif field in [displaced_field, fatalities_field]:
                if field['key'] in analysis_inasafe_fields and is_population:
                    field_index = analysis_layer.fields().lookupField(field['name'])
                    if field == fatalities_field:
                        # For fatalities field, we show a range of number
                        # instead
                        row_value = fatalities_range(
                            analysis_feature[field_index])
                    else:
                        row_value = format_number(
                            analysis_feature[field_index],
                            use_rounding=is_rounded,
                            is_population=is_population)

            reported_fields_result[field['key']] = row_value

        exposure_stats['reported_fields_result'] = reported_fields_result
        exposures_stats.append(exposure_stats)

    # After finish summarizing value, then proceed to context extraction.

    # find total value and labels for each exposure
    value_headers = []
    total_values = []
    for exposure_stats in exposures_stats:
        # label
        value_header = exposure_stats['value_header']
        value_headers.append(value_header)

        # total value
        classification_result = exposure_stats['classification_result']
        total_value = classification_result[total_exposed_field['key']]
        total_values.append(total_value)

    classifications = list(hazard_classifications.values())
    is_item_identical = (
        classifications.count(
            classifications[0]) == len(classifications))
    if classifications and is_item_identical:
        hazard_stats = []
        for hazard_class in classifications[0]['classes']:
            values = []
            for exposure_stats in exposures_stats:
                classification_result = exposure_stats['classification_result']
                value = classification_result[hazard_class['key']]
                values.append(value)
            stats = {
                'key': hazard_class['key'],
                'name': hazard_class['name'],
                'numbers': values
            }
            hazard_stats.append(stats)

        total_stats = {
            'key': total_exposed_field['key'],
            'name': total_exposed_field['name'],
            'as_header': True,
            'numbers': total_values
        }
        hazard_stats.append(total_stats)

        summary.append({
            'header_label': hazard_header,
            'value_labels': value_headers,
            'rows': hazard_stats
        })
    # if there are different hazard classifications used in the analysis,
    # we will create a separate table for each hazard classification
    else:
        hazard_classification_groups = {}
        for exposure_key, hazard_classification in (
                iter(list(hazard_classifications.items()))):
            exposure_type = definition(exposure_key)
            if hazard_classification['key'] not in (
                    hazard_classification_groups):
                hazard_classification_groups[hazard_classification['key']] = [
                    exposure_type]
            else:
                hazard_classification_groups[
                    hazard_classification['key']].append(exposure_type)

        for hazard_classification_key, exposures in (
                iter(list(hazard_classification_groups.items()))):
            custom_headers = []
            custom_total_values = []
            # find total value and labels for each exposure
            for exposure_stats in exposures_stats:
                if exposure_stats['exposure'] not in exposures:
                    continue
                # label
                value_header = exposure_stats['value_header']
                custom_headers.append(value_header)

                # total value
                classification_result = exposure_stats['classification_result']
                total_value = classification_result[total_exposed_field['key']]
                custom_total_values.append(total_value)

            hazard_stats = []
            hazard_classification = definition(hazard_classification_key)
            for hazard_class in hazard_classification['classes']:
                values = []
                for exposure_stats in exposures_stats:
                    if exposure_stats['exposure'] not in exposures:
                        continue
                    classification_result = exposure_stats[
                        'classification_result']
                    value = classification_result[hazard_class['key']]
                    values.append(value)
                stats = {
                    'key': hazard_class['key'],
                    'name': hazard_class['name'],
                    'numbers': values
                }
                hazard_stats.append(stats)

            total_stats = {
                'key': total_exposed_field['key'],
                'name': total_exposed_field['name'],
                'as_header': True,
                'numbers': custom_total_values
            }
            hazard_stats.append(total_stats)

            summary.append({
                'header_label': hazard_header,
                'value_labels': custom_headers,
                'rows': hazard_stats
            })

    reported_fields_stats = []
    for item in reported_fields:
        field = item.get('field')
        values = []
        for exposure_stats in exposures_stats:
            reported_fields_result = exposure_stats['reported_fields_result']
            value = reported_fields_result[field['key']]
            values.append(value)
        stats = {
            'key': field['key'],
            'name': item['header'],
            'numbers': values
        }
        reported_fields_stats.append(stats)

    header_label = resolve_from_dictionary(
        extra_args, ['reported_fields_header'])
    summary.append({
        'header_label': header_label,
        'value_labels': value_headers,
        'rows': reported_fields_stats
    })

    header = resolve_from_dictionary(extra_args, ['header'])

    combined_map_legend_title = ''
    for index, map_legend_title in enumerate(map_legend_titles):
        combined_map_legend_title += map_legend_title
        if not (index + 1) == len(map_legend_titles):
            combined_map_legend_title += ', '

    table_header_format = resolve_from_dictionary(
        extra_args, 'table_header_format')
    table_header = table_header_format.format(
        title=combined_map_legend_title,
        unit=classifications[0]['classification_unit'])

    # Section notes
    note_format = resolve_from_dictionary(
        extra_args, ['concept_notes', 'note_format'])

    concepts = resolve_from_dictionary(
        extra_args, ['concept_notes', 'general_concepts'])

    if population_exist:
        concepts += resolve_from_dictionary(
            extra_args, ['concept_notes', 'population_concepts'])

    notes = []
    for concept in concepts:
        note = note_format.format(**concept)
        notes.append(note)

    context['component_key'] = component_metadata.key
    context['header'] = header
    context['summary'] = summary
    context['table_header'] = table_header
    context['notes'] = notes

    return context
