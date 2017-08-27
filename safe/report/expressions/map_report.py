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
    white_inasafe_logo_path,
    north_arrow_path,
    organisation_logo_path,
    crs_text)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

image_group = tr('InaSAFE - Image Elements')
label_group = tr('InaSAFE - Label Elements')


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def legend_title_header_element(feature, parent):
    """Retrieve legend title header string from definitions."""
    _ = feature, parent  # NOQA
    header = legend_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def disclaimer_title_header_element(feature, parent):
    """Retrieve disclaimer title header string from definitions."""
    _ = feature, parent  # NOQA
    header = disclaimer_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def disclaimer_text_element(feature, parent):
    """Retrieve disclaimer text string from definitions."""
    _ = feature, parent  # NOQA
    text = disclaimer_text['string_format']
    return text


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def information_title_header_element(feature, parent):
    """Retrieve information title header string from definitions."""
    _ = feature, parent  # NOQA
    header = information_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def time_title_header_element(feature, parent):
    """Retrieve time title header string from definitions."""
    _ = feature, parent  # NOQA
    header = time_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def caution_title_header_element(feature, parent):
    """Retrieve caution title header string from definitions."""
    _ = feature, parent  # NOQA
    header = caution_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def caution_text_element(feature, parent):
    """Retrieve caution text string from definitions."""
    _ = feature, parent  # NOQA
    text = caution_text['string_format']
    return text


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def source_title_header_element(feature, parent):
    """Retrieve source title header string from definitions."""
    _ = feature, parent  # NOQA
    header = source_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def analysis_title_header_element(feature, parent):
    """Retrieve analysis title header string from definitions."""
    _ = feature, parent  # NOQA
    header = analysis_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def version_title_header_element(feature, parent):
    """Retrieve version title header string from definitions."""
    _ = feature, parent  # NOQA
    header = version_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def reference_title_header_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = reference_title_header['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def crs_text_element(crs, feature, parent):
    """Retrieve coordinate reference system text string from definitions.
    
    Example usage: crs_text_element(3857).
    """
    _ = feature, parent  # NOQA
    crs = QgsCoordinateReferenceSystem().createFromId(crs)
    crs = crs.description()
    text = crs_text['string_format'].format(crs=crs)
    return text


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def unknown_source_text_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = unknown_source_text['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=label_group, usesGeometry=False, referencedColumns=[])
def aggregation_not_used_text_element(feature, parent):
    """Retrieve reference title header string from definitions."""
    _ = feature, parent  # NOQA
    header = aggregation_not_used_text['string_format']
    return header.capitalize()


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[])
def inasafe_logo_white_path(feature, parent):
    """Retrieve the full path of inasafe-logo-white.svg."""
    _ = feature, parent  # NOQA
    return white_inasafe_logo_path['path']


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[])
def north_arrow_path(feature, parent):
    """Retrieve the full path of default north arrow logo."""
    _ = feature, parent  # NOQA
    return north_arrow_path['path']


@qgsfunction(
    args='auto', group=image_group, usesGeometry=False, referencedColumns=[])
def organisation_logo_path(feature, parent):
    """Retrieve the full path of inasafe-logo-white.svg."""
    _ = feature, parent  # NOQA
    return organisation_logo_path['path']
