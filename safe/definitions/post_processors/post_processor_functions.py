# coding=utf-8
# noinspection PyUnresolvedReferences
from PyQt4.QtCore import QPyNullVariant
from safe.definitions.hazard_classifications import (
    not_exposed_class,
    hazard_classes_all)

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


# This postprocessor function is also used in the aggregation_summary
def post_processor_affected_function(**kwargs):
    """Private function used in the affected postprocessor.

    The following are expected in kwargs:

    * classification: The hazard classification to use.
    * hazard_class: The hazard class to check.

    :return: If this hazard class is affected or not. It can be `not exposed`.
    :rtype: bool
    """
    classification = None
    for hazard in hazard_classes_all:
        if hazard['key'] == kwargs['classification']:
            classification = hazard['classes']
            break

    for level in classification:
        if level['key'] == kwargs['hazard_class']:
            affected = level['affected']
            break
    else:
        affected = not_exposed_class['key']

    return affected


def post_processor_population_displacement_function(
        classification=None, hazard_class=None, population=None):
    """Private function used in the displacement postprocessor.

    :param classification: The hazard classification to use.
    :type classification: dict

    :param hazard_class: The hazard class of the feature.
    :type hazard_class: str

    :param population: We don't use this value here. It's only used for
        condition for the postprocessor to run.
    :type population: float, int

    :return: The displacement ratio for a given hazard class.
    :rtype: float
    """
    _ = population
    for hazard in hazard_classes_all:
        if hazard['key'] == classification:
            classification = hazard['classes']
            break

    for hazard_class_def in classification:
        if hazard_class_def['key'] == hazard_class:
            displaced_ratio = hazard_class_def.get('displacement_rate', 0)
            return displaced_ratio

    return 0


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
    _ = population
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
