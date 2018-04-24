# coding=utf-8

"""QGIS Expressions which are available in the QGIS GUI interface."""

import os

from qgis.core import (
    qgsfunction,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsExpressionContextUtils,
)

from safe.common.custom_logging import LOGGER
from safe.definitions.default_settings import inasafe_default_settings
from safe.definitions.exposure import exposure_place
from safe.definitions.extra_keywords import extra_keyword_analysis_type
from safe.definitions.fields import (
    bearing_field,
    distance_field,
    direction_field,
    exposure_name_field,
)
from safe.definitions.keyword_properties import property_extra_keywords
from safe.definitions.provenance import (
    provenance_multi_exposure_summary_layers_id,
    provenance_multi_exposure_summary_layers,
    provenance_layer_exposure_summary_id,
    provenance_layer_exposure_summary,
    provenance_layer_analysis_impacted_id, provenance_layer_analysis_impacted)
from safe.definitions.reports.map_report import (
    legend_title_header,
    disclaimer_title_header,
    disclaimer_text,
    information_title_header,
    time_title_header,
    caution_title_header,
    caution_text,
    source_title_header,
    analysis_title_header,
    version_title_header,
    reference_title_header,
    unknown_source_text,
    aggregation_not_used_text,
    black_inasafe_logo_path,
    white_inasafe_logo_path,
    inasafe_north_arrow_path,
    inasafe_organisation_logo_path,
    crs_text)
from safe.gis.tools import load_layer
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.settings import setting
from safe.utilities.utilities import generate_expression_help

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

image_group = tr('InaSAFE - Image Elements')
label_group = tr('InaSAFE - Label Elements')

##
# For QGIS < 2.18.13 and QGIS < 2.14.19, docstrings are used in the QGIS GUI
# in the Expression dialog and also in the InaSAFE Help dialog.
#
# For QGIS >= 2.18.13, QGIS >= 2.14.19 and QGIS 3, the translated variable will
# be used in QGIS.
# help_text is used for QGIS 2.18 and 2.14
# helpText is used for QGIS 3 : https://github.com/qgis/QGIS/pull/5059
##


