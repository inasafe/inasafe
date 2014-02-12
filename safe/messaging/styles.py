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

# These all apply to heading elements

PROGRESS_UPDATE_STYLE = {
    'level': 5,
    'icon': 'icon-cog icon-white',
    'style_class': 'info'}

INFO_STYLE = {
    'level': 5,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'info'}

WARNING_STYLE = {
    'level': 5,
    'icon': 'icon-warning-sign icon-white',
    'style_class': 'warning'}

SUGGESTION_STYLE = {
    'level': 5,
    'icon': 'icon-comment icon-white',
    'style_class': 'suggestion'}

PROBLEM_STYLE = {
    'level': 5,
    'icon': 'icon-remove-sign icon-white',
    'style_class': 'warning'}

DETAILS_STYLE = {
    'level': 5,
    'icon': 'icon-list icon-white',
    'style_class': 'problem'}

SMALL_ICON_STYLE = {
    'attributes': 'style="width: 24px; height: 24px;"',
}

TRACEBACK_STYLE = {
    'level': 5,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'inverse',
    'attributes': 'onclick="toggleTracebacks();"'}

TRACEBACK_ITEMS_STYLE = {
    'style_class': 'traceback-detail',
}

# This is typically a text element or its derivatives
KEYWORD_STYLE = {
    # not working unless you turn css on and off again using inspector
    #'style_class': 'label label-success'
}
