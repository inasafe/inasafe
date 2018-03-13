# coding=utf-8

"""Definitions relating to map report template elements."""

from safe.defaults import (
    black_inasafe_logo_path,
    white_inasafe_logo_path,
)
from safe.utilities.i18n import tr
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


"""Text elements."""


legend_title_header = {
    'id': 'legend-title',
    'string_format': tr('Legend')
}

disclaimer_title_header = {
    'id': 'disclaimer-title',
    'string_format': tr('Disclaimer')
}

disclaimer_text = {
    'id': 'disclaimer',
    'string_format': setting('reportDisclaimer'),
    'setting_key': 'reportDisclaimer'
}

information_title_header = {
    'id': 'information-title',
    'string_format': tr('Analysis Information')
}

time_title_header = {
    'id': 'time-title',
    'string_format': tr('Time')
}

caution_title_header = {
    'id': 'caution-title',
    'string_format': tr('Note')
}

caution_text = {
    'id': 'caution-text',
    'string_format': tr(
        'This assessment is a guide - we strongly recommend that '
        'you ground truth the results shown here before '
        'deploying resources and / or personnel.'
    )
}

source_title_header = {
    'id': 'source-title',
    'string_format': tr('Data Source')
}

analysis_title_header = {
    'id': 'analysis-title',
    'string_format': tr('Analysis Name')
}

version_title_header = {
    'id': 'version-title',
    'string_format': tr('Software')
}

reference_title_header = {
    'id': 'spatial-reference-title',
    'string_format': tr('Reference')
}

crs_text = {
    'id': 'reference-text',
    'string_format': tr('Coordinate Reference System - {crs}')
}

unknown_source_text = {
    'id': 'unknown-source-text',
    'string_format': tr('Unknown')
}

aggregation_not_used_text = {
    'id': 'aggregation-not-used-text',
    'string_format': tr('Not used')
}

text_variable_elements = [
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
    crs_text]

"""Image elements."""

white_inasafe_logo_path = {
    'id': 'inasafe-logo-white',
    'path': white_inasafe_logo_path()
}

black_inasafe_logo_path = {
    'id': 'inasafe-logo-black',
    'path': black_inasafe_logo_path()
}

inasafe_north_arrow_path = {
    'id': 'north-arrow-logo',
    'path': setting('north_arrow_path'),
    'setting_key': 'north_arrow_path'
}

inasafe_organisation_logo_path = {
    'id': 'organisation-logo',
    # We default to the supporters logo, but an org can change to their logo
    # in options ...
    'path': setting('organisation_logo_path'),
    'setting_key': 'organisation_logo_path'
}

image_variable_elements = [
    black_inasafe_logo_path,
    white_inasafe_logo_path,
    inasafe_north_arrow_path,
    inasafe_organisation_logo_path]

all_variable_elements = text_variable_elements + image_variable_elements
