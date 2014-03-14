# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.defaults import get_defaults
from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor
from safe.common.utilities import (ugettext as tr)


class AgePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates age related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for AgePostprocessor postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)
        self.impact_total = None

    def description(self):
        """Describe briefly what the post processor does.

        Args:
            None

        Returns:
            Str the translated description

        Raises:
            Errors are propagated
        """
        return tr('Calculates age related statistics.')

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
        if self.impact_total is not None:
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        try:
            #either all 3 ratio are custom set or we use defaults
            self.youth_ratio = params['youth_ratio']
            self.adult_ratio = params['adult_ratio']
            self.elder_ratio = params['elder_ratio']

            ratios_total = (self.youth_ratio +
                            self.adult_ratio +
                            self.elder_ratio)
            if ratios_total > 1:
                self._raise_error('Age ratios should sum up to 1. Found: '
                                  '%s + %s + %s = %s ' % (self.youth_ratio,
                                                          self.adult_ratio,
                                                          self.elder_ratio,
                                                          ratios_total))
        except KeyError:
            self._log_message('either all 3 age ratio are custom set or we'
                              ' use defaults')
            defaults = get_defaults()
            self.youth_ratio = defaults['YOUTH_RATIO']
            self.adult_ratio = defaults['ADULT_RATIO']
            self.elder_ratio = defaults['ELDER_RATIO']

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
        if self.impact_total is None:
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_total()
            self._calculate_youth()
            self._calculate_adult()
            self._calculate_elder()

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
        self.impact_total = None

    def _calculate_total(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Total')

        myResult = self.impact_total
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_youth(self):
        """Indicator that shows population below 15 years old.

        this indicator reports the amount of young population according to the
        set youth_ratio

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Youth count (affected)')
        myResult = self.impact_total * self.youth_ratio
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_adult(self):
        """Indicator that shows population between 15 and 64 years old.

        this indicator reports the amount of young population according to the
        set adult_ratio

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Adult count (affected)')
        myResult = self.impact_total * self.adult_ratio
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_elder(self):
        """Indicator that shows population above 64 years old.

        this indicator reports the amount of young population according to the
        set elder_ratio

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Elderly count (affected)')
        myResult = self.impact_total * self.elder_ratio
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)
