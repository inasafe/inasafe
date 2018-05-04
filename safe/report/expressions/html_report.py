# coding=utf-8

"""QGIS Expressions which are available in the QGIS GUI interface."""

import codecs
from os.path import dirname, join, exists
from BeautifulSoup import BeautifulSoup

from qgis.core import (
    qgsfunction,
    QgsExpressionContextUtils,
    QgsProject,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer)

from safe.definitions.constants import MULTI_EXPOSURE_ANALYSIS_FLAG
from safe.definitions.exposure import (
    exposure_population,
    exposure_road,
    exposure_structure,
    exposure_place,
    exposure_land_cover)
from safe.definitions.extra_keywords import extra_keyword_analysis_type
from safe.definitions.provenance import provenance_layer_analysis_impacted
from safe.definitions.reports.components import (
    analysis_question_component,
    general_report_component,
    mmi_detail_component,
    analysis_detail_component,
    action_checklist_component,
    notes_assumptions_component,
    minimum_needs_component,
    aggregation_result_component,
    aggregation_postprocessors_component,
    analysis_provenance_details_simplified_component)
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import generate_expression_help

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

group = tr('InaSAFE - HTML Elements')


def get_analysis_dir(exposure_key=None):
    """Retrieve an output directory of an analysis/ImpactFunction from a
    multi exposure analysis/ImpactFunction based on exposure type.

    :param exposure_key: An exposure keyword.
    :type exposure_key: str

    :return: A directory contains analysis outputs.
    :rtype: str
    """
    keyword_io = KeywordIO()
    layer_tree_root = QgsProject.instance().layerTreeRoot()
    all_groups = [
        child for child in layer_tree_root.children() if (
            isinstance(child, QgsLayerTreeGroup))]
    multi_exposure_group = None
    for group in all_groups:
        if group.customProperty(MULTI_EXPOSURE_ANALYSIS_FLAG):
            multi_exposure_group = group
            break

    if multi_exposure_group:
        multi_exposure_tree_layers = [
            child for child in multi_exposure_group.children() if (
                isinstance(child, QgsLayerTreeLayer))]
        exposure_groups = [
            child for child in multi_exposure_group.children() if (
                isinstance(child, QgsLayerTreeGroup))]

        def get_report_ready_layer(tree_layers):
            """Get a layer which has a report inn its directory.

            :param tree_layers: A list of tree layer nodes (QgsLayerTreeLayer)
            :type tree_layers: list

            :return: A vector layer
            :rtype: QgsMapLayer
            """
            for tree_layer in tree_layers:
                layer = tree_layer.layer()
                keywords = keyword_io.read_keywords(layer)
                extra_keywords_found = keywords.get('extra_keywords')
                provenance = keywords.get('provenance_data')
                if provenance:
                    exposure_keywords = provenance.get('exposure_keywords', {})
                    exposure_key_found = exposure_keywords.get('exposure')
                    if exposure_key_found and (
                            exposure_key == exposure_key_found):
                        return layer
                if not exposure_key and extra_keywords_found and (
                        extra_keywords_found[
                            extra_keyword_analysis_type['key']] == (
                                MULTI_EXPOSURE_ANALYSIS_FLAG)):
                    return layer
            return None

        layer = get_report_ready_layer(multi_exposure_tree_layers)

        if not layer:
            for exposure_group in exposure_groups:
                tree_layers = [
                    child for child in exposure_group.children() if (
                        isinstance(child, QgsLayerTreeLayer))]
                layer = get_report_ready_layer(tree_layers)
                if layer:
                    break

        if layer:
            return dirname(layer.source())

    return None


def get_impact_report_as_string(analysis_dir):
    """Retrieve an html string of table report (impact-report-output.html).

    :param analysis_dir: Directory of where the report located.
    :type analysis_dir: str

    :return: HTML string of the report.
    :rtype: str
    """
    html_report_products = [
        'impact-report-output.html',
        'multi-exposure-impact-report-output.html']
    output_dir_path = join(analysis_dir, 'output')

    for html_report_product in html_report_products:
        table_report_path = join(output_dir_path, html_report_product)
        if exists(table_report_path):
            break
        table_report_path = None

    if not table_report_path:
        return None

    # We can display an impact report.
    # We need to open the file in UTF-8, the HTML may have some accents
    with codecs.open(table_report_path, 'r', 'utf-8') as table_report_file:
        report = table_report_file.read()
        return report


def get_report_section(html_report, tag=None, component_id=None):
    """Get specific report section from InaSAFE analysis summary report.

    :param html_report: The html report.
    :type html_report: basestring

    :param tag: The HTML tag.
    :type tag: basestring

    :param component_id: The component key.
    :type component_id: str

    :return: Requested report section as an html.
    :rtype: basestring
    """
    no_specs_error = tr('No tag or component id given.')
    no_element_error = tr('No element match the tag or component id.')

    container_format = (
        '<div class="container">'
        '   {section_content}'
        '</div>'
    )

    beautiful_soup = BeautifulSoup(html_report)
    if tag:
        section_soup = beautiful_soup.find(tag)
    elif component_id:
        section_soup = beautiful_soup.find(tag, {'id': component_id})
    else:
        return no_specs_error

    if section_soup:
        report_section = container_format.format(
            section_content=unicode(section_soup))
        return unicode(report_section)
    else:
        return no_element_error


