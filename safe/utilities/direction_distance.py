# coding=utf-8

"""Direction and Distance Functionality."""

import logging
import math
from qgis.core import (
    QgsDistanceArea,
    QGis
)
from safe.definitions.fields import (
    distance_field,
    bearing_field,
    direction_field
)
from safe.gis.vector.tools import create_field_from_definition
from safe.utilities.i18n import tr

LOGGER = logging.getLogger('InaSAFE')


def bearing_to_cardinal(angle):
    """Get cardinality of an angle.

    :param angle: Bearing angle.
    :type angle: float

    :return: cardinality of input angle.
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


def get_distance(hazard_point, place_layer):
    """Calculate the direction of hazard from places layer.

    :param hazard_point: A point indicating hazard location.
    :type hazard_point: QgsPoint

    :param place_layer: Vector Layer containing place information.
    :type place_layer: QgsVectorLayer

    :return: place layer with additional field.
    :rtype: QgsVectorLayer
    """
    find_distance = QgsDistanceArea()
    find_distance.setEllipsoidalMode(True)
    find_distance.setEllipsoid('WGS84')

    place_provider = place_layer.dataProvider()
    field_distance = create_field_from_definition(distance_field)
    place_provider.addAttributes([field_distance])
    place_layer.updateFields()

    distance_index = place_layer.fields().indexFromName('distance')
    for feature in place_layer.getFeatures():
        fid = feature.id()
        city_point = feature.geometry().asPoint()
        distance = find_distance.measureLine(hazard_point, city_point)
        place_layer.changeAttributeValue(fid, distance_index, distance)
    place_layer.commitChanges()
    return place_layer


def get_direction(hazard_point, place_layer):
    """Calculate the direction of hazard from places layer.

    :param hazard_point: A point indicating hazard location.
    :type hazard_point: QgsPoint

    :param place_layer: Vector Layer containing place information.
    :type place_layer: QgsVectorLayer

    :return: place layer with additional field.
    :rtype: QgsVectorLayer
    """
    place_provider = place_layer.dataProvider()
    field_bearing = create_field_from_definition(bearing_field)
    field_direction = create_field_from_definition(direction_field)
    place_provider.addAttributes([
        field_bearing,
        field_direction
    ])
    place_layer.updateFields()

    bearing_index = place_layer.fields().indexFromName('bearing')
    direction_index = place_layer.fields().indexFromName('direction')
    for feature in place_layer.getFeatures():
        fid = feature.id()
        city_point = feature.geometry().asPoint()
        bearing = city_point.azimuth(hazard_point)
        direction = bearing_to_cardinal(bearing)
        place_layer.changeAttributeValue(fid, bearing_index, bearing)
        place_layer.changeAttributeValue(fid, direction_index, direction)
    place_layer.commitChanges()
    return place_layer
