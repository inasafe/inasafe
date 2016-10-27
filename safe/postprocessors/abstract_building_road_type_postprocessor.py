# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'Etienne Trimaille'
__revision__ = '$Format:%H$'
__date__ = '10/05/2016'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor
from safe.utilities.utilities import reorder_dictionary, main_type


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

        # Integer with total number of features/metres affected.
        self.impact_total = None

        # List of features
        self.impact_attrs = None

        # Name the field in the impact layer for the result.
        self.target_field = None

        # The name of field in the exposure layer.
        self.valid_type_fields = None

        # The value mapping for the exposure layer.
        self.value_mapping = None

        # Bool to know if there are some features. We will be computed later.
        self.no_features = None

        # Find which attribute field has to be used
        self.type_fields = None

        # Dictionary key - display name for the mapping.
        self._labels = {}

        # The categories order.
        self._order = None

    @staticmethod
    def feature_value(feature):
        """Return the value to add in the statistics.

        :param feature: The feature.
        """
        raise NotImplementedError

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

        self.value_mapping = reorder_dictionary(
            params['value_map'], self._order)

        self.valid_type_fields = params['key_attribute']

        self.type_fields = []
        try:
            for key in self.impact_attrs[0].iterkeys():
                if key in self.valid_type_fields:
                    self.type_fields.append(key)
        except IndexError:
            pass

        if len(self.type_fields) == 0:
            self.type_fields = None

        # there are no features in this postprocessing polygon
        self.no_features = None
        if len(self.impact_attrs):
            self.no_features = True

        if 'other' not in self.value_mapping.keys():
            self.value_mapping['other'] = []

    def process(self):
        """Concrete implementation that performs all indicators calculations.
        """
        AbstractPostprocessor.process(self)

        if (self.impact_total is None or
                self.impact_attrs is None or
                self.value_mapping is None or
                self.target_field is None):
            self._log_message(
                '%s not all params have been correctly initialized, setup '
                'needs to be called before process. Skipping this '
                'postprocessor.' % self.__class__.__name__)
        else:
            for title in self.value_mapping:
                self._calculate_type(title)
            self.translate_results()

    def _calculate_type(self, category):
        """Indicator that shows total features impacted for one category.

        This indicator reports the features by category. The logic is:
        - look for the fields that occurs with a name included in
            self.valid_type_fields
        - if the main usage from a record is equal to the category then it is
            considered affected.

        This function uses safe.utilities.utilities.main_type
        """

        result = 0
        if self.type_fields is not None:
            try:
                for feature in self.impact_attrs:
                    for type_field in self.type_fields:
                        field_value = feature[self.target_field]
                        val = 0
                        if isinstance(field_value, basestring):
                            if field_value != 'Not Affected':
                                val += self.feature_value(feature)
                        else:
                            if field_value:
                                val += self.feature_value(feature)

                        if val:
                            feature_type = feature[type_field]
                            main_feature_type = main_type(
                                feature_type, self.value_mapping)
                            if main_feature_type == category:
                                result += val
                                break

                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(category, result)

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

    def translate_results(self):
        """Replace keys in the result table by the beautiful translated name.
        """
        for key in self._results:
            if key in self._labels:
                translation = self._labels[key]
                self._results[translation] = self._results[key]
                del self._results[key]