description = tr('Retrieve legend title header string from definitions.')
examples = {
    'legend_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def legend_title_header_element(feature, parent):
    """Retrieve legend title header string from definitions."""
    _ = feature, parent  # NOQA
    header = legend_title_header['string_format']
    return header.capitalize()


def exposure_summary_layer():
    """Helper method for retrieving exposure summary layer.

    If the analysis is multi-exposure, then it will return the exposure
    summary layer from place exposure analysis.
    """
    project_context_scope = QgsExpressionContextUtils.projectScope()
    project = QgsProject.instance()

    key = provenance_layer_analysis_impacted_id['provenance_key']
    analysis_summary_layer = project.mapLayer(
        project_context_scope.variable(key))
    if not analysis_summary_layer:
        key = provenance_layer_analysis_impacted['provenance_key']
        if project_context_scope.hasVariable(key):
            analysis_summary_layer = load_layer(
                project_context_scope.variable(key))[0]

    if not analysis_summary_layer:
        return None

    keywords = KeywordIO.read_keywords(analysis_summary_layer)
    extra_keywords = keywords.get(property_extra_keywords['key'], {})
    is_multi_exposure = extra_keywords.get(extra_keyword_analysis_type['key'])

    key = provenance_layer_exposure_summary_id['provenance_key']
    if is_multi_exposure:
        key = ('{provenance}__{exposure}').format(
            provenance=provenance_multi_exposure_summary_layers_id[
                'provenance_key'],
            exposure=exposure_place['key'])
    if not project_context_scope.hasVariable(key):
        return None

    exposure_summary_layer = project.mapLayer(
        project_context_scope.variable(key))
    if not exposure_summary_layer:
        key = provenance_layer_exposure_summary['provenance_key']
        if is_multi_exposure:
            key = ('{provenance}__{exposure}').format(
                provenance=provenance_multi_exposure_summary_layers[
                    'provenance_key'],
                exposure=exposure_place['key'])
        if project_context_scope.hasVariable(key):
            exposure_summary_layer = load_layer(
                project_context_scope.variable(key))[0]
        else:
            return None

    return exposure_summary_layer


description = tr(
    'If the impact layer has a distance field, it will return the distance to '
    'the nearest place in metres.')
examples = {
    'distance_to_nearest_place()': '1234'
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def distance_to_nearest_place(feature, parent):
    """If the impact layer has a distance field, it will return the distance to
    the nearest place in metres.

    e.g. distance_to_nearest_place() -> 1234
    """
    _ = feature, parent  # NOQA

    layer = exposure_summary_layer()
    if not layer:
        return None

    index = layer.fields().lookupField()(
        distance_field['field_name'])
    if index < 0:
        return None

    feature = next(layer.getFeatures())
    return feature[index]


description = tr(
    'If the impact layer has a distance field, it will return the direction '
    'to the nearest place.')
examples = {
    'direction_to_nearest_place()': tr('NW')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def direction_to_nearest_place(feature, parent):
    """If the impact layer has a distance field, it will return the direction
    to the nearest place.

    e.g. direction_to_nearest_place() -> NW
    """
    _ = feature, parent  # NOQA

    layer = exposure_summary_layer()
    if not layer:
        return None

    index = layer.fields().lookupField()(
        direction_field['field_name'])
    if index < 0:
        return None

    feature = next(layer.getFeatures())
    return feature[index]


description = tr(
    'If the impact layer has a distance field, it will return the bearing '
    'to the nearest place in degrees.')
examples = {
    'bearing_to_nearest_place()': tr('280')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def bearing_to_nearest_place(feature, parent):
    """If the impact layer has a distance field, it will return the bearing
    to the nearest place in degrees.

    e.g. bearing_to_nearest_place() -> 280
    """
    _ = feature, parent  # NOQA

    layer = exposure_summary_layer()
    if not layer:
        return None

    index = layer.fields().lookupField()(
        bearing_field['field_name'])
    if index < 0:
        return None

    feature = next(layer.getFeatures())
    return feature[index]


description = tr(
    'If the impact layer has a distance field, it will return the name '
    'of the nearest place.')
examples = {
    'name_of_the_nearest_place()': tr('Tokyo')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def name_of_the_nearest_place(feature, parent):
    """If the impact layer has a distance field, it will return the name
    of the nearest place.

    e.g. name_of_the_nearest_place() -> Tokyo
    """
    _ = feature, parent  # NOQA

    layer = exposure_summary_layer()
    if not layer:
        return None

    index = layer.fields().lookupField()(
        exposure_name_field['field_name'])
    if index < 0:
        return None

    feature = next(layer.getFeatures())
    return feature[index]


description = tr(
    'Retrieve disclaimer title header string from definitions.')
examples = {
    'disclaimer_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def disclaimer_title_header_element(feature, parent):
    """Retrieve disclaimer title header string from definitions."""
    _ = feature, parent  # NOQA
    header = disclaimer_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve disclaimer text string from definitions.')
examples = {
    'disclaimer_text_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def disclaimer_text_element(feature, parent):
    """Retrieve disclaimer text string from definitions."""
    _ = feature, parent  # NOQA
    return setting(disclaimer_text['setting_key'])


description = tr(
    'Retrieve information title header string from definitions.')
examples = {
    'information_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def information_title_header_element(feature, parent):
    """Retrieve information title header string from definitions."""
    _ = feature, parent  # NOQA
    header = information_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve time title header string from definitions.')
examples = {
    'time_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def time_title_header_element(feature, parent):
    """Retrieve time title header string from definitions."""
    _ = feature, parent  # NOQA
    header = time_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve caution title header string from definitions.')
examples = {
    'caution_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def caution_title_header_element(feature, parent):
    """Retrieve caution title header string from definitions."""
    _ = feature, parent  # NOQA
    header = caution_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve caution text string from definitions.')
examples = {
    'caution_text_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def caution_text_element(feature, parent):
    """Retrieve caution text string from definitions."""
    _ = feature, parent  # NOQA
    text = caution_text['string_format']
    return text


description = tr(
    'Retrieve source title header string from definitions.')
examples = {
    'source_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def source_title_header_element(feature, parent):
    """Retrieve source title header string from definitions."""
    _ = feature, parent  # NOQA
    header = source_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve analysis title header string from definitions.')
examples = {
    'analysis_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_title_header_element(feature, parent):
    """Retrieve analysis title header string from definitions."""
    _ = feature, parent  # NOQA
    header = analysis_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve version title header string from definitions.')
examples = {
    'version_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def version_title_header_element(feature, parent):
    """Retrieve version title header string from definitions."""
    _ = feature, parent  # NOQA
    header = version_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve reference title header string from definitions.')
examples = {
    'reference_title_header_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def reference_title_header_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = reference_title_header['string_format']
    return header.capitalize()


description = tr(
    'Retrieve coordinate reference system text string from definitions.')
examples = {
    'crs_text_element(\'EPSG:3857\')': (
        'Coordinate Reference System - WGS 84 / Pseudo Mercator')
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def crs_text_element(crs, feature, parent):
    """Retrieve coordinate reference system text string from definitions.

    Example usage: crs_text_element('EPSG:3857').
    """
    _ = feature, parent  # NOQA
    crs_definition = QgsCoordinateReferenceSystem(crs)
    crs_description = crs_definition.description()
    text = crs_text['string_format'].format(crs=crs_description)
    return text


description = tr(
    'Retrieve reference title header string from definitions.')
examples = {
    'unknown_source_text_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def unknown_source_text_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = unknown_source_text['string_format']
    return header.capitalize()


description = tr(
    'Retrieve reference title header string from definitions.')
examples = {
    'aggregation_not_used_text_element()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def aggregation_not_used_text_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = aggregation_not_used_text['string_format']
    return header.capitalize()


description = tr(
    'Retrieve the full path of inasafe-logo-black.svg')
examples = {
    'inasafe_logo_black_path()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def inasafe_logo_black_path(feature, parent):
    """Retrieve the full path of inasafe-logo-black.svg."""
    _ = feature, parent  # NOQA
    return black_inasafe_logo_path['path']


description = tr(
    'Retrieve the full path of inasafe-logo-white.svg.')
examples = {
    'inasafe_logo_white_path()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def inasafe_logo_white_path(feature, parent):
    """Retrieve the full path of inasafe-logo-white.svg."""
    _ = feature, parent  # NOQA
    return white_inasafe_logo_path['path']


description = tr(
    'Retrieve the full path of user specified north arrow image. If the '
    'custom north arrow logo is not found, it will return the default north '
    'arrow image.')
examples = {
    'north_arrow_path()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def north_arrow_path(feature, parent):
    """Retrieve the full path of default north arrow logo."""
    _ = feature, parent  # NOQA

    north_arrow_file = setting(inasafe_north_arrow_path['setting_key'])
    if os.path.exists(north_arrow_file):
        return north_arrow_file
    else:
        LOGGER.info(
            'The custom north arrow is not found in {north_arrow_file}. '
            'Default north arrow will be used.').format(
            north_arrow_file=north_arrow_file)
        return inasafe_default_settings['north_arrow_path']


description = tr(
    'Retrieve the full path of user specified organisation logo. If the '
    'custom organisation logo is not found, it will return the default '
    'organisation logo.')
examples = {
    'organisation_logo_path()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def organisation_logo_path(feature, parent):
    """Retrieve the full path of used specified organisation logo."""
    _ = feature, parent  # NOQA
    organisation_logo_file = setting(
        inasafe_organisation_logo_path['setting_key'])
    if os.path.exists(organisation_logo_file):
        return organisation_logo_file
    else:
        LOGGER.info(
            'The custom organisation logo is not found in {logo_path}. '
            'Default organisation logo will be used.').format(
            logo_path=organisation_logo_file)
        return inasafe_default_settings['organisation_logo_path']
