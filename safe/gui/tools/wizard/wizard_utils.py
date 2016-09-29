# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**Wizard Utilities.**

The module provides utilities function for InaSAFE Wizard dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '24/04/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import re

from PyQt4 import QtCore
from qgis.core import QgsCoordinateTransform

import safe.gui.tools.wizard.wizard_strings
from safe.definitionsv4.layer_purposes import layer_purpose_exposure
from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.hazard import layer_purpose_hazard
from safe.common.version import get_version
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer,
    is_polygon_layer)
from safe.utilities.i18n import tr
from safe.utilities.utilities import is_keyword_version_supported


# Data roles
RoleFunctions = QtCore.Qt.UserRole
RoleHazard = QtCore.Qt.UserRole + 1
RoleExposure = QtCore.Qt.UserRole + 2
RoleHazardConstraint = QtCore.Qt.UserRole + 3
RoleExposureConstraint = QtCore.Qt.UserRole + 4


def get_question_text(constant):
    """Find a constant by name and return its value.

    :param constant: The name of the constant to look for.
    :type constant: string

    :returns: The value of the constant or red error message.
    :rtype: string
    """
    if constant in dir(safe.gui.tools.wizard.wizard_strings):
        return getattr(safe.gui.tools.wizard.wizard_strings, constant)
    else:
        return '<b>MISSING CONSTANT: %s</b>' % constant


def layers_intersect(layer_a, layer_b):
    """Check if extents of two layers intersect.

    :param layer_a: One of the two layers to test overlapping
    :type layer_a: QgsMapLayer

    :param layer_b: The second of the two layers to test overlapping
    :type layer_b: QgsMapLayer

    :returns: true if the layers intersect, false if they are disjoint
    :rtype: boolean
    """
    extent_a = layer_a.extent()
    extent_b = layer_b.extent()
    if layer_a.crs() != layer_b.crs():
        coord_transform = QgsCoordinateTransform(
            layer_a.crs(), layer_b.crs())
        extent_b = (coord_transform.transform(
            extent_b, QgsCoordinateTransform.ReverseTransform))
    return extent_a.intersects(extent_b)


def layer_description_html(layer, keywords=None):
    """Form a html description of a given layer based on the layer
       parameters and keywords if provided

    :param layer: The layer to get the description
    :type layer: QgsMapLayer

    :param keywords: The layer keywords
    :type keywords: None, dict

    :returns: The html description in tabular format,
        ready to use in a label or tool tip.
    :rtype: str
    """

    if keywords and 'keyword_version' in keywords:
        keyword_version = str(keywords['keyword_version'])
    else:
        keyword_version = None

    if (keywords and
            keyword_version and
            is_keyword_version_supported(keyword_version)):
        # The layer has valid keywords
        purpose = keywords.get('layer_purpose')
        if purpose == layer_purpose_hazard['key']:
            subcategory = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                tr('Hazard'), keywords.get(purpose))
            unit = keywords.get('continuous_hazard_unit')
        elif purpose == layer_purpose_exposure['key']:
            subcategory = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                tr('Exposure'), keywords.get(purpose))
            unit = keywords.get('exposure_unit')
        else:
            subcategory = ''
            unit = None
        if keywords.get('layer_mode') == layer_mode_classified['key']:
            unit = tr('classified data')
        if unit:
            unit = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                tr('Unit'), unit)

        desc = """
            <table border="0" width="100%%">
            <tr><td><b>%s</b>: </td><td>%s</td></tr>
            <tr><td><b>%s</b>: </td><td>%s</td></tr>
            %s
            %s
            <tr><td><b>%s</b>: </td><td>%s</td></tr>
            </table>
        """ % (tr('Title'), keywords.get('title'),
               tr('Purpose'), keywords.get('layer_purpose'),
               subcategory,
               unit,
               tr('Source'), keywords.get('source'))
    elif keywords:
        # The layer has keywords, but the version is wrong
        desc = tr(
            'Your layer\'s keyword\'s version (%s) does not match with '
            'your InaSAFE version (%s). If you wish to use it as an '
            'exposure, hazard, or aggregation layer in an analysis, '
            'please update the keywords. Click Next if you want to assign '
            'keywords now.' % (keyword_version or 'No Version',
                               get_version()))
    else:
        # The layer is keywordless
        if is_point_layer(layer):
            geom_type = 'point'
        elif is_polygon_layer(layer):
            geom_type = 'polygon'
        else:
            geom_type = 'line'

        # hide password in the layer source
        source = re.sub(
            r'password=\'.*\'', r'password=*****', layer.source())

        desc = """
            %s<br/><br/>
            <b>%s</b>: %s<br/>
            <b>%s</b>: %s<br/><br/>
            %s
        """ % (tr('This layer has no valid keywords assigned'),
               tr('SOURCE'), source,
               tr('TYPE'), is_raster_layer(layer) and 'raster' or
               'vector (%s)' % geom_type,
               tr('In the next step you will be able' +
                  ' to assign keywords to this layer.'))
    return desc
