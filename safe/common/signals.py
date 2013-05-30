"""
InaSAFE Disaster risk assessment tool by AusAid - **Standard signal defs.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

These signals are defined for global use throughout the safe and InaSAFE
application. They provide context for when parts of the application want to
send messages to each other.

See: https://github.com/AIFDR/inasafe/issues/577 for more detailed explanation.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

DYNAMIC_MESSAGE_SIGNAL = 'DynamicMessage'
STATIC_MESSAGE_SIGNAL = 'StaticMessage'
ERROR_MESSAGE_SIGNAL = 'ErrorMessage'
