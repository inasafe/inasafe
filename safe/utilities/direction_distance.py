# coding=utf-8

"""Direction and Distance Functionality."""

import logging
import math
from qgis.core import QgsDistanceArea

LOGGER = logging.getLogger('InaSAFE')


def bearing_to_cardinal(angle):
    """Get cardinality of an angle.

    :param angle: Bearing angle
    :type angle: angle in degrees
    :return: cardinality of input angle
    :rtype: string
    """
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


def get_direction_distance(hazard_point, places_layer, name, population=None):
    """Calculate distance and bearing angle.

    :param hazard_point: A point indicating hazard location
    :type hazard_point: QgsPoint
    :param places_layer: Vector Layer containing place information
    :type places_layer: QgsVectorLayer
    :param name: Field that contains the place name
    :type name: String
    :param population: Field that contains the place name
    :type population: String
    :return: list that contains dictionaries of city
    :rtype: list
    """
    # define distance
    find_distance = QgsDistanceArea()
    find_distance.setEllipsoidalMode(True)
    find_distance.setEllipsoid('WGS84')

    fields = places_layer.dataProvider().fields()
    # list to store cities information
    cities = []
    # start calculating distance and get cardinality
    for feature in places_layer.getFeatures():
        city_name = feature[fields.indexFromName(name)]
        if not population:
            # give zero value if there is no population fields given
            population_number = 0
        else:
            population_number = feature[fields.indexFromName(population)]
        city_point = feature.geometry().asPoint()
        # get distance
        distance = find_distance.measureLine(hazard_point, city_point)
        # hazard angle
        bearing_to = hazard_point.azimuth(city_point)
        bearing_from = city_point.azimuth(hazard_point)
        # get direction of the bearing angle
        direction_to = bearing_to_cardinal(bearing_to)
        direction_from = bearing_to_cardinal(bearing_from)
        # store information in a dictionary
        city = {
            'name': city_name,
            'population': population_number,
            'distance': distance,
            'bearing_to': bearing_to,
            'direction_to': direction_to,
            'bearing_from': bearing_from,
            'direction_from': direction_from
        }
        cities.append(city)
    # sort cities by distance and population
    sorted_cities = sorted(
        cities,
        key=lambda d: (
            d['distance'],
            -d['population']
        )
    )
    return sorted_cities
