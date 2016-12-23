# coding=utf-8

"""Colors which are used in InaSAFE."""

from PyQt4.QtGui import QColor

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Hazard classes as specified in reporting standards :
# https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044

green = QColor('#1A9641')
light_green = QColor('#A6D96A')
yellow = QColor('#FFFFB2')
orange = QColor('#FEB24C')
red = QColor('#F03B20')
dark_red = QColor('#BD0026')

# Default color for no hazard
no_hazard = QColor('#000000')

# Rubber bands
user_analysis_color = QColor(0, 0, 255, 100)
user_analysis_width = 2

next_analysis_color = QColor(0, 255, 0, 100)
next_analysis_width = 10

last_analysis_color = QColor(255, 0, 0, 100)
last_analysis_width = 5
