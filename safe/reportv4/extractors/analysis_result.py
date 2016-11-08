# coding=utf-8
import os

from safe.definitionsv4.exposure import exposure_population
from safe.utilities.i18n import tr
from safe.definitionsv4.hazard_classifications import generic_hazard_classes

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def sum_field_by_hazard(layer, hazard_classification, field_name):
    """

    :param layer:
    :type layer: qgis.core.QgsVectorLayer
    :param hazard_classification:
    :return: dict
    """
    classes = hazard_classification.get('classes')
    result = []
    for c in classes:
        result.append({
            'key': c.get('key'),
            'name': c.get('name'),
            'value': 0
        })

    hazard_class_idx = layer.fieldNameIndex('hazard_class')
    target_field_idx = layer.fieldNameIndex(field_name)
    for f in layer.getFeatures():
        attrs = f.attributes()
        try:
            hazard_class = attrs[hazard_class_idx]
            idx = [
                i for i, v in enumerate(result) if v['key'] == hazard_class
                ][0]
            result[idx]['value'] += attrs[target_field_idx]
        except:
            pass

    return result


def count_field_by_hazard(layer, hazard_classification, field_name):
    """

    :param layer:
    :type layer: qgis.core.QgsVectorLayer
    :param hazard_classification:
    :return: dict
    """
    class_name = [c.get('key') for c in hazard_classification.get('classes')]
    result = {}
    for c in class_name:
        result[c] = 0

    hazard_class_idx = layer.fieldNameIndex('hazard_class')
    for f in layer.getFeatures():
        attrs = f.attributes()
        result[attrs[hazard_class_idx]] += 1

    return result


def sum_affected_field(layer, hazard_classification, field_name):
    """

    :param layer:
    :type layer: qgis.core.QgsVectorLayer
    :param field_name:
    :return: dict
    """
    hazard_class = hazard_classification.get('classes')
    affected_dict = {}
    for c in hazard_class:
        affected_dict[c.get('key')] = c.get('affected')
    result = {
        'affected': 0,
        'unaffected': 0,
        'total': 0,
    }
    hazard_class_idx = layer.fieldNameIndex('hazard_class')
    target_field_idx = layer.fieldNameIndex(field_name)
    for f in layer.getFeatures():
        attrs = f.attributes()
        try:
            if affected_dict.get(attrs[hazard_class_idx]):
                result['affected'] += attrs[target_field_idx]
            else:
                result['unaffected'] += attrs[target_field_idx]
        except:
            pass

    result['total'] = result['affected'] + result['unaffected']
    return result


def count_affected_field(layer, hazard_classification, field_name):
    """

    :param layer:
    :type layer: qgis.core.QgsVectorLayer
    :param field_name:
    :return: dict
    """
    hazard_class = hazard_classification.get('classes')
    affected_dict = {}
    for c in hazard_class:
        affected_dict[c.get('key')] = c.get('affected')
    result = {
        'affected': 0,
        'unaffected': 0,
        'total': 0,
    }
    hazard_class_idx = layer.fieldNameIndex('hazard_class')
    for f in layer.getFeatures():
        attrs = f.attributes()
        if affected_dict.get(attrs[hazard_class_idx]):
            result['affected'] += 1
        else:
            result['unaffected'] += 1

    result['total'] = result['affected'] + result['unaffected']
    return result


def analysis_result_extractor(impact_report, component_metadata):
    """
    Extracting analysis result from the impact layer

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
    analysis_layer = impact_report.analysis_layer
    """:type: qgis.core.QgsVectorLayer"""
    fields = impact_layer.pendingFields()
    field_names = [field.name() for field in fields]

    # TODO: Derive proper question string
    question = None

    # find hazard class
    hazard_classification = None
    hazard_stats = None
    summary = None
    evacuation_needs = None

    analysis_feature = analysis_layer.getFeatures().next()
    analysis_fields = analysis_layer.pendingFields()
    if 'hazard_class' in field_names:
        # retrieve hazard classes
        # TODO: need a correct way to retrieve the classifications
        hazard_classification = generic_hazard_classes
        hazard_stats = []
        for h_class in hazard_classification['classes']:
            class_idx = analysis_layer.fieldNameIndex(h_class['key'])
            hazard_stats.append({
                'key': h_class['key'],
                'name': h_class['name'],
                'value': analysis_feature[class_idx],
            })

    context['header'] = tr('Analysis Results')
    context['hazard_stats'] = hazard_stats
    context['summary'] = summary
    context['question'] = question

    return context
