# coding=utf-8

"""Direction and Distance Functionality."""

import logging
import math
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsDistanceArea,
    QgsField,
    QGis
)
from safe.gis.vector.tools import create_memory_layer

LOGGER = logging.getLogger('InaSAFE')


def bearing_to_cardinal(angle):
    """Get cardinality of an angle.

    :param angle: Bearing angle
    :type angle: angle in degrees

    :return: cardinality of input angle
    :rtype: string
    """

    # this method could still be improved later, since the acquisition interval
    # is a bit strange, i.e the input angle of 22.499° will return `N` even
    # though 22.5° is the direction for `NNE`
    direction_list = [
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
        'SSE', 'S', 'SSW', 'SW', 'WSW', 'W',
        'WNW', 'NW', 'NNW'
    ]

    bearing = float(angle)
    direction_count = len(direction_list)
    direction_interval = 360. / direction_count
    index = int(math.floor(bearing / direction_interval))
    index %= direction_count
    return direction_list[index]


def get_direction_distance(hazard_point, places_layer):
    """Calculate distance and bearing angle.

    :param hazard_point: A point indicating hazard location
    :type hazard_point: QgsPoint

    :param places_layer: Vector Layer containing place information
    :type places_layer: QgsVectorLayer

    :return: memory layer of city with direction and distance value
    :rtype: QgsVectorLayer
    """
    # define distance
    find_distance = QgsDistanceArea()
    find_distance.setEllipsoidalMode(True)
    find_distance.setEllipsoid('WGS84')

    fields = places_layer.dataProvider().fields()

    # memory layer to save new place layer
    output_layer = create_memory_layer(
        'Nearby Places', QGis.Point, places_layer.crs(), fields
    )
    output_provider = output_layer.dataProvider()
    # get features from place layer and add it to the memory layer
    feature_list = []
    for feature in places_layer.getFeatures():
        feature_list.append(feature)
    output_provider.addFeatures(feature_list)
    # define new field name
    distance_field = 'distance'
    bearing_to_field = 'bearing_to'
    bearing_from_field = 'bearing_fr'
    direction_to_field = 'dir_to'
    direction_from_field = 'dir_from'
    mmi_field = 'mmi'
    # create new fields to store the calculation result
    output_provider.addAttributes([
        QgsField(distance_field, QVariant.Double),
        QgsField(bearing_to_field, QVariant.Double),
        QgsField(direction_to_field, QVariant.String),
        QgsField(bearing_from_field, QVariant.Double),
        QgsField(direction_from_field, QVariant.String),
        QgsField(mmi_field, QVariant.Double)
    ])
    output_layer.updateFields()
    # get field index
    output_fields = output_provider.fields()
    distance_index = output_fields.indexFromName(distance_field)
    bearing_to_index = output_fields.indexFromName(bearing_to_field)
    dir_to_index = output_fields.indexFromName(direction_to_field)
    bearing_fr_index = output_fields.indexFromName(bearing_from_field)
    dir_from_index = output_fields.indexFromName(direction_from_field)
    # start calculating distance and get cardinality
    output_layer.startEditing()
    for feature in output_layer.getFeatures():
        fid = feature.id()
        city_point = feature.geometry().asPoint()
        # get distance
        distance = find_distance.measureLine(hazard_point, city_point)
        # hazard angle
        bearing_to = hazard_point.azimuth(city_point)
        bearing_from = city_point.azimuth(hazard_point)
        # get direction of the bearing angle
        direction_to = bearing_to_cardinal(bearing_to)
        direction_from = bearing_to_cardinal(bearing_from)
        # store the value to attribute table
        output_layer.changeAttributeValue(fid, distance_index, distance)
        output_layer.changeAttributeValue(fid, bearing_to_index, bearing_to)
        output_layer.changeAttributeValue(fid, dir_to_index, direction_to)
        output_layer.changeAttributeValue(fid, bearing_fr_index, bearing_from)
        output_layer.changeAttributeValue(fid, dir_from_index, direction_from)
    output_layer.commitChanges()
    return output_layer
