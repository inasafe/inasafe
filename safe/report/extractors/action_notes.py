# coding=utf-8
from safe.definitions.hazard_classifications import hazard_classes_all
from safe.report.extractors.util import resolve_from_dictionary

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
    """
    context = {}
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['action_checklist']

    return context


def notes_assumptions_extractor(impact_report, component_metadata):
    """
    Extracting notes and assumptions of the exposure layer

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
    context = {}
    hazard_layer = impact_report.hazard
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context['header'] = resolve_from_dictionary(extra_args, 'header')
    context['items'] = provenance['notes']

    # Get hazard classification
    hazard_classification = None
    # retrieve hazard classification from hazard layer
    for classification in hazard_classes_all:
        classification_name = hazard_layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break

    for hazard_class in hazard_classification['classes']:
        if hazard_class['displacement_rate'] > 0:
            show_displacement_note = True
            break
    else:
        show_displacement_note = False

    if show_displacement_note:
        # add notes for displacement rate used
        displacement_note_format = resolve_from_dictionary(
            extra_args, 'displacement_rates_note_format')

        # generate rate description
        hazard_note_format = resolve_from_dictionary(
            extra_args, 'hazard_displacement_rates_note_format')
        hazard_note = []
        for hazard_class in hazard_classification['classes']:
            hazard_note.append(hazard_note_format.format(**hazard_class))

        rate_description = ', '.join(hazard_note)
        context['items'].append(
            displacement_note_format.format(rate_description=rate_description))

    return context
