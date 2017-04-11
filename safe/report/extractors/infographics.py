# coding=utf-8
"""Infographic extractor class for standard reporting.
"""
from collections import OrderedDict

from jinja2.exceptions import TemplateError

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.common.utilities import safe_dir
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    total_affected_field,
    population_count_field,
    exposure_count_field,
    analysis_name_field, displaced_field)
from safe.definitions.minimum_needs import minimum_needs_fields
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    jinja2_output_as_string,
    value_from_field_name,
    resolve_from_dictionary,
    layer_hazard_classification)
from safe.utilities.resources import resource_url, resources_path
from safe.utilities.rounding import format_number

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class PeopleInfographicElement(object):

    """Used as local context for People Infographic.

    .. versionadded:: 4.0
    """

    def __init__(self, header, icon, number, header_note=None):
        """Create context holder for PeopleInfographicElement."""
        self._header = header
        self._header_note = header_note
        self._icon = icon
        self._number = number

    @property
    def header(self):
        """Header of the section."""
        return self._header

    @property
    def header_note(self):
        """Note of the header"""
        return self._header_note

    @property
    def icon(self):
        """Icon for the element."""
        return self._icon

    @property
    def number(self):
        """Number to be displayed for the element."""
        value = format_number(
            self._number,
            enable_rounding=True)
        return value


class PeopleVulnerabilityInfographicElement(PeopleInfographicElement):

    """Used as local context for Vulnerability section.

    .. versionadded:: 4.0
    """

    def __init__(self, header, icon, number, percentage):
        """Create context holder for PeopleVulnerabilityInfographicElement."""
        super(PeopleVulnerabilityInfographicElement, self).__init__(
            header, icon, number)
        self._percentage = percentage

    @property
    def percentage(self):
        """Percentage value to be displayed for the element."""
        number_format = '{:.1f}'
        return number_format.format(self._percentage)


class PeopleMinimumNeedsInfographicElement(PeopleInfographicElement):

    """Used as local context for Minimum Needs section.

    .. versionadded:: 4.0
    """

    def __init__(self, header, icon, number, unit):
        """Create context holder for PeopleMinimumNeedsInfographicElement."""
        super(PeopleMinimumNeedsInfographicElement, self).__init__(
            header, icon, number)
        self._unit = unit

    @property
    def unit(self):
        """Unit string to be displayed for the element."""
        return self._unit


