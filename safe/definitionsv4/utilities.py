# coding=utf-8

"""Utilities module for helping definitions retrieval.
"""

from safe.definitionsv4 import layer_purposes

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def purposes_for_layer(layer_geometry_key):
    """Get purposes of a layer geometry id.

    :param layer_geometry_key: The geometry id
    :type layer_geometry_key: str

    :returns: List of suitable layer purpose.
    :rtype: list
    """
    return_value = []
    for layer_purpose in layer_purposes:
        layer_geometry_keys = [
            i['key'] for i in layer_purpose['layer_geometry']]
        if layer_geometry_key in layer_geometry_keys:
            return_value.append(layer_purpose['key'])

    return sorted(return_value)