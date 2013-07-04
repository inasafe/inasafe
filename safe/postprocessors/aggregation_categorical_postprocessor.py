# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor

from safe.common.utilities import ugettext as tr


class AggregationCategoricalPostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates categorical statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class,
        It takes care of defining self.impact_classes
        """
        AbstractPostprocessor.__init__(self)
        self.impact_classes = None
        self.impact_attrs = None
        self.target_field = None

    def description(self):
        """Describe briefly what the post processor does.

        Args:
            None

        Returns:
            Str the translated description

        Raises:
            Errors are propagated
        """
        return tr('Calculates generic categorical statistics.')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        Args:
            params: dict of parameters to pass to the post processor
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.setup(self, None)
        if (self.impact_classes is not None or
            self.impact_attrs is not None or
            self.target_field is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_classes = params['impact_classes']
        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']
        self._log_message(self.impact_attrs)

    def process(self):
        """concrete implementation it takes care of the needed parameters being
         available and performs all the indicators calculations

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.process(self)
        if (self.impact_classes is None or
            self.impact_attrs is None or
            self.target_field is None):
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_categories()

    def clear(self):
        """concrete implementation it takes care of the needed parameters being
         properly cleared

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.clear(self)
        self.impact_classes = None
        self.impact_attrs = None
        self.target_field = None

    def _calculate_categories(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """

        impact_name = tr(self.target_field).lower()

        results = {}
        for impact_class in self.impact_classes:
            results[impact_class] = 0

        for feature in self.impact_attrs:
            myTarget = feature[self.target_field]
            results[myTarget] += 1

        for impact_class in self.impact_classes:
            result = results[impact_class]
            self._append_result('%s %s' % (impact_name, impact_class), result)
