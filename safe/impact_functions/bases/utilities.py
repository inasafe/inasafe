# coding=utf-8
from qgis.core import (
    QgsVectorLayer)

from safe.storage.vector import Vector

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


def check_attribute_exist(layer, attribute):
    """Check an attribute is exists in the layer.

    :param layer: A layer to check
    :type layer: QgsVectorLayer

    :param attribute: the attribute to check in the layer
    :type attribute: str, unicode

    :return: True if the attribute exists
    :rtype: bool
    """
    attribute_index = layer.dataProvider().fieldNameIndex(attribute)
    return attribute_index != -1


def get_qgis_vector_layer(layer):
    """Get QgsVectorLayer if the layer param is a vector storage layer (
    old-style).

    :param layer: The layer to normalize
    :type layer: QgsMapLayer, Vector
    :return: QgsMapLayer returned
    :rtype: QgsVectorLayer
    """
    if isinstance(layer, Vector):
        return layer.get_layer()
    elif isinstance(layer, QgsVectorLayer):
        return layer
    else:
        return None


def check_layer_constraint(metadata, hazard_layer_mode,
                           hazard_layer_geometries, exposure_layer_mode,
                           exposure_layer_geometries):
    """Check the layer constraint in metadata is relevant with the base class
    used.

    :param metadata: the metadata of the class
    :type metadata: ImpactFunctionMetadata

    :param hazard_layer_mode: the layer_mode of hazard layer
    :type hazard_layer_mode: dict

    :param hazard_layer_geometries: the layer_geometry allowed for hazard layer
    :type hazard_layer_geometries: list

    :param exposure_layer_mode: the layer_mode of exposure_layer
    :type exposure_layer_mode: dict

    :param exposure_layer_geometries: the layer_geometry allowed for
    exposure_layer
    :type exposure_layer_geometries: list

    :return: True if valid
    :rtype: bool
    """
    valid_keywords = metadata.valid_layer_keywords()
    hazard_keywords = valid_keywords['hazard_keywords']
    exposure_keywords = valid_keywords['exposure_keywords']
    valid = True
    if not hazard_keywords['layer_mode'] == hazard_layer_mode['key']:
        valid = False
    hazard_geometries = hazard_layer_geometries
    hazard_geometries = [k['key'] for k in hazard_geometries]
    geom_exist = False
    for key in hazard_geometries:
        if key in hazard_keywords['layer_geometry']:
            geom_exist = True
            break

    if not geom_exist:
        valid = False

    if not exposure_keywords['layer_mode'] == exposure_layer_mode['key']:
        valid = False
    exposure_geometries = exposure_layer_geometries
    exposure_geometries = [k['key'] for k in exposure_geometries]
    geom_exist = False
    for key in exposure_geometries:
        if key in exposure_keywords['layer_geometry']:
            geom_exist = True
            break

    if not geom_exist:
        valid = False

    return valid
