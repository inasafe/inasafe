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
    direction_field,
    place_mmi_field
)
from safe.gis.vector.tools import (
    create_memory_layer,
    create_field_from_definition
)
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


def get_direction_distance(hazard_point, places_layer):
    """Calculate distance and bearing angle.

    :param hazard_point: A point indicating hazard location.
    :type hazard_point: QgsPoint

    :param places_layer: Vector Layer containing place information.
    :type places_layer: QgsVectorLayer

    :return: memory layer of city with direction and distance value.
    :rtype: QgsVectorLayer
    """
    # define distance
    find_distance = QgsDistanceArea()
    find_distance.setEllipsoidalMode(True)
    find_distance.setEllipsoid('WGS84')

    fields = places_layer.dataProvider().fields()

    # memory layer to save new place layer
    output_layer = create_memory_layer(
        tr('Nearby Places'), QGis.Point, places_layer.crs(), fields
    )
    output_provider = output_layer.dataProvider()
    # get features from place layer and add it to the memory layer
    feature_list = []
    for feature in places_layer.getFeatures():
        feature_list.append(feature)
    output_provider.addFeatures(feature_list)
    # create new fields to store the calculation result
    field_distance = create_field_from_definition(distance_field)
    field_bearing = create_field_from_definition(bearing_field)
    field_mmi = create_field_from_definition(place_mmi_field)
    field_direction = create_field_from_definition(direction_field)
    output_provider.addAttributes([
        field_distance,
        field_bearing,
        field_direction,
        field_mmi
    ])
    output_layer.updateFields()
    # get field index
    distance_index = output_layer.fields().indexFromName('distance')
    bearing_index = output_layer.fields().indexFromName('bearing')
    direction_index = output_layer.fields().indexFromName('direction')
    # place_mmi_index = output_layer.fields().indexFromName('place_mmi')
    # start calculating distance and get cardinality
    output_layer.startEditing()
    for feature in output_layer.getFeatures():
        fid = feature.id()
        city_point = feature.geometry().asPoint()
        # get distance
        distance = find_distance.measureLine(hazard_point, city_point)
        # hazard angle
        bearing = city_point.azimuth(hazard_point)
        # get direction of the bearing angle
        direction = bearing_to_cardinal(bearing)
        # store the value to attribute table
        output_layer.changeAttributeValue(fid, distance_index, distance)
        output_layer.changeAttributeValue(fid, bearing_index, bearing)
        output_layer.changeAttributeValue(fid, direction_index, direction)
    output_layer.commitChanges()
    LOGGER.info('Output Layer feature count = %d' %
                output_layer.featureCount())
    return output_layer
