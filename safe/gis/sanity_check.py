# coding=utf-8

"""Sanity check module."""

from qgis.core import QGis

from safe.common.exceptions import InvalidLayerError

from safe.utilities.gis import is_vector_layer, is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def check_inasafe_fields(layer):
    """Helper to check inasafe_fields.

    :param layer: The layer to check.
    :type layer: QgsVectorLayer

    :return: Return True if the layer is valid.
    :rtype: bool

    :raises: Exception with a message if the layer is not correct.
    """
    inasafe_fields = layer.keywords['inasafe_fields']

    real_fields = [field.name() for field in layer.fields().toList()]

    difference = set(inasafe_fields.values()).difference(real_fields)
    if len(difference):
        message = tr(
            'inasafe_fields has more fields than the layer %s itself : %s'
            % (layer.keywords['layer_purpose'], difference))
        raise InvalidLayerError(message)

    difference = set(real_fields).difference(inasafe_fields.values())
    if len(difference):
        message = tr(
            'The layer %s has more fields than inasafe_fields : %s'
            % (layer.title(), difference))
        raise InvalidLayerError(message)

    return True


def check_layer(layer, has_geometry=True):
    """Helper to check layer validity.

    This function wil; raise InvalidLayerError if the layer is invalid.

    :param layer: The layer to check.
    :type layer: QgsMapLayer

    :param has_geometry: If the layer must have a geometry. True by default.
        If it's a raster layer, we will no check this parameter.
    :type has_geometry: bool

    :raise: InvalidLayerError

    :return: Return True if the layer is valid.
    :rtype: bool
    """
    if is_vector_layer(layer) or is_raster_layer(layer):
        if not layer.isValid():
            raise InvalidLayerError(tr('The layer is invalid.'))

        if is_vector_layer(layer):

            if len(layer.dataProvider().subLayers()) > 1:
                raise InvalidLayerError(
                    tr('The layer should not have many sublayers.'))

            if layer.geometryType() == QGis.UnknownGeometry:
                raise InvalidLayerError(
                    tr('The layer has not a valid geometry type.'))

            if layer.hasGeometryType() != has_geometry:
                raise InvalidLayerError(
                    tr('The layer has not a correct geometry type.'))

    else:
        raise InvalidLayerError(
            tr('The layer is neither a raster nor a vector.'))

    return True
