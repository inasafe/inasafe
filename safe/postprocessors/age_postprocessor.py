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


class AgePostprocessor(AbstractPostprocessor):
    """
    https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    Age structure:
    0-14 years: 26.3% (male 944,987,919/female 884,268,378)
    15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
    65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)
    """
    YOUTH_RATIO = 0.263
    ADULT_RATIO = 0.659
    ELDERLY_RATIO = 0.079

    def __init__(self):
        AbstractPostprocessor.__init__(self)
        self.populationTotal = None

    def setup(self, thePopulationTotal):
        AbstractPostprocessor.setup(self)
        if self.populationTotal is not None:
            self.raiseError('clear needs to be called before setup')
        self.populationTotal = thePopulationTotal

    def process(self):
        AbstractPostprocessor.process(self)
        if self.populationTotal is None:
            self.raiseError('setup needs to be called before process')
        self._calculateYouth()
        self._calculateAdult()
        self._calculateElderly()

    def clear(self):
        AbstractPostprocessor.clear(self)
        self.populationTotal = None

    def _calculateYouth(self):
        myName = self.tr('Youth count')
        myResult = self.populationTotal * self.YOUTH_RATIO
        myResult = int(round(myResult))
        self._appendResult(myName, myResult)

    def _calculateAdult(self):
        myName = self.tr('Adult count')
        myResult = self.populationTotal * self.ADULT_RATIO
        myResult = int(round(myResult))
        self._appendResult(myName, myResult)

    def _calculateElderly(self):
        myName = self.tr('Elderly count')
        myResult = self.populationTotal * self.ELDERLY_RATIO
        myResult = int(round(myResult))
        self._appendResult(myName, myResult)

