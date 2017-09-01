# coding=utf-8
"""This module contains constants that are used in definitions."""

from PyQt4.QtCore import QVariant
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

inasafe_keyword_version_key = 'keyword_version'
no_field = tr('No Field')
no_data_value = 200
zero_default_value = 0.0
big_number = 9999

# Whole Number in QVariant / Integer as in math
qvariant_whole_numbers = [
    QVariant.Int,
    QVariant.UInt,
    QVariant.LongLong,
    QVariant.ULongLong
]

# Number in QVariant
qvariant_numbers = qvariant_whole_numbers + [
    QVariant.Double,
]

# Extent selector
EXPOSURE = 'Exposure'
HAZARD_EXPOSURE = 'HazardExposure'
HAZARD_EXPOSURE_VIEW = 'HazardExposureView'
HAZARD_EXPOSURE_BOOKMARK = 'HazardExposureBookmark'
HAZARD_EXPOSURE_BOUNDINGBOX = 'HazardExposureBoundingBox'

# Impact function status
PREPARE_SUCCESS = 0
PREPARE_FAILED_BAD_INPUT = 1
PREPARE_FAILED_BAD_CODE = 2
PREPARE_FAILED_INSUFFICIENT_OVERLAP = 5

# If the hazard and the exposure overlap but not the requested extent.
PREPARE_FAILED_INSUFFICIENT_OVERLAP_REQUESTED_EXTENT = 7
PREPARE_FAILED_BAD_LAYER = 6

ANALYSIS_SUCCESS = 0
ANALYSIS_FAILED_BAD_INPUT = 3
ANALYSIS_FAILED_BAD_CODE = 4

# GLOBAL is to indicate that a setting is stored as a global default
GLOBAL = 'global'
# RECENT is to indicate that a setting is stored as a recent input from the
# user
RECENT = 'recent'

# Options keys in the field mapping
DO_NOT_REPORT = 'do not report'
CUSTOM_VALUE = 'custom value'
GLOBAL_DEFAULT = 'global default'
FIELDS = 'fields'

# Type in the field mapping
STATIC = 'static'
SINGLE_DYNAMIC = 'single dynamic'
MULTIPLE_DYNAMIC = 'multiple dynamic'
