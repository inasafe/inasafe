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

from safe.common.utilities import OrderedDict
from safe.impact_functions.earthquake.\
    itb_earthquake_fatality_model.impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake\
    .pager_earthquake_fatality_model.metadata_definitions import \
    PAGFatalityMetadata

class PAGFatalityFunction(ITBFatalityFunction):
    # noinspection PyUnresolvedReferences
    """USGS Pager fatality estimation model.
    Fatality rate(MMI) = cum. standard normal dist(1/BETA * ln(MMI/THETA)).
    Reference:
    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.
    v1.0:
        Theta: 14.05, Beta: 0.17, Zeta 2.15
        Jaiswal, K, and Wald, D (2010)
        An Empirical Model for Global Earthquake Fatality Estimation
        Earthquake Spectra, Volume 26, No. 4, pages 1017–1037
    v2.0:
        Theta: 13.249, Beta: 0.151, Zeta: 1.641)
        (http://pubs.usgs.gov/of/2009/1136/pdf/
        PAGER%20Implementation%20of%20Empirical%20model.xls)
    """
    _metadata = PAGFatalityMetadata()

    def __init__(self):
        super(PAGFatalityFunction, self).__init__()
        self.hardcoded_parameters = OrderedDict([
            ('Theta', 13.249),
            ('Beta', 0.151),
            ('Zeta', 1.641), # Model coefficients
            # Rates of people displaced for each MMI level
            ('displacement_rate', {
                2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 1.0,
                7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0}), # Seems not model specific
            ('mmi_range', range(2, 11)),
            ('step', 0.5),
            # Threshold below which layer should be transparent
            ('tolerance', 0.01),
            ('calculate_displaced_people', True)
        ])

    # noinspection PyPep8Naming
    def fatality_rate(self, mmi):
        """Pager method to compute fatality rate.

        :param mmi: MMI

        :returns: Fatality rate
            lognorm.cdf(mmi, shape=Beta, scale=Theta)
        """
        THETA = self.hardcoded_parameters['Theta']
        BETA = self.hardcoded_parameters['Beta']

        x = math.log(mmi / THETA) / BETA
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
