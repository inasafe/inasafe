# coding=utf-8
"""This module contains constants that are used in definitions.
"""
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
