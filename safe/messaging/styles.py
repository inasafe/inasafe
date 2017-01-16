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
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '06/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QUrl
# These all apply to heading elements

from safe.utilities.resources import resources_path


# Used for section headers in definitions_help.py
TITLE_STYLE = {
    'level': 1,
    'style_class': 'title'}

SECTION_STYLE = {
    'level': 2,
    'style_class': 'section'}

SUBSECTION_STYLE = {
    'level': 3,
    'style_class': 'subsection'}

INFO_STYLE = {
    'level': 4,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'info'}

HEADING_STYLE = {
    'level': 4,
    'style_class': 'subsection'}

PROGRESS_UPDATE_STYLE = {
    'level': 4,
    'icon': 'icon-cog icon-white',
    'style_class': 'info'}


SUB_INFO_STYLE = {
    'level': 5,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'sub_info'}

WARNING_STYLE = {
    'level': 4,
    'icon': 'icon-warning-sign icon-white',
    'style_class': 'warning'}

SUGGESTION_STYLE = {
    'level': 4,
    'icon': 'icon-comment icon-white',
    'style_class': 'suggestion'}

PROBLEM_STYLE = {
    'level': 4,
    'icon': 'icon-remove-sign icon-white',
    'style_class': 'warning'}

DETAILS_STYLE = {
    'level': 4,
    'icon': 'icon-list icon-white',
    'style_class': 'problem'}

SMALL_ICON_STYLE = {
    'attributes': 'style="width: 24px; height: 24px;"',
}

MEDIUM_ICON_STYLE = {
    'attributes': 'style="width: 96px; height: 96px;"',
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
    # 'style_class': 'label label-success'
}


def logo_element():
    """Create a sanitised local url to the logo for insertion into html.

    :returns: A sanitised local url to the logo.
    :rtype: str
    """
    path = os.path.join(resources_path(), 'img', 'logos', 'inasafe-logo.png')
    url = QUrl(path)
    path = url.toLocalFile()
    return path
