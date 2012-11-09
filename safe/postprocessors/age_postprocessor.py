# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.abstract_postprocessor import (
    AbstractPostprocessor)

from safe.common.utilities import (get_defaults,
                                   ugettext as tr)


class AgePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates age related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for AgePostprocessor postprocessor class,
        It takes care of defining self.population_total
        """
        AbstractPostprocessor.__init__(self)
        self.population_total = None

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
        if self.population_total is not None:
            self._raise_error('clear needs to be called before setup')

        self.population_total = params['population_total']
        try:
            #either all 3 ratio are custom set or we use defaults
            self.youth_ratio = params['youth_ratio']
            self.adult_ratio = params['adult_ratio']
            self.elder_ratio = params['elder_ratio']
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
        if self.population_total is None:
            self._raise_error('setup needs to be called before process')
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
        self.population_total = None

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

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.population_total > 8000000000 or self.population_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.population_total
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
        myName = tr('Youth count')

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.population_total > 8000000000 or self.population_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.population_total * self.youth_ratio
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
        myName = tr('Adult count')

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.population_total > 8000000000 or self.population_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.population_total * self.adult_ratio
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
        myName = tr('Elderly count')

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.population_total > 8000000000 or self.population_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.population_total * self.elder_ratio
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)