##
# For QGIS < 2.18.13 and QGIS < 2.14.19, docstrings are used in the QGIS GUI
# in the Expression dialog and also in the InaSAFE Help dialog.
#
# For QGIS >= 2.18.13, QGIS >= 2.14.19 and QGIS 3, the translated variable will
# be used in QGIS.
# help_text is used for QGIS 2.18 and 2.14
# helpText is used for QGIS 3 : https://github.com/qgis/QGIS/pull/5059
##

description = tr('Retrieve an HTML table report of current selected analysis.')
examples = {
    'analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_summary_report(feature, parent):
    """Retrieve an HTML table report of current selected analysis.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    return get_impact_report_as_string(analysis_dir)


description = tr('Retrieve default InaSAFE HTML resources (style and script) '
                 'from InaSAFE analysis report of current selected analysis.')
examples = {
    'inasafe_html_resources()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def default_inasafe_html_resources(feature, parent):
    """Retrieve default InaSAFE HTML resources (style and script).
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, tag='head')

    return requested_html_report


description = tr('Retrieve the analysis question section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'analysis_question_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_question_report(feature, parent):
    """Retrieve the analysis question section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=analysis_question_component['key'])

    return requested_html_report


description = tr('Retrieve the general report section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'general_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def general_report(feature, parent):
    """Retrieve the general report section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=general_report_component['key'])

    return requested_html_report


description = tr('Retrieve the mmi detail section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'mmi_detail_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def mmi_detail_report(feature, parent):
    """Retrieve the mmi detail section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=mmi_detail_component['key'])

    return requested_html_report


description = tr('Retrieve the analysis detail section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'analysis_detail_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_detail_report(feature, parent):
    """Retrieve the analysis detail section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=analysis_detail_component['key'])

    return requested_html_report


description = tr('Retrieve the action checklist section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'action_checklist_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def action_checklist_report(feature, parent):
    """Retrieve the action checklist section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=action_checklist_component['key'])

    return requested_html_report


description = tr('Retrieve the notes assumptions section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'notes_assumptions_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def notes_assumptions_report(feature, parent):
    """Retrieve the notes assumptions section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=notes_assumptions_component['key'])

    return requested_html_report


description = tr('Retrieve the minimum needs section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'minimum_needs_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def minimum_needs_report(feature, parent):
    """Retrieve the minimum needs section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=minimum_needs_component['key'])

    return requested_html_report


description = tr('Retrieve the aggregation result section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'aggregation_result_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def aggregation_result_report(feature, parent):
    """Retrieve the aggregation result section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report, component_id=aggregation_result_component['key'])

    return requested_html_report


description = tr('Retrieve the aggregation postprocessors section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'aggregation_postprocessors_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def aggregation_postprocessors_report(feature, parent):
    """Retrieve the aggregation postprocessors section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report,
        component_id=aggregation_postprocessors_component['key'])

    return requested_html_report


description = tr('Retrieve the analysis provenance details section from '
                 'InaSAFE analysis report of current selected analysis.')
examples = {
    'analysis_provenance_details_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_provenance_details_report(feature, parent):
    """Retrieve the analysis provenance details section from InaSAFE report.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    complete_html_report = get_impact_report_as_string(analysis_dir)

    requested_html_report = get_report_section(
        complete_html_report,
        component_id=analysis_provenance_details_simplified_component['key'])

    return requested_html_report


description = tr('Retrieve an HTML population analysis table report from '
                 'a multi exposure analysis.')
examples = {
    'population_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def population_analysis_summary_report(feature, parent):
    """Retrieve an HTML population analysis table report from a multi exposure
    analysis.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir(exposure_population['key'])
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None


description = tr('Retrieve an HTML road analysis table report from '
                 'a multi exposure analysis.')
examples = {
    'road_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def road_analysis_summary_report(feature, parent):
    """Retrieve an HTML road analysis table report from a multi exposure
    analysis.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir(exposure_road['key'])
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None


description = tr('Retrieve an HTML structure analysis table report from '
                 'a multi exposure analysis.')
examples = {
    'structure_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def structure_analysis_summary_report(feature, parent):
    """Retrieve an HTML structure analysis table report from a multi exposure
    analysis.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir(exposure_structure['key'])
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None


description = tr('Retrieve an HTML place analysis table report from '
                 'a multi exposure analysis.')
examples = {
    'place_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def place_analysis_summary_report(feature, parent):
    """Retrieve an HTML place analysis table report from a multi exposure
    analysis.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir(exposure_place['key'])
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None


description = tr('Retrieve an HTML land cover analysis table report from '
                 'a multi exposure analysis.')
examples = {
    'land_cover_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def land_cover_analysis_summary_report(feature, parent):
    """Retrieve an HTML land cover analysis table report from a multi exposure
    analysis.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir(exposure_land_cover['key'])
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None


description = tr('Retrieve an HTML multi exposure analysis table report.')
examples = {
    'multi_exposure_analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def multi_exposure_analysis_summary_report(feature, parent):
    """Retrieve an HTML multi exposure analysis table report.
    """
    _ = feature, parent  # NOQA
    analysis_dir = get_analysis_dir()
    if analysis_dir:
        return get_impact_report_as_string(analysis_dir)
    return None
