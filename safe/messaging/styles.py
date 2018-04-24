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
from future import standard_library
standard_library.install_aliases()
import os
import urllib.request
import urllib.parse
import urllib.error
import urllib.parse

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import

from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# Used for section headers in definitions_help.py
TITLE_LEVEL_1_STYLE = {
    'level': 1,
    'style_class': 'title'}

SECTION_LEVEL_2_STYLE = {
    'level': 2,
    'style_class': 'section'}

SUBSECTION_LEVEL_3_STYLE = {
    'level': 3,
    'style_class': 'subsection'}

HEADING_LEVEL_4_STYLE = {
    'level': 4,
    'style_class': 'subsection'}

BLUE_LEVEL_4_STYLE = {
    'level': 4,
    'icon': 'icon-info-sign icon-white',
    'style_class': 'info'}
RED_LEVEL_4_STYLE = {
    'level': 4,
    'icon': 'icon-warning-sign icon-white',
    'style_class': 'warning'}

GREEN_LEVEL_4_STYLE = {
    'level': 4,
    'icon': 'icon-comment icon-white',
    'style_class': 'suggestion'}

ORANGE_LEVEL_4_STYLE = {
    'level': 4,
    'icon': 'icon-remove-sign icon-white',
    'style_class': 'warning'}

ORANGE_LEVEL_5_STYLE = {
    'level': 5,
    'icon': 'icon-list icon-white',
    'style_class': 'problem'}

GREY_LEVEL_6_STYLE = {
    'level': 6,
    'icon': 'icon-list icon-white',
    'style_class': 'details-subgroup'}

PROGRESS_UPDATE_STYLE = {
    'level': 4,
    'icon': 'icon-cog icon-white',
    'style_class': 'info'}

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

    :returns: A sanitised local url to the logo prefixed with file://.
    :rtype: str

    ..note:: We are not using QUrl here because on Windows 10 it returns
        an empty path if using QUrl.toLocalPath
    """

    path = os.path.join(resources_path(), 'img', 'logos', 'inasafe-logo.png')
    url = urllib.parse.urljoin('file:', urllib.request.pathname2url(path))
    return url
