# coding=utf-8
"""Wizard Utilities Functions."""


import logging
import os

from qgis.PyQt import QtCore
from qgis.core import QgsCoordinateTransform, QgsProject

import safe.gui.tools.wizard.wizard_strings
from safe.common.version import get_version
from safe.definitions.constants import RECENT, GLOBAL
from safe.definitions.layer_modes import layer_mode_classified
from safe.definitions.layer_purposes import (
    layer_geometry_line, layer_geometry_point, layer_geometry_polygon)
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.utilities.default_values import get_inasafe_default_value_qsetting
from safe.utilities.gis import (
    is_raster_layer, is_point_layer, is_polygon_layer)
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path
from safe.utilities.utilities import is_keyword_version_supported

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Data roles
RoleFunctions = QtCore.Qt.UserRole
RoleHazard = QtCore.Qt.UserRole + 1
RoleExposure = QtCore.Qt.UserRole + 2
RoleHazardConstraint = QtCore.Qt.UserRole + 3
RoleExposureConstraint = QtCore.Qt.UserRole + 4

LOGGER = logging.getLogger('InaSAFE')


not_set_image_path = resources_path(
    'img', 'wizard', 'keyword-subcategory-notset.svg')


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
            layer_a.crs(), layer_b.crs(), QgsProject.instance())
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

    if (keywords
            and keyword_version
            and is_keyword_version_supported(keyword_version)):
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

        description = """
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
        layer_version = keyword_version or tr('No Version')
        description = tr(
            'Your layer\'s keyword\'s version ({layer_version}) does not '
            'match with your InaSAFE version ({inasafe_version}). If you wish '
            'to use it as an exposure, hazard, or aggregation layer in an '
            'analysis, please update the keywords. Click Next if you want to '
            'assign keywords now.').format(
            layer_version=layer_version, inasafe_version=get_version())
    else:
        # The layer is keywordless
        if is_point_layer(layer):
            geom_type = layer_geometry_point['key']
        elif is_polygon_layer(layer):
            geom_type = layer_geometry_polygon['key']
        else:
            geom_type = layer_geometry_line['key']

        # hide password in the layer source
        source = layer.publicSource()
        description = """
            %s<br/><br/>
            <b>%s</b>: %s<br/>
            <b>%s</b>: %s<br/><br/>
            %s
        """ % (tr('This layer has no valid keywords assigned'),
               tr('SOURCE'), source,
               tr('TYPE'), is_raster_layer(layer)
               and 'raster'
               or 'vector (%s)' % geom_type,
               tr('In the next step you will be able'
                  + ' to assign keywords to this layer.'))
    return description


def get_inasafe_default_value_fields(qsetting, field_key):
    """Obtain default value for a field with default value.

    By default it will return label list and default value list
    label: [Setting, Do not report, Custom]
    values: [Value from setting, None, Value from QSetting (if exist)]

    :param qsetting: QSetting object
    :type qsetting: QSetting

    :param field_key: The field's key.
    :type field_key: str

    :returns: Tuple of list. List of labels and list of values.
    """
    labels = [tr('Global (%s)'), tr('Do not report'), tr('Custom')]
    values = [
        get_inasafe_default_value_qsetting(qsetting, GLOBAL, field_key),
        None,
        get_inasafe_default_value_qsetting(qsetting, RECENT, field_key)
    ]

    return labels, values


def clear_layout(layout):
    """Clear layout content.

    :param layout: A layout.
    :type layout: QLayout
    """
    # Different platform has different treatment
    # If InaSAFE running on Windows or Linux

    # Adapted from http://stackoverflow.com/a/9383780
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Remove the widget from layout
                widget.close()
                widget.deleteLater()
            else:
                clear_layout(item.layout())

            # Remove the item from layout
            layout.removeItem(item)
            del item  # shouldn't be needed, but just to be safe...


def skip_inasafe_field(layer, inasafe_fields):
    """Check if it possible to skip inasafe field step.

    The function will check if the layer has a specified field type.

    :param layer: A Qgis Vector Layer.
    :type layer: QgsVectorLayer

    :param inasafe_fields: List of non compulsory InaSAFE fields default.
    :type inasafe_fields: list

    :returns: True if there are no specified field type.
    :rtype: bool
    """
    # Iterate through all inasafe fields
    for inasafe_field in inasafe_fields:
        for field in layer.fields():
            # Check the field type
            if isinstance(inasafe_field['type'], list):
                if field.type() in inasafe_field['type']:
                    return False
            else:
                if field.type() == inasafe_field['type']:
                    return False
    return True


def get_image_path(definition):
    """Helper to get path of image from a definition in resource directory.

    :param definition: A definition (hazard, exposure).
    :type definition: dict

    :returns: The definition's image path.
    :rtype: str
    """
    path = resources_path(
        'img', 'wizard', 'keyword-subcategory-%s.svg' % definition['key'])
    if os.path.exists(path):
        return path
    else:
        return not_set_image_path
