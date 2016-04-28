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

import itertools
from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor
from safe.utilities.i18n import tr


class AbstractBuildingRoadTypePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates building/roads types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)

        # Type of the post processor defined in child class.
        self.type = None

        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None
        self.no_features = None
        self.type_fields = None
        self.valid_type_fields = None
        self.value_mapping = None

        self.known_types = []

    def description(self):
        """
        Describe briefly what the post processor does.
        """
        raise NotImplementedError('Please don\'t use this class directly')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        :param params: dict of parameters to pass to the post processor
        """
        AbstractPostprocessor.setup(self, None)
        if (self.impact_total is not None or
                self.impact_attrs is not None or
                self.target_field is not None or
                self.valid_type_fields is not None or
                self.value_mapping is not None or
                self.type_fields is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']
        self.value_mapping = params['value_mapping']
        self.valid_type_fields = params['key_attribute']

        # find which attribute field has to be used
        self.type_fields = []
        try:
            for key in self.impact_attrs[0].iterkeys():
                if key.lower() in self.valid_type_fields:
                    self.type_fields.append(key)
        except IndexError:
            pass

        if len(self.type_fields) == 0:
            self.type_fields = None

        self.no_features = False
        # there are no features in this postprocessing polygon
        if len(self.impact_attrs):
            self.no_features = True

    def process(self):
        """Concrete implementation that performs all indicators calculations.
        """
        AbstractPostprocessor.process(self)

        if (self.impact_total is None or
                self.type is None or
                self.impact_attrs is None or
                self.value_mapping is None or
                self.target_field is None):
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_total()
            for title, field_values in self.value_mapping.iteritems():
                self._calculate_type(title, field_values)

    def _calculate_total(self):
        """Indicator that shows total temporarily closed roads."""

        name = tr('Temporarily closed')
        result = 0
        if self.type_fields is not None:
            try:
                for road in self.impact_attrs:
                    field_value = road[self.target_field]
                    if isinstance(field_value, basestring):
                        if field_value != 'Not Affected':
                            if self.type == 'RoadTypePostprocessor':
                                result += road['aggr_sum']
                            else:
                                # BuildingTypePostprocessor
                                # See issue #2258. Since we are only
                                # working with one road at a time we
                                # should only add 1.
                                result += 1
                    else:
                        if field_value:
                            if self.type == 'RoadTypePostprocessor':
                                result += road['aggr_sum']
                            else:
                                # BuildingTypePostprocessor
                                # See issue #2258. Since we are only
                                # working with one road at a time we
                                # should only add 1.
                                result += 1
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
        """Indicator that shows total features impacted.

        This indicator reports the features by type. The logic is:
        - look for the fields that occurs with a name included in
            self.valid_type_fields
        - look in those fields for any of the values of self.fields_values
        - if a record has one of the valid fields with one of the valid
        fields_values then it is considered affected
        """

        title = tr(title)

        result = 0
        if self.type_fields is not None:
            try:
                for feature in self.impact_attrs:
                    for type_field in self.type_fields:
                        feature_type = feature[type_field]
                        if feature_type in fields_values:
                            field_value = feature[self.target_field]
                            if isinstance(field_value, basestring):
                                if field_value != 'Not Affected':
                                    if self.type == 'RoadTypePostprocessor':
                                        result += feature['aggr_sum']
                                    else:
                                        # BuildingTypePostprocessor
                                        # See issue #2258. Since we are only
                                        # working with one road at a time we
                                        # should only add 1.
                                        result += 1
                            else:
                                if field_value:
                                    if self.type == 'RoadTypePostprocessor':
                                        result += feature['aggr_sum']
                                    else:
                                        # BuildingTypePostprocessor
                                        # See issue #2258. Since we are only
                                        # working with one road at a time we
                                        # should only add 1.
                                        result += 1
                            break
                        elif self._is_unknown_type(feature_type):
                            self._update_known_types(feature_type)

                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(title, result)

    def clear(self):
        """concrete implementation that ensures needed parameters are cleared.
        """
        AbstractPostprocessor.clear(self)
        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None
        self.type_fields = None
        self.value_mapping = None
        self.valid_type_fields = None

    def _is_unknown_type(self, feature_type):
        """Check if the given type is in any of the known_types dictionary.

        :param feature_type: The name of the type.
        :type feature_type: str

        :returns: Flag indicating if the feature_type is unknown.
        :rtype: boolean
        """

        is_unknown = feature_type not in self.known_types
        return is_unknown

    def _update_known_types(self, feature_type=None):
        """
        Adds a feature_type (if passed) and updates the known_types list

        This is called each time a new unknown type is found and is needed so
        that self._is_unknown_type (which is called many times) to perform
        only a simple 'in' check

        :param feature_type: the name of the type to add to the known types.
        :type feature_type: str
        """
        # Fixme, as we use a mapping to classify values, do we need this ?
        """
        if type is not None:
            self.fields_values['Other'].append(building_type)

        # flatten self.fields_values.values()
        # using http://stackoverflow.com/questions/5286541/#5286614
        self.known_types = list(itertools.chain.from_iterable(
            itertools.repeat(x, 1) if isinstance(x, str) else x for x in
            self.fields_values.values()))
        """
        return
