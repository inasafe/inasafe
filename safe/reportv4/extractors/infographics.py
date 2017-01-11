# coding=utf-8
"""Infographic extractor class for standard reporting.
"""
from collections import OrderedDict

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.common.utilities import safe_dir
from safe.definitionsv4.colors import green
from safe.definitionsv4.exposure import exposure_population
from safe.definitionsv4.fields import (
    total_affected_field,
    population_count_field,
    exposure_count_field,
    female_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field, analysis_name_field, hazard_count_field,
    total_unaffected_field)
from safe.definitionsv4.hazard_classifications import all_hazard_classes
from safe.definitionsv4.minimum_needs import minimum_needs_fields
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.extractors.composer import QGISComposerContext
from safe.reportv4.extractors.infographic_elements.svg_charts import \
    DonutChartContext
from safe.reportv4.extractors.util import round_affecter_number, \
    jinja2_output_as_string
from safe.utilities.i18n import tr
from safe.utilities.resources import resource_url, resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def value_from_field_name(field_name, analysis_layer):
    """Get the value of analysis layer based on field name.

    :param field_name: Field name of analysis layer that we want to get
    :type field_name: str

    :param analysis_layer: Analysis layer
    :type analysis_layer: qgis.core.QgsVectorLayer

    :return: return the valeu of a given field name of the analysis.
    """
    field_index = analysis_layer.fieldNameIndex(field_name)
    return analysis_layer.getFeatures().next()[field_index]


class PeopleInfographicElement(object):

    """Used as local context for People Infographic."""

    def __init__(self, header, icon, number):
        self._header = header
        self._icon = icon
        self._number = number

    @property
    def header(self):
        """Header of the section."""
        return self._header

    @property
    def icon(self):
        """Icon for the element."""
        return self._icon

    @property
    def number(self):
        """Number to be displayed for the element."""
        return round_affecter_number(
            self._number,
            enable_rounding=True,
            use_population_rounding=True)


class PeopleVulnerabilityInfographicElement(PeopleInfographicElement):

    """Used as local context for Vulnerability section."""

    def __init__(self, header, icon, number, percentage):
        super(PeopleVulnerabilityInfographicElement, self).__init__(
            header, icon, number)
        self._percentage = percentage

    @property
    def percentage(self):
        """Percentage value to be displayed for the element."""
        number_format = '{:.1f}'
        return number_format.format(self._percentage)


class PeopleMinimumNeedsInfographicElement(PeopleInfographicElement):

    """Used as local context for Minimum Needs section."""

    def __init__(self, header, icon, number, unit):
        super(PeopleMinimumNeedsInfographicElement, self).__init__(
            header, icon, number)
        self._unit = unit

    @property
    def unit(self):
        """Unit string to be displayed for the element."""
        return self._unit

    @property
    def number(self):
        """Overriden, number to be displayed for the element."""
        return self._number


