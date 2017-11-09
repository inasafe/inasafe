# coding=utf-8

"""Python functions that we use in postprocessors."""

# noinspection PyUnresolvedReferences
from PyQt4.QtCore import QPyNullVariant

from qgis.core import QgsPoint
from safe.definitions.hazard_classifications import (
    hazard_classes_all, not_exposed_class)
from safe.definitions.exposure import exposure_population
from safe.definitions.utilities import get_displacement_rate, is_affected

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# # #
# Functions
#
# Note that the function names and docstrings will be shown in the
# definitions report, so keep them neat and tidy!
# # #


def multiply(**kwargs):
    """Simple postprocessor where we multiply the input values.

    :param kwargs: Dictionary of values to multiply
    :type kwargs: dict

    :return: The result.
    :rtype: float
    """
    result = 1
    for i in kwargs.values():
        if isinstance(i, QPyNullVariant) or not i:
            # If one value is null, we return null.
            return i
        result *= i
    return result


def size(size_calculator, geometry):
    """Simple postprocessor where we compute the size of a feature.

    :param geometry: The geometry.
    :type geometry: QgsGeometry

    :param size_calculator: The size calculator.
    :type size_calculator: safe.gis.vector.tools.SizeCalculator

    :return: The size.
    """
    feature_size = size_calculator.measure(geometry)
    return feature_size


def calculate_distance(
        distance_calculator,
        latitude,
        longitude,
        place_geometry):
    """Simple postprocessor where we compute the distance between two points.

    :param distance_calculator: The size calculator.
    :type distance_calculator: safe.gis.vector.tools.SizeCalculator

    :param latitude: The latitude to use.
    :type latitude: float

    :param longitude: The longitude to use.
    :type longitude: float

    :param place_geometry: Geometry of place.
    :type place_geometry: QgsGeometry

    :return: distance
    :rtype: float
    """
    epicenter = QgsPoint(longitude, latitude)
    place_point = place_geometry.asPoint()
    distance = distance_calculator.measure_distance(epicenter, place_point)
    return distance


def calculate_bearing(bearing_function, latitude, longitude, place_geometry):
    """Simple postprocessor where we compute the bearing angle between two
    points.

    :param bearing_function: The size calculator.
    :type bearing_function: safe.gis.vector.tools.measure_bearing

    :param latitude: The latitude to use.
    :type latitude: float

    :param longitude: The longitude to use.
    :type longitude: float

    :param place_geometry: Geometry of place.
    :type place_geometry: QgsGeometry

    :return: Bearing angle
    :rtype:
    """
    epicenter = QgsPoint(longitude, latitude)
    place_point = place_geometry.asPoint()
    bearing = bearing_function(epicenter, place_point)
    return bearing


def calculate_cardinality(cardinality_function, angle):
    """Simple postprocessor where we compute the distance between two points.

    :param cardinality_function: The cardinality function.
    :type cardinality_function: safe.gis.vector.tools.measure_cardinality

    :param angle: Bearing angle.
    :type angle: float

    :return: Cardinality text.
    :rtype: str
    """
    cardinality = cardinality_function(angle)
    return cardinality


# This postprocessor function is also used in the aggregation_summary
def post_processor_affected_function(
        exposure=None, hazard=None, classification=None, hazard_class=None):
    """Private function used in the affected postprocessor.

    :param exposure: The exposure to use.
    :type exposure: str

    :param hazard: The hazard to use.
    :type hazard: str

    :param classification: The hazard classification to use.
    :type classification: str

    :param hazard_class: The hazard class of the feature.
    :type hazard_class: str

    :return: If this hazard class is affected or not. It can be `not exposed`.
    :rtype: bool
    """
    if exposure == exposure_population['key']:
        affected = is_affected(
           hazard, classification, hazard_class)
    else:
        classes = None
        for hazard in hazard_classes_all:
            if hazard['key'] == classification:
                classes = hazard['classes']
                break

        for the_class in classes:
            if the_class['key'] == hazard_class:
                affected = the_class['affected']
                break
        else:
            affected = not_exposed_class['key']

    return affected


def post_processor_population_displacement_function(
        hazard=None, classification=None, hazard_class=None, population=None):
    """Private function used in the displacement postprocessor.

    :param hazard: The hazard to use.
    :type hazard: str

    :param classification: The hazard classification to use.
    :type classification: str

    :param hazard_class: The hazard class of the feature.
    :type hazard_class: str

    :param population: We don't use this value here. It's only used for
        condition for the postprocessor to run.
    :type population: float, int

    :return: The displacement ratio for a given hazard class.
    :rtype: float
    """
    _ = population  # NOQA

    return get_displacement_rate(hazard, classification, hazard_class)


def post_processor_population_fatality_function(
        classification=None, hazard_class=None, population=None):
    """Private function used in the fatality postprocessor.

    :param classification: The hazard classification to use.
    :type classification: str

    :param hazard_class: The hazard class of the feature.
    :type hazard_class: str

    :param population: We don't use this value here. It's only used for
        condition for the postprocessor to run.
    :type population: float, int

    :return: The displacement ratio for a given hazard class.
    :rtype: float
    """
    _ = population  # NOQA
    for hazard in hazard_classes_all:
        if hazard['key'] == classification:
            classification = hazard['classes']
            break

    for hazard_class_def in classification:
        if hazard_class_def['key'] == hazard_class:
            displaced_ratio = hazard_class_def.get('fatality_rate', 0.0)
            if displaced_ratio is None:
                displaced_ratio = 0.0
            # We need to cast it to float to make it works.
            return float(displaced_ratio)

    return 0.0
