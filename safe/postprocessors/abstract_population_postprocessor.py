# -*- coding: utf-8 -*-
"""**Abstract postprocessor class, do not instantiate directly**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor

LOGGER = logging.getLogger('InaSAFE')


class AbstractPopulationPostprocessor(AbstractPostprocessor):

    def __init__(self):
        AbstractPostprocessor.__init__(self)

    def _calculate_total(self):
        raise NotImplementedError
