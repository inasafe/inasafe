# coding=utf-8
from qgis.core import (
    QGis,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry)

from PyQt4.QtCore import QVariant

from safe.common.exceptions import WrongDataTypeException
from safe.gis.qgis_vector_tools import create_layer
from safe.storage.raster import Raster
from safe.storage.vector import Vector

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


def check_attribute_exist(layer, attribute):
    """Check an attribute is exists in the layer

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

def get_qgis_raster_layer(layer):
    """Get QgsRasterLayer if the layer param is a raster storage layer (
    old-style).
    :param layer: The layer to normalize
    :type layer: QgsMapLayer, Raster
    :return: QgsMapLayer returned
    :rtype: QgsRasterLayer
    """
    if isinstance(layer, Raster):
        return layer.get_layer()
    elif isinstance(layer, QgsRasterLayer):
        return layer
    else:
        return None


def split_by_polygon_class(
        target_layer,
        polygon_splitter,
        request=None,
        attribute=None):
    """Split the target layer using several polygons and categorizes it.
    Also assigns category values in the attribute

    :param target_layer: The target layer to be split and categorizes
    :type target_layer: QgsVectorLayer

    :param polygon_splitter: The dict of polygons to split the target_layer
    :type polygon_splitter: dict[QgsGeometry]

    :param request: possible QgsFeatureRequest to filter target_layer
    :type request: QgsFeatureRequest

    :return: A categorized vector layer
    :rtype: QgsVectorLayer
    """

    def _set_feature(geometry, feature_attributes):
        """
        Helper to create and set up feature
        """
        included_feature = QgsFeature()
        included_feature.setGeometry(geometry)
        included_feature.setAttributes(feature_attributes)
        return included_feature

    def _update_attr_list(attributes, index, value, add_attribute=False):
        """
        Helper for update list of attributes.
        """
        new_attributes = attributes[:]
        if add_attribute:
            new_attributes.append(value)
        else:
            new_attributes[index] = value
        return new_attributes

    # Create layer to store the splitted objects
    result_layer = create_layer(target_layer)
    result_provider = result_layer.dataProvider()
    fields = result_provider.fields()

    # If target_field does not exist, add it:
    new_field_added = False
    if not attribute:
        if fields.indexFromName(attribute) == -1:
            result_layer.startEditing()
            result_provider.addAttributes(
                [QgsField(attribute, QVariant.String)])
            new_field_added = True
            result_layer.commitChanges()

    target_field_index = None
    if not attribute:
        target_field_index = result_provider.fieldNameIndex(attribute)
        if target_field_index == -1:
            raise WrongDataTypeException(
                'Field not found for %s' % attribute)

    # Start split procedure
    result_layer.startEditing()
    for initial_feature in target_layer.getFeatures(request):
        initial_geom = initial_feature.geometry()
        attributes = initial_feature.attributes()
        geometry_type = initial_geom.type()

        if (geometry_type == QGis.WKBPolygon or geometry_type ==
                QGis.WKBMultiPolygon or geometry_type == QGis.WKBMultiPoint):
            # convert to centroid so each geom is counted only once for the
            # respective class
            initial_geom = initial_geom.centroid()

        for key, polygon in enumerate(polygon_splitter):
            if polygon.contains(initial_geom):
                if attribute:
                    new_attributes = _update_attr_list(
                        attributes,
                        target_field_index,
                        key,
                        add_attribute=new_field_added)
                else:
                    new_attributes = attributes
                feature = _set_feature(
                    initial_feature.geometry(), new_attributes)
                _ = result_layer.dataProvider().addFeatures([feature])

    result_layer.commitChanges()
    result_layer.updateExtents()

    return result_layer

def check_layer_constraint(metadata, hazard_layer_mode,
                           hazard_layer_geometries, exposure_layer_mode,
                           exposure_layer_geometries):
    """Check the layer constraint in metadata is relevant with the base class
    used

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
