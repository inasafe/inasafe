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


class GenderPostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates gender related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        AbstractPostprocessor.__init__(self)
        self.impact_total = None
        self.female_ratio = None

    def description(self):
        """Describe briefly what the post processor does.

        Args:
            None

        Returns:
            Str the translated description

        Raises:
            Errors are propagated
        """
        return tr('Calculates gender related statistics.')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        Args:
            params: Dict of parameters to pass to the post processor
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.setup(self, None)
        if self.impact_total is not None or self.female_ratio is not None:
            self._raise_error('clear needs to be called before setup')
        self.impact_total = params['impact_total']
        self.female_ratio = params['female_ratio']

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
        if self.impact_total is None or self.female_ratio is None:
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_total()
            self._calculate_females()
            self._calculate_weekly_hygene_packs()
            self._calculate_weekly_increased_calories()

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
        self.female_ratio = None

    def _calculate_total(self):
        """Total population indicator.

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
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        try:
            myResult = self.impact_total
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_females(self):
        """Female population count indicator.

        this indicator reports the amount of female population according to the
        set female_ratio

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Female population')

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.impact_total * self.female_ratio
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_weekly_hygene_packs(self):
        """Weekly requirements of female hygiene packs indicator.

        This indicator reports the weekly requirements of female hygiene packs
        for further detail refer to the "Sample InaSAFE Actions for Vulnerable
        Populations" [27.07.2012] paper

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Weekly hygiene packs')
        myMeta = {'description': 'Females hygiene packs for weekly use'}

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT, myMeta)
            return

        #weekly hygene packs =
        # affected pop * fem_ratio * 0.7937 * week / intended day-of-use
        myResult = self.impact_total * self.female_ratio * 0.7937 * (7 / 7)
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult, myMeta)

    def _calculate_weekly_increased_calories(self):
        """Weekly additional kg of rice for pregnant and lactating women
        indicator.

        This indicator reports the weekly additional kg of rice for pregnant
        and lactating women.
        for further detail refer to the "Sample InaSAFE Actions for Vulnerable
        Populations" [27.07.2012] paper

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Additional weekly rice kg for pregnant and lactating'
                    ' women')
        myMeta = {'description': 'Additional rice kg per week for pregnant and'
                                 ' lactating women'}

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT, myMeta)
            return

        #weekly Kg rice =
        # affected pop * fem_ratio * 0.7937 * week / intended day-of-use
        myLactKg = self.impact_total * self.female_ratio * 2 * 0.033782
        myPregKg = self.impact_total * self.female_ratio * 2 * 0.01281
        myResult = myLactKg + myPregKg
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult, myMeta)
