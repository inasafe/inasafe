# coding=utf-8

from qgis.core import qgsfunction, QgsCoordinateReferenceSystem

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
from safe.utilities.i18n import tr
from safe.utilities.utilities import generate_expression_help
from safe.utilities.settings import setting

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
    'Retrieve the full path of default north arrow logo.')
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
    return setting(inasafe_north_arrow_path['setting_key'])


description = tr(
    'Retrieve the full path of used specified organisation logo.')
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
    return setting(inasafe_organisation_logo_path['setting_key'])
