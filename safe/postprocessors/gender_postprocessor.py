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
from safe.common.utilities import ugettext as tr # pylint: disable=W0611

from safe.postprocessors.abstract_postprocessor import (
    AbstractPostprocessor)


class GenderPostprocessor(AbstractPostprocessor):
    def __init__(self):
        AbstractPostprocessor.__init__(self)
        self.population_total = None
        self.female_ratio = None

    def setup(self, population_total, female_ratio):
        AbstractPostprocessor.setup(self)
        if self.population_total is not None or self.female_ratio is not None:
            self.raise_error('clear needs to be called before setup')
        self.population_total = population_total
        self.female_ratio = female_ratio

    def process(self):
        AbstractPostprocessor.process(self)
        if self.population_total is None or self.female_ratio is None:
            self.raise_error('setup needs to be called before process')
        self._calculate_females()
        self._calculate_female_weekly_hygene_packs()

    def clear(self):
        AbstractPostprocessor.clear(self)
        self.population_total = None
        self.female_ratio = None

    def _calculate_females(self):
        myName = self.tr('Females count')
        myResult = self.population_total * self.female_ratio
        myResult = int(round(myResult))
        self._append_result(myName, myResult)

    def _calculate_female_weekly_hygene_packs(self):
        myName = self.tr('Females weekly hygene packs')
        myMeta = {'description': 'Females hygene packs for weekly use'}
        #weekly hygene packs =
        # affected pop * fem_ratio * 0.7937 * week / intended day-of-use
        myResult = self.population_total * self.female_ratio * 0.7937 * (7 / 7)
        myResult = int(round(myResult))
        self._append_result(myName, myResult, myMeta)
