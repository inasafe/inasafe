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
        AbstractPostprocessor.__init__()
        self.populationTotal = None
        self.femaleRatio = None

    def setup(self, thePopulationTotal, theFemaleRatio):
        AbstractPostprocessor.setup()
        if self.populationTotal is not None or self.femaleRatio is not None:
            self.raiseError('clear needs to be called before setup')
        self.populationTotal = thePopulationTotal
        self.femaleRatio = theFemaleRatio

    def process(self):
        AbstractPostprocessor.process()
        if self.populationTotal is None or self.femaleRatio is None:
            self.raiseError('setup needs to be called before process')
        self._calculateFemales()
        self._calculateFemaleWeeklyHygenePacks()
        self._clear()

    def clear(self):
        AbstractPostprocessor.clear()
        self.populationTotal = None
        self.femaleRatio = None

    def _calculateFemales(self):
        myName = self.tr('Females count')
        myResult = self.populationTotal * self.femaleRatio
        self._appendResult(myName, myResult)

    def _calculateFemales(self):
        myName = self.tr('Females count')
        myResult = self.populationTotal * self.femaleRatio
        self._appendResult(myName, myResult)

    def _calculateFemaleWeeklyHygenePacks(self):
        myName = self.tr('Females daily hygene packs')
        myMeta = {'description': 'Females hygene packs for weekly use'}
        #FIXME: (MB) include self.femaleRatio
        #weekly hygene packs =
        # affected pop * 0.3969 * week / intended day-of-use
        myResult = self.populationTotal * 0.3969 * (7 / 7)
        self._appendResult(myName, myResult, myMeta)
