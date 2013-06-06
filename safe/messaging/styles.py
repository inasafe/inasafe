"""
InaSAFE Disaster risk assessment tool developed by AusAid **Messaging styles.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

Style constants for use with messaging. Example usage::

    from messaging.styles import PROGRESS_UPDATE_STYLE
    m.ImportantText(myTitle, **PROGRESS_UPDATE_STYLE)

This will result in some standardised styling being applied to the important
text element.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '06/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

PROGRESS_UPDATE_STYLE = {
    'icon': 'icon-ok icon-white', 'style_class': 'label label-success'}
