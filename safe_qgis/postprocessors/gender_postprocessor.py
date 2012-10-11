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

from safe_qgis.postprocessors.abstract_postprocessor import (
    AbstractPostprocessor)


class GenderPostprocessor(AbstractPostprocessor):
    def __init__(self):
        AbstractPostprocessor.__init__(self)
        self.populationTotal = None
        self.femaleRatio = None

    def setup(self, thePopulationTotal, theFemaleRatio):
        AbstractPostprocessor.setup(self)
        if self.populationTotal is not None or self.femaleRatio is not None:
            self.raiseError('clear needs to be called before setup')
        self.populationTotal = thePopulationTotal
        self.femaleRatio = theFemaleRatio

    def process(self):
        AbstractPostprocessor.process(self)
        if self.populationTotal is None or self.femaleRatio is None:
            self.raiseError('setup needs to be called before process')
        self._calculateFemales()
        self._calculateFemaleWeeklyHygenePacks()

    def clear(self):
        AbstractPostprocessor.clear(self)
        self.populationTotal = None
        self.femaleRatio = None

    def _calculateFemales(self):
        myName = self.tr('Females count')
        myResult = self.populationTotal * self.femaleRatio
        myResult = int(round(myResult))
        self._appendResult(myName, myResult)

    def _calculateFemaleWeeklyHygenePacks(self):
        myName = self.tr('Females weekly hygene packs')
        myMeta = {'description': 'Females hygene packs for weekly use'}
        #weekly hygene packs =
        # affected pop * fem_ratio * 0.7937 * week / intended day-of-use
        myResult = self.populationTotal * self.femaleRatio * 0.7937 * (7 / 7)
        myResult = int(round(myResult))
        self._appendResult(myName, myResult, myMeta)
