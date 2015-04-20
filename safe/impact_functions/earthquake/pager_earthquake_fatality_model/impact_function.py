# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - PAGER Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import math
import numpy

from safe.common.utilities import OrderedDict
from safe.impact_functions.earthquake.\
    itb_earthquake_fatality_model.impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake\
    .pager_earthquake_fatality_model.metadata_definitions import \
    PAGFatalityMetadata


class PAGFatalityFunction(ITBFatalityFunction):
    # noinspection PyUnresolvedReferences
    """Population Vulnerability Model Pager.

    Loss ratio(MMI) = standard normal distrib( 1 / BETA * ln(MMI/THETA)).
    Reference:
    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.
    """
    _metadata = PAGFatalityMetadata()

    def __init__(self):
        super(PAGFatalityFunction, self).__init__()
        self.hardcode_parameters = OrderedDict([
            ('Theta', 11.067),
            ('Beta', 0.106),  # Model coefficients
            # Rates of people displaced for each MMI level
            ('displacement_rate', {
                1: 0, 1.5: 0, 2: 0, 2.5: 0, 3: 0,
                3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0,
                6: 1.0, 6.5: 1.0, 7: 1.0, 7.5: 1.0,
                8: 1.0, 8.5: 1.0, 9: 1.0, 9.5: 1.0,
                10: 1.0}),
            ('mmi_range', list(numpy.arange(2, 10, 0.5))),
            ('step', 0.25),
            # Threshold below which layer should be transparent
            ('tolerance', 0.01),
            ('calculate_displaced_people', True)
        ])

    # noinspection PyPep8Naming
    def fatality_rate(self, mmi):
        """Pager method to compute fatality rate.

        :param mmi: MMI

        :returns: Fatality rate
        """

        N = math.sqrt(2 * math.pi)
        THETA = self.hardcode_parameters['Theta']
        BETA = self.hardcode_parameters['Beta']

        x = math.log(mmi / THETA) / BETA
        return math.exp(-x * x / 2.0) / N
