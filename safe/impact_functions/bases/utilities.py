# coding=utf-8
from qgis.core import (
    QGis,
    QgsVectorLayer,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry)
from PyQt4.QtCore import QVariant
from safe.common.exceptions import WrongDataTypeException
from safe.gis.qgis_vector_tools import create_layer
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
    """ Get QgsVectorLayer if the layer param is a vector storage layer (
    old-style)
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