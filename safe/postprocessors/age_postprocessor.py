# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""
from safe.utilities.i18n import tr

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.defaults import get_defaults
from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor


class AgePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates age related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for AgePostprocessor postprocessor class.

        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)
        self.youth_ratio = None
        self.adult_ratio = None
        self.elderly_ratio = None
        self.impact_total = None

    def description(self):
        """Describe briefly what the post processor does.

        :returns: The translated description.
        :rtype: str
        """
        return tr('Calculates age related statistics.')

    def setup(self, params):
        """Concrete implementation to ensure needed parameters are initialized.

        :param params: Dict of parameters to pass to the post processor.
        :type params: dict

        """
        AbstractPostprocessor.setup(self, None)
        if self.impact_total is not None:
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        try:
            # either all 3 ratio are custom set or we use defaults
            self.youth_ratio = params['youth_ratio']
            self.adult_ratio = params['adult_ratio']
            self.elderly_ratio = params['elderly_ratio']

            ratios_total = (self.youth_ratio +
                            self.adult_ratio +
                            self.elderly_ratio)
            if ratios_total > 1:
                self._raise_error(
                    'Age ratios should sum up to 1. Found: '
                    '%s + %s + %s = %s ' % (
                        self.youth_ratio,
                        self.adult_ratio,
                        self.elderly_ratio,
                        ratios_total))
        except KeyError:
            self._log_message('either all 3 age ratio are custom set or we'
                              ' use defaults')
            defaults = get_defaults()
            self.youth_ratio = defaults['YOUTH_RATIO']
            self.adult_ratio = defaults['ADULT_RATIO']
            self.elderly_ratio = defaults['ELDERLY_RATIO']

    def process(self):
        """Performs all the indicator calculations.
        """
        AbstractPostprocessor.process(self)
        if self.impact_total is None:
            self._log_message(
                '%s not all params have been correctly '
                'initialized, setup needs to be called before '
                'process. Skipping this postprocessor'
                % self.__class__.__name__)
        else:
            self._calculate_total()
            self._calculate_youth()
            self._calculate_adult()
            self._calculate_elderly()

    def clear(self):
        """Clear postprocessor state.
        """
        AbstractPostprocessor.clear(self)
        self.impact_total = None

    def _calculate_total(self):
        """Indicator that shows total population.

        This indicator reports the total population.
        """
        name = tr('Total')

        result = self.impact_total
        try:
            result = int(round(result))
        except ValueError:
            result = self.NO_DATA_TEXT
        self._append_result(name, result)

    def _calculate_youth(self):
        """Indicator that shows population below 15 years old.

        This indicator reports the amount of young population according to the
        set youth_ratio.

        """
        name = tr('Youth count (affected)')
        result = self.impact_total * self.youth_ratio
        try:
            result = int(round(result))
        except ValueError:
            result = self.NO_DATA_TEXT
        self._append_result(name, result)

    def _calculate_adult(self):
        """Indicator that shows population between 15 and 64 years old.

        This indicator reports the amount of young population according to the
        set adult_ratio.

        """
        name = tr('Adult count (affected)')
        result = self.impact_total * self.adult_ratio
        try:
            result = int(round(result))
        except ValueError:
            result = self.NO_DATA_TEXT
        self._append_result(name, result)

    def _calculate_elderly(self):
        """Indicator that shows population above 64 years old.

        This indicator reports the amount of young population according to the
        set elderly_ratio.

        """
        name = tr('Elderly count (affected)')

        # FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(name, self.NO_DATA_TEXT)
            return

        result = self.impact_total * self.elderly_ratio
        try:
            result = int(round(result))
        except ValueError:
            result = self.NO_DATA_TEXT
        self._append_result(name, result)