def population_infographic_extractor(impact_report, component_metadata):
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
    context = {}
    extra_args = component_metadata.extra_args

    """Initializations"""
    hazard_layer = impact_report.hazard
    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    icons = component_metadata.extra_args.get('icons')

    # this report sections only applies if it is a population report.
    population_fields = [
        population_count_field['key'],
        exposure_count_field['key'] % (exposure_population['key'], ),
    ] + [f['key'] for f in minimum_needs_fields]

    for item in population_fields:
        if item in analysis_layer_fields:
            break
    else:
        return context

    # We try to get total affected field
    # if it didn't exists, check other fields to show
    total_affected_fields = [
        total_affected_field['key'],
        # We might want to check other fields, but turn it off until further
        # discussion
        population_count_field['key'],
        exposure_count_field['key'] % (exposure_population['key'], ),
    ]

    for item in total_affected_fields:
        if item in analysis_layer_fields:
            total_affected = value_from_field_name(
                analysis_layer_fields[item],
                analysis_layer)
            total_affected_field_used = item
            break
    else:
        return context

    if displaced_field['key'] in analysis_layer_fields:
        total_displaced = value_from_field_name(
            analysis_layer_fields[displaced_field['key']],
            analysis_layer)
    else:
        return context

    sections = OrderedDict()

    """People Section"""

    # Take default value from definitions
    people_header = resolve_from_dictionary(
        extra_args, ['sections', 'people', 'header'])
    people_items = resolve_from_dictionary(
        extra_args, ['sections', 'people', 'items'])

    # create context for affected infographic
    sub_header = resolve_from_dictionary(
        people_items[0], 'sub_header')

    # retrieve relevant header based on the fields we showed.
    sub_header = sub_header[total_affected_field_used]

    affected_infographic = PeopleInfographicElement(
        header=sub_header,
        icon=icons.get(
            total_affected_field['key']),
        number=total_affected)

    # create context for displaced infographic
    sub_header = resolve_from_dictionary(
        people_items[1], 'sub_header')
    sub_header_note_format = resolve_from_dictionary(
        people_items[1], 'sub_header_note_format')
    rate_description_format = resolve_from_dictionary(
        people_items[1], 'rate_description_format')
    rate_description = []

    hazard_classification = layer_hazard_classification(hazard_layer)
    for hazard_class in hazard_classification['classes']:
        displacement_rate = hazard_class.get('displacement_rate', 0)
        if displacement_rate:
            rate_description.append(
                rate_description_format.format(**hazard_class))

    rate_description_string = ', '.join(rate_description)

    sub_header_note = sub_header_note_format.format(
        rate_description=rate_description_string)

    displaced_infographic = PeopleInfographicElement(
        header=sub_header,
        header_note=sub_header_note,
        icon=icons.get(
            displaced_field['key']),
        number=total_displaced)

    sections['people'] = {
        'header': people_header,
        'items': [
            affected_infographic,
            displaced_infographic
        ]
    }

    """Vulnerability Section"""

    # Take default value from definitions
    vulnerability_items = resolve_from_dictionary(
        extra_args,
        ['sections', 'vulnerability', 'items'])

    vulnerability_section_header = resolve_from_dictionary(
        extra_args,
        ['sections', 'vulnerability', 'header'])

    vulnerability_section_sub_header_format = resolve_from_dictionary(
        extra_args,
        ['sections', 'vulnerability', 'sub_header_format'])

    infographic_elements = []
    for group in vulnerability_items:
        fields = group['fields']
        group_header = group['sub_group_header']
        bootstrap_column = group['bootstrap_column']
        element_column = group['element_column']
        headers = group['headers']
        elements = []
        for field, header in zip(fields, headers):
            field_key = field['key']
            try:
                field_name = analysis_layer_fields[field_key]
                value = value_from_field_name(
                    field_name, analysis_layer)
            except KeyError:
                # It means the field is not there
                continue

            if value:
                value_percentage = value * 100.0 / total_displaced
            else:
                value_percentage = 0

            infographic_element = PeopleVulnerabilityInfographicElement(
                header=header,
                icon=icons.get(field_key),
                number=value,
                percentage=value_percentage
            )
            elements.append(infographic_element)
        if elements:
            infographic_elements.append({
                'group_header': group_header,
                'bootstrap_column': bootstrap_column,
                'element_column': element_column,
                'items': elements
            })

    total_displaced_rounded = format_number(
        total_displaced,
        enable_rounding=True)

    sections['vulnerability'] = {
        'header': vulnerability_section_header,
        'small_header': vulnerability_section_sub_header_format.format(
            number_displaced=total_displaced_rounded),
        'items': infographic_elements
    }

    """Minimum Needs Section"""

    minimum_needs_header = resolve_from_dictionary(
        extra_args,
        ['sections', 'minimum_needs', 'header'])
    empty_unit_string = resolve_from_dictionary(
        extra_args,
        ['sections', 'minimum_needs', 'empty_unit_string'])

    items = []

    for item in minimum_needs_fields:
        need = item['need_parameter']
        if isinstance(need, ResourceParameter):

            needs_count = value_from_field_name(
                item['field_name'], analysis_layer)

            if need.unit.abbreviation:
                unit_string = '{unit}/{frequency}'.format(
                    unit=need.unit.abbreviation,
                    frequency=need.frequency)
            else:
                unit_string = empty_unit_string

            item = PeopleMinimumNeedsInfographicElement(
                header=item['name'],
                icon=icons.get(
                    item['key']),
                number=needs_count,
                unit=unit_string)
            items.append(item)

    # TODO: get from impact function provenance later
    needs_profile = NeedsProfile()

    sections['minimum_needs'] = {
        'header': minimum_needs_header,
        'small_header': needs_profile.provenance,
        'items': items,
    }

    """Population Charts"""

    population_donut_path = impact_report.component_absolute_output_path(
        'population-chart-png')

    css_label_classes = []
    try:
        population_chart_context = impact_report.metadata.component_by_key(
            'population-chart').context['context']
        """
        :type: safe.report.extractors.infographic_elements.svg_charts.
            DonutChartContext
        """
        for pie_slice in population_chart_context.slices:
            label = pie_slice['label']
            if not label:
                continue
            css_class = label.replace(' ', '').lower()
            css_label_classes.append(css_class)
    except KeyError:
        population_chart_context = None

    sections['population_chart'] = {
        'img_path': resource_url(population_donut_path),
        'context': population_chart_context,
        'css_label_classes': css_label_classes
    }

    context['brand_logo'] = resource_url(
        resources_path('img', 'logos', 'inasafe-logo-white.png'))
    context['sections'] = sections
    context['title'] = analysis_layer.title() or value_from_field_name(
        analysis_name_field['field_name'], analysis_layer)

    return context


def infographic_layout_extractor(impact_report, component_metadata):
    """Extracting infographic result and format it with a layout.

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

    infographics = resolve_from_dictionary(extra_args, ['infographics'])
    provenance = impact_report.impact_function.provenance

    infographic_result = ''

    for component_key in infographics:
        result = jinja2_output_as_string(impact_report, component_key)
        if result:
            infographic_result += result

    if not infographic_result:
        return context

    resources_dir = safe_dir(sub_dir='../resources')
    context['inasafe_resources_base_dir'] = resources_dir
    context['infographic_content'] = infographic_result
    version = provenance['inasafe_version']
    date_time = provenance['datetime']
    date = date_time.strftime('%Y-%m-%d')
    time = date_time.strftime('%H:%M')
    footer_format = resolve_from_dictionary(extra_args, 'footer_format')
    context['footer'] = footer_format.format(
        version=version, analysis_date=date, analysis_time=time)
    return context


def infographic_pdf_extractor(impact_report, component_metadata):
    """Extracting infographic result and format it for PDF generation.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        QgisComposerComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.0
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    context = QGISComposerContext()

    # we only have html elements for this
    try:
        infographic_html = jinja2_output_as_string(
            impact_report, 'infographic-layout')
    except TemplateError:
        return context

    if infographic_html.strip():
        # get component object
        margin_left = 0
        margin_right = 0
        margin_top = 4.5
        margin_bottom = 0
        html_frame_elements = [
            {
                'id': 'infographic',
                'mode': 'text',
                'text': jinja2_output_as_string(
                    impact_report, 'infographic-layout'),
                'margin_left': margin_left,
                'margin_top': margin_top,
                'height': (
                    component_metadata.page_height -
                    margin_top -
                    margin_bottom),
                'width': (
                    component_metadata.page_width -
                    margin_left -
                    margin_right)
            }
        ]
        context.html_frame_elements = html_frame_elements
    return context
