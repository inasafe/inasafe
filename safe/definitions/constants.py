# coding=utf-8
"""This module contains constants that are used in definitions."""

from PyQt4.QtCore import QVariant
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

small_number = 2 ** -53  # I think this is small enough
inasafe_keyword_version_key = 'keyword_version'
multipart_polygon_key = 'multipart_polygon'
no_field = tr('No Field')
no_data_value = 200
zero_default_value = 0.0

# Number in QVariant
qvariant_numbers = [
    QVariant.Int,
    QVariant.Double,
    QVariant.UInt,
    QVariant.LongLong,
    QVariant.ULongLong
]

# Whole Number in QVariant / Integer as in math
qvariant_whole_numbers = [
    QVariant.Int,
    QVariant.UInt,
    QVariant.LongLong,
    QVariant.ULongLong
]

# Extent selector
HAZARD_EXPOSURE = 'HazardExposure'
HAZARD_EXPOSURE_VIEW = 'HazardExposureView'
HAZARD_EXPOSURE_BOOKMARK = 'HazardExposureBookmark'
HAZARD_EXPOSURE_BOUNDINGBOX = 'HazardExposureBoundingBox'

# Impact function status
PREPARE_SUCCESS = 0
PREPARE_FAILED_BAD_INPUT = 1
PREPARE_FAILED_BAD_CODE = 2
PREPARE_FAILED_INSUFFICIENT_OVERLAP = 5
PREPARE_FAILED_BAD_LAYER = 6

ANALYSIS_SUCCESS = 0
ANALYSIS_FAILED_BAD_INPUT = 3
ANALYSIS_FAILED_BAD_CODE = 4

# GLOBAL is to indicate that a setting is stored as a global default
GLOBAL = 'global'
# RECENT is to indicate that a setting is stored as a recent input from the
# user
RECENT = 'recent'
