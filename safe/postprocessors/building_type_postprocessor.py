# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from definitionsv4.definitions_v3 import structure_class_mapping, structure_class_order
from safe.postprocessors.abstract_building_road_type_postprocessor import \
    AbstractBuildingRoadTypePostprocessor
from safe.utilities.i18n import tr


class BuildingTypePostprocessor(AbstractBuildingRoadTypePostprocessor):
    """
    Postprocessor that calculates building types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractBuildingRoadTypePostprocessor.__init__(self)
        self._description = tr('Calculates building types related statistics.')
        self._labels = {
            item['key']: item['name'] for item in structure_class_mapping}
        self._order = structure_class_order

    @staticmethod
    def feature_value(feature):
        """ Return the value to add in the statistics. For a building, it's 1.

        :note: See issue #2258.
        :param feature: The feature is not used.

        :return: The value to add in the postprocessing.
        :rtype: int
        """
        return 1
