# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.postprocessors.abstract_building_road_type_postprocessor import \
    AbstractBuildingRoadTypePostprocessor
from safe.definitions import place_class_mapping, place_class_order
from safe.utilities.i18n import tr

__author__ = 'Etienne Trimaille>'
__revision__ = '$Format:%H$'
__date__ = '21/07/2016'
__license__ = "GPL"
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')


class PlaceTypePostprocessor(AbstractBuildingRoadTypePostprocessor):
    """Postprocessor that calculates place types related statistics."""

    def __init__(self):
        """Constructor for postprocessor class."""
        AbstractBuildingRoadTypePostprocessor.__init__(self)
        self._description = tr('Calculates place types related statistics.')
        self._labels = {
            item['key']: item['name'] for item in place_class_mapping}
        self._order = place_class_order
        self.population_field = None

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        :param params: dict of parameters to pass to the post processor
        """
        super(PlaceTypePostprocessor, self).setup(params)
        if self.population_field is not None:
            self._raise_error('clear needs to be called before setup')

        self.population_field = params['population_field']

    def clear(self):
        """concrete implementation that ensures needed parameters are cleared.
        """
        super(PlaceTypePostprocessor, self).clear()
        self.population_field = None

    def feature_value(self, feature):
        """Return the value to add in the statistics.

        :param feature: The feature is not used.
        :type feature: QgsFeature

        :return: The value to add in the postprocessing.
        :rtype: float
        """
        if self.population_field:
            return feature[self.population_field]
        else:
            return 1
