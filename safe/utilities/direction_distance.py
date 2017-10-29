# coding=utf-8

"""Direction and Distance Functionality."""

import logging
import math
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsDistanceArea,
    QgsField,
    QgsRasterLayer,
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


def get_direction_distance(
        hazard_point,
        places_layer,
        name,
        population=None
):
    """Calculate distance and bearing angle.

    :param hazard_point: A point indicating hazard location
    :type hazard_point: QgsPoint
    :param places_layer: Vector Layer containing place information
    :type places_layer: QgsVectorLayer
    :param name: Field that contains the place name
    :type name: str
    :param population: Field that contains the place name
    :type population: str
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
    # create new fields to store the calculation result
    output_provider.addAttributes([
        QgsField('distance', QVariant.Double),
        QgsField('bearing_to', QVariant.Double),
        QgsField('dir_to', QVariant.String),
        QgsField('bearing_fr', QVariant.Double),
        QgsField('dir_from', QVariant.String),
        QgsField('mmi', QVariant.Double)
    ])
    output_layer.updateFields()
    # get field index
    distance_index =  output_provider.fields().indexFromName('distance')
    bearing_to_index =  output_provider.fields().indexFromName('bearing_to')
    dir_to_index =  output_provider.fields().indexFromName('dir_to')
    bearing_fr_index =  output_provider.fields().indexFromName('bearing_fr')
    dir_from_index =  output_provider.fields().indexFromName('dir_from')
    # start calculating distance and get cardinality
    output_layer.startEditing()
    for feature in output_layer.getFeatures():
        fid = feature.id()
        city_name = feature[fields.indexFromName(name)]
        # get latitude and longitude
        city_x = feature.geometry().asPoint().x()
        city_y = feature.geometry().asPoint().y()
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
        # store the value to attribute table
        output_layer.changeAttributeValue(fid, distance_index, distance)
        output_layer.changeAttributeValue(fid, bearing_to_index, bearing_to)
        output_layer.changeAttributeValue(fid, dir_to_index, direction_to)
        output_layer.changeAttributeValue(fid, bearing_fr_index, bearing_from)
        output_layer.changeAttributeValue(fid, dir_from_index, direction_from)
    output_layer.commitChanges()

        # store information in a dictionary
        # city = {
        #     'latitude': city_y,
        #     'longitude': city_x,
        #     'name': city_name,
        #     'population': population_number,
        #     'distance': distance,
        #     'bearing_to': bearing_to,
        #     'direction_to': direction_to,
        #     'bearing_from': bearing_from,
        #     'direction_from': direction_from
        # }
        # cities.append(city)
    # sort cities by distance and population
    # sorted_cities = sorted(
    #     cities,
    #     key=lambda d: (
    #         d['distance'],
    #         -d['population']
    #     )
    # )
    return output_layer


def mmi_sampling(place_layer, shake_tiff_path):
    """Get MMI information from ShakeMap Tiff on place location.

    Get the MMI value on each cities/places from the generated tiff files.
    :param place_layer: List of place dictionaries
    :type place_layer: list
    :param shake_tiff_path: Path to shake tiff files
    :type shake_tiff_path: Path
    :return: List containing places dictionaries with mmi values
    :rtype: list
    """

    shake_layer = QgsRasterLayer(shake_tiff_path, 'Shake Layer')
    shake_provider = shake_layer.dataProvider()
    for place in place_layer:
        x_coord = place['longitude']
        y_coord = place['latitude']


