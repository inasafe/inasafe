"""
InaSAFE Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.postprocessors.abstract_postprocessor import (
    AbstractPostprocessor)

from safe.defaults import (DEFAULT_YOUTH_RATIO,
                           DEFAULT_ADULT_RATIO,
                           DEFAULT_ELDER_RATIO)


class AgePostprocessor(AbstractPostprocessor):
    """
    https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    Age structure:
    0-14 years: 26.3% (male 944,987,919/female 884,268,378)
    15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
    65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)
    """

    def __init__(self):
        AbstractPostprocessor.__init__(self)
        self.population_total = None

    def setup(self, params):
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
            self.youth_ratio = DEFAULT_YOUTH_RATIO
            self.adult_ratio = DEFAULT_ADULT_RATIO
            self.elder_ratio = DEFAULT_ELDER_RATIO

    def process(self):
        AbstractPostprocessor.process(self)
        if self.population_total is None:
            self._raise_error('setup needs to be called before process')
        self._calculate_total()
        self._calculate_youth()
        self._calculate_adult()
        self._calculate_elder()

    def clear(self):
        AbstractPostprocessor.clear(self)
        self.population_total = None

    def _calculate_total(self):
        myName = self.tr('Total')
        myResult = self.population_total
        myResult = int(round(myResult))
        self._append_result(myName, myResult)

    def _calculate_youth(self):
        myName = self.tr('Youth count')
        myResult = self.population_total * self.youth_ratio
        myResult = int(round(myResult))
        self._append_result(myName, myResult)

    def _calculate_adult(self):
        myName = self.tr('Adult count')
        myResult = self.population_total * self.adult_ratio
        myResult = int(round(myResult))
        self._append_result(myName, myResult)

    def _calculate_elder(self):
        myName = self.tr('Elderly count')
        myResult = self.population_total * self.elder_ratio
        myResult = int(round(myResult))
        self._append_result(myName, myResult)