def population_infographic_extractor(impact_report, component_metadata):
    """
    Extracting aggregate result of demographic.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    """Initializations"""
    analysis_layer = impact_report.analysis

    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    hazard_layer = impact_report.hazard
    icons = component_metadata.extra_args.get('icons')

    # this report sections only applies if it is a population report.
    population_fields = [
        population_count_field['key'],
        exposure_count_field['key'] % (exposure_population['key'], ),
    ] + [f['key'] for f in minimum_needs_fields]

    for field in population_fields:
        if field in analysis_layer_fields:
            break
    else:
        return context

    total_affected_fields = [
        population_count_field['key'],
        exposure_count_field['key'] % (exposure_population['key'], ),
        total_affected_field['key']
    ]

    for field in total_affected_fields:
        if field in analysis_layer_fields:
            total_affected = value_from_field_name(
                analysis_layer_fields[field],
                analysis_layer)
            break
    else:
        return context

    sections = OrderedDict()

    """People Section"""

    sections['people'] = {
        'header': tr('People'),
        'items': [
            PeopleInfographicElement(
                header=tr('Affected'),
                icon=icons.get(
                    total_affected_field['key']),
                number=total_affected
            )
        ]
    }

    """Vulnerability Section"""

    female_affected = value_from_field_name(
        female_count_field['field_name'],
        analysis_layer)

    female_percentage = female_affected * 100.0 / total_affected

    youth_affected = value_from_field_name(
        youth_count_field['field_name'],
        analysis_layer)

    youth_percentage = youth_affected * 100.0 / total_affected

    adult_affected = value_from_field_name(
        adult_count_field['field_name'],
        analysis_layer)

    adult_percentage = adult_affected * 100.0 / total_affected

    elderly_affected = value_from_field_name(
        elderly_count_field['field_name'],
        analysis_layer)

    elderly_percentage = elderly_affected * 100.0 / total_affected

    sections['vulnerability'] = {
        'header': tr('Vulnerability'),
        'small_header': tr(
            'from {number_affected} affected').format(
                number_affected=total_affected),
        'items': [
            PeopleVulnerabilityInfographicElement(
                header=tr('Female'),
                icon=icons.get(
                    female_count_field['key']),
                number=female_affected,
                percentage=female_percentage
            ),
            PeopleVulnerabilityInfographicElement(
                header=tr('Youth'),
                icon=icons.get(
                    youth_count_field['key']),
                number=youth_affected,
                percentage=youth_percentage
            ),
            PeopleVulnerabilityInfographicElement(
                header=tr('Adult'),
                icon=icons.get(
                    adult_count_field['key']),
                number=adult_affected,
                percentage=adult_percentage
            ),
            PeopleVulnerabilityInfographicElement(
                header=tr('Elderly'),
                icon=icons.get(
                    elderly_count_field['key']),
                number=elderly_affected,
                percentage=elderly_percentage
            ),
        ]
    }

    """Minimum Needs Section"""

    items = []

    for field in minimum_needs_fields:
        need = field['need_parameter']
        if isinstance(need, ResourceParameter):

            needs_count = value_from_field_name(
                field['field_name'], analysis_layer)

            if need.unit.abbreviation:
                unit_string = '{unit}/{frequency}'.format(
                    unit=need.unit.abbreviation,
                    frequency=need.frequency)
            else:
                unit_string = tr('units')

            item = PeopleMinimumNeedsInfographicElement(
                header=field['name'],
                icon=icons.get(
                    field['key']),
                number=needs_count,
                unit=unit_string)
            items.append(item)

    # TODO: get from impact function provenance later
    needs_profile = NeedsProfile()

    sections['minimum_needs'] = {
        'header': tr('Minimum needs'),
        'small_header': needs_profile.provenance,
        'items': items,
    }

    """Generate Donut chart for affected population"""

    # create context for the donut chart

    # retrieve hazard classification from hazard layer
    for classification in all_hazard_classes:
        classification_name = hazard_layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break
    else:
        hazard_classification = None

    data = []
    labels = []
    colors = []

    for hazard_class in hazard_classification['classes']:

        # Skip if it is not affected hazard class
        if not hazard_class['affected']:
            continue

        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'], )

        try:
            # retrieve dynamic field name from analysis_fields keywords
            # will cause key error if no hazard count for that particular
            # class
            field_name = analysis_layer_fields[field_key_name]
            # Hazard label taken from translated hazard count field
            # label, string-formatted with translated hazard class label
            hazard_value = value_from_field_name(field_name, analysis_layer)
            hazard_value = round_affecter_number(
                hazard_value,
                enable_rounding=True,
                use_population_rounding=True)
        except KeyError:
            # in case the field was not found
            continue

        data.append(hazard_value)
        labels.append(hazard_class['name'])
        colors.append(hazard_class['color'].name())

    # add total unaffected
    field_name = analysis_layer_fields[total_unaffected_field['key']]
    hazard_value = value_from_field_name(field_name, analysis_layer)
    data.append(hazard_value)
    labels.append(total_unaffected_field['name'])
    colors.append(green.name())

    # add number for total unaffected
    donut_context = DonutChartContext(
        data=data,
        labels=labels,
        colors=colors,
        inner_radius_ratio=0.5,
        stroke_color='#fff',
        title=tr('Estimated total population'),
        total_header=tr('Population'),
        as_file=False)

    sections['population_donut'] = donut_context

    context['brand_logo'] = resource_url(
        resources_path('img', 'logos', 'inasafe-logo-white.png'))
    context['sections'] = sections
    context['title'] = analysis_layer.title() or value_from_field_name(
        analysis_name_field['field_name'], analysis_layer)

    return context


def infographic_layout_extractor(impact_report, component_metadata):
    """
    Extracting infographic result and format it with a layout.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}
    extra_args = component_metadata.extra_args
    infographics = extra_args['infographics']

    infographic_result = ''

    for component_key in infographics:
        result = jinja2_output_as_string(impact_report, component_key)
        infographic_result += result

    if not infographic_result:
        return context

    resources_dir = safe_dir(sub_dir='../resources')
    context['inasafe_resources_base_dir'] = resources_dir
    context['infographic_content'] = infographic_result
    footer_format = tr(
        '{version} | {analysis_date} | {analysis_time} | '
        'info@inasafe.org | BNPB-AusAid-World Bank-GFDRR-DMInnovation')
    context['footer'] = footer_format
    return context


def infographic_pdf_extractor(impact_report, component_metadata):
    """
    Extracting infographic result and format it for PDF generation.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    context = QGISComposerContext()

    # we only have html elements for this
    html_frame_elements = [
        {
            'id': 'infographic',
            'mode': 'text',
            'text': jinja2_output_as_string(
                impact_report, 'infographic-layout'),
            'margin_left': 10,
            'margin_right': 10,
        }
    ]
    context.html_frame_elements = html_frame_elements
    return context
