# coding=utf-8

"""Definitions relating to map report template elements."""

from safe.defaults import white_inasafe_logo_path, default_north_arrow_path, \
    supporters_logo_path
from safe.definitions.messages import disclaimer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


"""Label elements"""


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
    'string_format': disclaimer()
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

reference_text = {
    'id': 'reference-text',
    'string_format': tr('Geographic Coordinates - {crs}')
}

unknown_source_text = {
    'id': 'unknown-source-text',
    'string_format': tr('Unknown')
}

aggregation_not_used_text = {
    'id': 'aggregation-not-used-text',
    'string_format': tr('Not used')
}


"""Image elements"""


inasafe_logo_white = {
    'id': 'inasafe-logo-white',
    'path': white_inasafe_logo_path()
}

north_arrow_logo = {
    'id': 'north-arrow-logo',
    'path': default_north_arrow_path()
}

organisation_logo = {
    'id': 'organisation-logo',
    'path': supporters_logo_path()
}
