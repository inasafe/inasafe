# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from collections import OrderedDict
import itertools

from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor
from safe.utilities.i18n import tr


class BuildingTypePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates building types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class.
        """
        AbstractPostprocessor.__init__(self)
        self.impact_attrs = None
        self.target_field = None
        self.no_features = True
        self.type_field = None
        self.class_scores = {}  # number of each class affected
        self.class_totals = {}  # number of each class regardless if affected

    def description(self):
        """Describe briefly what the post processor does.

        :returns: The translated description.
        :rtype: str
        """
        return tr('Calculates building types related statistics.')

    def setup(self, params):
        """Initialiser for parameters.

        :param params: dict of parameters to pass to the post processor
        """
        AbstractPostprocessor.setup(self, None)
        if (self.impact_attrs is not None or
                self.target_field is not None or
                self.type_field is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']
        self.type_field = params['key_attribute']

        if len(self.type_field) == 0:
            self.type_field = None

        # there are no features in this postprocessing polygon
        if len(self.impact_attrs):
            self.no_features = True
        self.class_scores = {}
        self.class_totals = {}

    def process(self):
        """Concrete implementation that performs all indicators calculations.
        """
        AbstractPostprocessor.process(self)

        if self.impact_attrs is None or self.target_field is None:
            self._log_message(
                '%s not all params have been correctly initialized, '
                'setup needs to be called before process. Skipping this '
                'postprocessor' % self.__class__.__name__)
            return

        affected = 0
        total = 0
        for building in self.impact_attrs:
            total += 1
            building_type = building[self.type_field]
            if building_type not in self.class_scores:
                # Create an empty key for it since it does not exist
                self.class_scores[building_type] = 0
            if building_type not in self.class_totals:
                # Create an empty key for it since it does not exist
                self.class_totals[building_type] = 0

            self.class_totals[building_type] += 1
            field_value = building[self.target_field]
            if isinstance(field_value, basestring):
                # This needs to be softcoded to the keywords list of poss vals
                if field_value != 'Not Affected':
                    self.class_scores[building_type] += 1
                    affected += 1
            else:
                if field_value:
                    # See issue #2258. Since we are only working with
                    # one building at a time we should only add 1.
                    self.class_scores[building_type] += 1
                    affected += 1
        self._append_result(tr('Total Affected'), self.class_scores)
        self._append_result(tr('Total Counted'), self.class_totals)
        print self.results()

    def clear(self):
        """
        Concrete implementation that ensures needed parameters are cleared.
        """
        AbstractPostprocessor.clear(self)
        self.impact_attrs = None
        self.target_field = None
        self.type_field = None
        self.class_scores = None
        self.no_features = True
