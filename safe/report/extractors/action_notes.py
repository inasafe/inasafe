# coding=utf-8
"""Module used to generate context for action and notes sections.
"""
from safe.common.utilities import safe_dir
from safe.definitions.exposure import exposure_population
from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    resolve_from_dictionary,
    layer_definition_type,
    layer_hazard_classification,
    jinja2_output_as_string)
from safe.utilities.resources import (
    resource_url,
    resources_path)

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
    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args
    exposure_type = layer_definition_type(exposure_layer)

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['notes']

    # Get hazard classification
    hazard_classification = layer_hazard_classification(hazard_layer)

    # Check hazard affected class
    affected_classes = []
    for hazard_class in hazard_classification['classes']:
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
        hazard_note_format = resolve_from_dictionary(
            extra_args, 'hazard_displacement_rates_note_format')
        hazard_note = []
        for hazard_class in hazard_classification['classes']:
            hazard_note.append(hazard_note_format.format(**hazard_class))

        rate_description = ', '.join(hazard_note)

        for index, displacement_note in enumerate(
                displacement_note_dict['item_list']):
            displacement_note_dict['item_list'][index] = (
                displacement_note.format(rate_description=rate_description)
            )

        context['items'].append(displacement_note_dict)

    return context


def action_notes_extractor(impact_report, component_metadata):
    """Extracting action checklist and notes of the impact layer.

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

    resources_dir = safe_dir(sub_dir='../resources')
    context['inasafe_resources_base_dir'] = resources_dir

    return context


def action_notes_pdf_extractor(impact_report, component_metadata):
    """Extracting action checklist and notes of the impact layer.

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
