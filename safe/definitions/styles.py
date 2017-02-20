# coding=utf-8
"""Styles and colors which are used in InaSAFE."""

from PyQt4.QtGui import QColor

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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
MMI_white = QColor ('#ffffff')
MMI_blue = QColor ('#209fff')
MMI_light_blue = QColor ('#00cfff')
MMI_cyan = QColor ('#55ffff')
MMI_light_cyan = QColor ('#aaffff')
MMI_yellow = QColor ('#fff000')
MMI_light_orange = QColor ('#ffa800')
MMI_orange = QColor('#ff7000')
MMI_red = QColor ('#ff0000')
MMI_dark_red = QColor ('#dd0000')
MMI_brown = QColor('#880000')
MMI_dark_brown = QColor('#440000')

# Map legend templates according to standards :
# https://github.com/inasafe/inasafe/issues/3653#issuecomment-275011957
# The space between count and exposure_unit will be automatically added if
# the unit is not empty.
template_without_thresholds = u'{name} ({count}{exposure_unit})'
template_with_maximum_thresholds = (
    u'{name} <= {max} {hazard_unit} ({count}{exposure_unit})')
template_with_minimum_thresholds = (
    u'{name} > {min} {hazard_unit} ({count}{exposure_unit})')
template_with_range_thresholds = (
    u'{name} > {min} - {max} {hazard_unit} ({count}{exposure_unit})')

# Default line width for exposure
line_width_exposure = 0.66

# Rubber bands
user_analysis_color = QColor(0, 0, 255, 100)
user_analysis_width = 2

next_analysis_color = QColor(0, 255, 0, 100)
next_analysis_width = 10

last_analysis_color = QColor(255, 0, 0, 100)
last_analysis_width = 5

# Availability options color in wizard
available_option_color = QColor(120, 255, 120)
unavailable_option_color = QColor(220, 220, 220)
