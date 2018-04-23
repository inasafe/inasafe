# coding=utf-8
"""Styles and colors which are used in InaSAFE."""

from qgis.PyQt.QtGui import QColor

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

transparent = QColor(0, 0, 0, 0)

# Hazard classes as specified in reporting standards :
# https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044
grey = QColor('#8C8C8C')  # Used for not exposed.
green = QColor('#1A9641')
light_green = QColor('#A6D96A')
yellow = QColor('#FFFFB2')
orange = QColor('#FEB24C')
red = QColor('#F03B20')
dark_red = QColor('#BD0026')
very_dark_red = QColor('#710017')

# Colors for each MMI levels.
MMI_1 = QColor('#ffffff')
MMI_2 = QColor('#209fff')
MMI_3 = QColor('#00cfff')
MMI_4 = QColor('#55ffff')
MMI_5 = QColor('#aaffff')
MMI_6 = QColor('#fff000')
MMI_7 = QColor('#ffa800')
MMI_8 = QColor('#ff7000')
MMI_9 = QColor('#ff0000')
MMI_10 = QColor('#dd0000')
MMI_11 = QColor('#880000')
MMI_12 = QColor('#440000')

# Colors used in reporting.
affected_column_background = QColor('#fff8e9')
charcoal_black = QColor('#36454F')

# Map legend templates according to standards :
# https://github.com/inasafe/inasafe/issues/3653#issuecomment-275011957
# The space between count and exposure_unit will be automatically added if
# the unit is not empty.
template_without_thresholds = '{name} ({count}{exposure_unit})'
template_with_maximum_thresholds = (
    '{name} <= {max} {hazard_unit} ({count}{exposure_unit})')
template_with_minimum_thresholds = (
    '{name} > {min} {hazard_unit} ({count}{exposure_unit})')
template_with_range_thresholds = (
    '{name} > {min} - {max} {hazard_unit} ({count}{exposure_unit})')

# Default line width for exposure
line_width_exposure = 0.66

# Rubber bands
user_analysis_color = QColor(0, 0, 255, 100)  # Blue
user_analysis_width = 2

next_analysis_color = QColor(0, 255, 0, 100)  # Green
next_analysis_width = 10

last_analysis_color = QColor(255, 0, 0, 100)  # Red
last_analysis_width = 5

# Availability options color in wizard
available_option_color = QColor(120, 255, 120)
unavailable_option_color = QColor(220, 220, 220)

# Aggregation layer
aggregation_width = '1.0'
aggregation_color = QColor(255, 125, 125)

# Analysis layer
analysis_width = '2.0'
analysis_color = QColor(255, 0, 0)
