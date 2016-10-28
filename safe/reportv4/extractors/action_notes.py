# coding=utf-8
import os

from safe.definitionsv4.exposure import exposure_population, exposure_road, \
    exposure_all
from safe.utilities.i18n import tr
from safe.definitionsv4.hazard_classifications import generic_hazard_classes

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/27/16'


def action_checklist_extractor(impact_report, component_metadata):
    """
    Extracting action checklist of the exposure layer

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport
    :param component_metadata: the componenet metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    # figure out analysis report type
    impact_layer = impact_report.impact_layer
    """:type: qgis.core.QgsVectorLayer"""
    fields = impact_layer.pendingFields()
    field_names = [field.name() for field in fields]

    actions = []
    for f_n in field_names:
        for e in exposure_all:
            if e['key'] == f_n:
                actions += e['actions']

    context['header'] = tr('Action Checklist')
    context['items'] = actions

    return context


def notes_assumptions_extractor(impact_report, component_metadata):
    """
    Extracting notes and assumptions of the exposure layer

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport
    :param component_metadata: the componenet metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    # figure out analysis report type
    impact_layer = impact_report.impact_layer
    """:type: qgis.core.QgsVectorLayer"""
    fields = impact_layer.pendingFields()
    field_names = [field.name() for field in fields]

    notes = []
    for f_n in field_names:
        for e in exposure_all:
            if e['key'] == f_n:
                notes += e['notes']

    context['header'] = tr('Notes and assumptions')
    context['items'] = notes

    return context
