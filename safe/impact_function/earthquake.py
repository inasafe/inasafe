# coding=utf-8

"""Earthquake functions."""

import logging

# noinspection PyUnresolvedReferences
from qgis.core import (
    QGis,
    QgsRasterLayer,
    QgsVectorLayer,
)

from safe.definitions.utilities import definition

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


def from_mmi_to_hazard_class(mmi_level, classification_key):
    """From a MMI level, it returns the hazard class given a classification.

    :param mmi_level: The MMI level.
    :type mmi_level: int

    :param classification_key: The earthquake classification key.
    :type classification_key: safe.definitions.hazard_classifications

    :return: The hazard class key
    :rtype: basestring
    """
    classes = definition(classification_key)['classes']
    for hazard_class in classes:
        minimum = hazard_class['numeric_default_min']
        maximum = hazard_class['numeric_default_max']
        if minimum < mmi_level <= maximum:
            return hazard_class['key']
    return None


def displacement_rate(mmi_level, classification_key):
    """From a MMI level, it gives the displacement rate given a classification.

    :param mmi_level: The MMI level.
    :type mmi_level: int

    :param classification_key: The earthquake classification key.
    :type classification_key: safe.definitions.hazard_classifications

    :return: The displacement rate.
    :rtype: float
    """
    classes = definition(classification_key)['classes']
    for hazard_class in classes:
        minimum = hazard_class['numeric_default_min']
        maximum = hazard_class['numeric_default_max']
        if minimum < mmi_level <= maximum:
            return hazard_class['displacement_rate']
    return 0.0


def fatality_rate(mmi_level, classification_key):
    """From a MMI level, it gives the fatality rate given a classification.

    :param mmi_level: The MMI level.
    :type mmi_level: int

    :param classification_key: The earthquake classification key.
    :type classification_key: safe.definitions.hazard_classifications

    :return: The fatality rate.
    :rtype: float
    """
    classes = definition(classification_key)['classes']
    for hazard_class in classes:
        minimum = hazard_class['numeric_default_min']
        maximum = hazard_class['numeric_default_max']
        if minimum < mmi_level <= maximum:
            return hazard_class['fatality_rate']
    return 0.0
