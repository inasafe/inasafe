# coding=utf-8
"""Module used to generate context for action and notes sections.
"""

from copy import deepcopy

from safe.definitions.exposure import exposure_population
from safe.definitions.utilities import definition
from safe.definitions.utilities import get_displacement_rate, is_affected
from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    resolve_from_dictionary,
    jinja2_output_as_string)
from safe.utilities.metadata import active_classification
from safe.utilities.resources import (
    resource_url,
    resources_path)
from safe.utilities.rounding import html_scientific_notation_rate

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def action_checklist_extractor(impact_report, component_metadata):
    """Extracting action checklist of the exposure layer.

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
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['action_checklist']

    return context


def notes_assumptions_extractor(impact_report, component_metadata):
    """Extracting notes and assumptions of the exposure layer

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
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args
    hazard_keywords = provenance['hazard_keywords']
    exposure_keywords = provenance['exposure_keywords']
    exposure_type = definition(exposure_keywords['exposure'])

    analysis_note_dict = resolve_from_dictionary(extra_args, 'analysis_notes')
    context['items'] = [analysis_note_dict]

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] += provenance['notes']

    # Get hazard classification
    hazard_classification = definition(
        active_classification(hazard_keywords, exposure_keywords['exposure']))

    # Check hazard affected class
    affected_classes = []
    for hazard_class in hazard_classification['classes']:
        if exposure_keywords['exposure'] == exposure_population['key']:
            # Taking from profile
            is_affected_class = is_affected(
                hazard=hazard_keywords['hazard'],
                classification=hazard_classification['key'],
                hazard_class=hazard_class['key'],
            )
            if is_affected_class:
                affected_classes.append(hazard_class)
        else:
            if hazard_class.get('affected', False):
                affected_classes.append(hazard_class)

    if affected_classes:
        affected_note_dict = resolve_from_dictionary(
            extra_args, 'affected_note_format')

        # generate hazard classes
        hazard_classes = ', '.join([
            c['name'] for c in affected_classes
        ])

        for index, affected_note in enumerate(affected_note_dict['item_list']):
            affected_note_dict['item_list'][index] = (
                affected_note.format(hazard_classes=hazard_classes)
            )

        context['items'].append(affected_note_dict)

    # Check hazard have displacement rate
    for hazard_class in hazard_classification['classes']:
        if hazard_class.get('displacement_rate', 0) > 0:
            have_displacement_rate = True
            break
    else:
        have_displacement_rate = False

    # Only show displacement note if analysis about population exposure
    if have_displacement_rate and exposure_type == exposure_population:
        # add notes for displacement rate used
        displacement_note_dict = resolve_from_dictionary(
            extra_args, 'displacement_rates_note_format')

        # generate rate description
        displacement_rates_note_format = resolve_from_dictionary(
            extra_args, 'hazard_displacement_rates_note_format')
        displacement_rates_note = []
        for hazard_class in hazard_classification['classes']:
            the_hazard_class = deepcopy(hazard_class)
            the_hazard_class['displacement_rate'] = get_displacement_rate(
                hazard=hazard_keywords['hazard'],
                classification=hazard_classification['key'],
                hazard_class=the_hazard_class['key']
            )
            displacement_rates_note.append(
                displacement_rates_note_format.format(**the_hazard_class))

        rate_description = ', '.join(displacement_rates_note)

        for index, displacement_note in enumerate(
                displacement_note_dict['item_list']):
            displacement_note_dict['item_list'][index] = (
                displacement_note.format(rate_description=rate_description)
            )

        context['items'].append(displacement_note_dict)

    # Check hazard have displacement rate
    for hazard_class in hazard_classification['classes']:
        if hazard_class.get('fatality_rate', 0) > 0:
            have_fatality_rate = True
            break
    else:
        have_fatality_rate = False

    if have_fatality_rate and exposure_type == exposure_population:
        # add notes for fatality rate used
        fatality_note_dict = resolve_from_dictionary(
            extra_args, 'fatality_rates_note_format')

        # generate rate description
        fatality_rates_note_format = resolve_from_dictionary(
            extra_args, 'hazard_fatality_rates_note_format')
        fatality_rates_note = []
        for hazard_class in hazard_classification['classes']:
            # we make a copy here because we don't want to
            # change the real value.
            copy_of_hazard_class = dict(hazard_class)
            if not copy_of_hazard_class['fatality_rate'] > 0:
                copy_of_hazard_class['fatality_rate'] = 0
            else:
                # we want to show the rate as a scientific notation
                copy_of_hazard_class['fatality_rate'] = (
                    html_scientific_notation_rate(
                        copy_of_hazard_class['fatality_rate']))

            fatality_rates_note.append(
                fatality_rates_note_format.format(**copy_of_hazard_class))

        rate_description = ', '.join(fatality_rates_note)

        for index, fatality_note in enumerate(fatality_note_dict['item_list']):
            fatality_note_dict['item_list'][index] = (
                fatality_note.format(rate_description=rate_description)
            )

        context['items'].append(fatality_note_dict)

    return context


def action_checklist_report_extractor(impact_report, component_metadata):
    """Extracting action checklist of the impact layer to its own report.

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
    for key, component in components_list.iteritems():
        context[key] = jinja2_output_as_string(
            impact_report, component['key'])

    context['inasafe_resources_base_dir'] = resources_path()

    return context


def action_checklist_report_pdf_extractor(impact_report, component_metadata):
    """Extracting action checklist of the impact layer to its own report.

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
            'id': 'action-checklist-report',
            'mode': 'text',
            'text': jinja2_output_as_string(
                impact_report, 'action-checklist-report'),
            'margin_left': 10,
            'margin_top': 10,
        }
    ]
    context.html_frame_elements = html_frame_elements
    return context
