# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@google.com>'
__revision__ = '$Format:%H$'
__date__ = '08/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from safe.postprocessors.abstract_building_road_type_postprocessor import \
    AbstractBuildingRoadTypePostprocessor
from safe.utilities.i18n import tr


class RoadTypePostprocessor(AbstractBuildingRoadTypePostprocessor):
    """
    Postprocessor that calculates road types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class.

        It takes care of defining self.impact_total
        """

        AbstractBuildingRoadTypePostprocessor.__init__(self)

    def description(self):
        """Describe briefly what the post processor does.
        """
        return tr('Calculates road types related statistics.')

    def _calculate_total(self):
        """Indicator that shows total temporarily closed roads.

        This indicator reports the temporarily closed roads in this region.

        :note: This is copy/paste from the building_type_postprocessor,
            except that the indicator counts the length of the road.
        """

        name = tr('Total affected')
        result = 0
        if self.type_fields is not None:
            try:
                for road in self.impact_attrs:
                    field_value = road[self.target_field]
                    if isinstance(field_value, basestring):
                        if field_value != 'Not Affected':
                            result += road['aggr_sum']
                    else:
                        if field_value:
                            # See issue #2258. Since we are only working with
                            # one road at a time we should only add 1.
                            result += road['aggr_sum']
                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(name, result)

    def _calculate_type(self, title, fields_values):
        """Indicator that shows total population.

        this indicator reports the road by type. the logic is:
        - look for the fields that occurs with a name included in
        self.valid_type_fields
        - look in those fields for any of the values of self.fields_values
        - if a record has one of the valid fields with one of the valid
        fields_values then it is considered affected

        :note: This is copy/paste from the building_type_postprocessor,
            except that indicator counts the length of the road.
        """

        title = tr(title)

        result = 0
        if self.type_fields is not None:
            try:
                for road in self.impact_attrs:
                    for type_field in self.type_fields:
                        road_type = road[type_field]
                        if road_type in fields_values:
                            field_value = road[self.target_field]
                            if isinstance(field_value, basestring):
                                if field_value != 'Not Affected':
                                    result += road['aggr_sum']
                            else:
                                if field_value:
                                    # See issue #2258. Since we are only
                                    # working with one road at a time we
                                    # should only add 1.
                                    result += road['aggr_sum']
                            break
                        elif self._is_unknown_type(road_type):
                            self._update_known_types(road_type)

                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(title, result)
