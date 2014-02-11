# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '22/08/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor

from safe.common.utilities import (ugettext as tr)


class MinimumNeedsPostprocessor(AbstractPostprocessor):
    """
    Postprocessor that aggregates minimum needs.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for MinimumNeedsPostprocessor postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)
        self.impact_total = None
        self.minimum_needs = None

    def description(self):
        """Describe briefly what the post processor does.
            Errors are propagated
        """
        return tr('Aggregates minimum needs.')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        :param params: Parameters to pass to the post processor.
        :type params: dict
        """
        AbstractPostprocessor.setup(self, None)
        if self.impact_total is not None or self.minimum_needs is not None:
            self._raise_error('clear needs to be called before setup')

        try:
            self.impact_total = int(round(params['impact_total']))
        except (ValueError, TypeError):
            self.impact_total = self.NO_DATA_TEXT
        self.minimum_needs = params['function_params']['minimum needs']

    def process(self):
        """concrete implementation it takes care of the needed parameters being
         available and performs all the indicators calculations
        """
        AbstractPostprocessor.process(self)
        if self.impact_total is None or self.minimum_needs is None:
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_needs()

    def clear(self):
        """concrete implementation it takes care of the needed parameters being
         properly cleared
        """
        AbstractPostprocessor.clear(self)
        self.impact_total = None
        self.minimum_needs = None

    def _calculate_needs(self):
        """Indicator that shows aggregated minimum needs.

        this indicator reports the aggregated minimum needs
        """

        for need, value in self.minimum_needs.iteritems():
            try:
                result = int(round(value * self.impact_total))
            except (ValueError, TypeError):
                result = self.NO_DATA_TEXT

            self._append_result(need, result)
