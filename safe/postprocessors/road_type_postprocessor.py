# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Dmitry Kolesov <kolesov.dm@google.com>'
__revision__ = '$Format:%H$'
__date__ = '08/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from collections import OrderedDict
from safe.postprocessors.building_type_postprocessor import \
    BuildingTypePostprocessor
from safe.utilities.i18n import tr


# The road postprocessing is the same workflow as Building postprocessing
# So we can redefine field values and call BuildingTypePostprocessor
# That is why I define RoadTypePostprocessor
# as descendant of BuildingTypePostprocessor
class RoadTypePostprocessor(BuildingTypePostprocessor):
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

        BuildingTypePostprocessor.__init__(self)
        # Note: Do we need these explicityl defined? With new osm-reporter
        # changes you already get a nicely named list in the 'type' field
        self.fields_values = OrderedDict([
            ('Motorway / highway', ['Motorway or highway']),
            ('Motorway link', ['Motorway link']),
            ('Primary road', ['Primary road']),
            ('Primary link', ['Primary link']),
            ('Tertiary', ['Tertiary']),
            ('Tertiary link', ['Tertiary link']),
            ('Secondary', ['Secondary']),
            ('Secondary link', ['Secondary link']),
            ('Road, residential, living street, etc.', [
                'Road, residential, living street, etc.']),
            ('Track', ['Track']),
            ('Cycleway, footpath, etc.', ['Cycleway, footpath, etc.']),
            ('Other', [])
        ])
        self.known_types = []
        self._update_known_types()

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
                        building_type = road[type_field]
                        if building_type in fields_values:
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
                        elif self._is_unknown_type(building_type):
                            self._update_known_types(building_type)

                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(title, result)
