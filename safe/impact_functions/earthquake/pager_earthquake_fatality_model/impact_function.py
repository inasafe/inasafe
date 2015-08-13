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
import heapq

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
            ('calculate_displaced_people', True),
            ('magnitude_bin', numpy.power(10, range(0, 6), dtype=float))
        ])

    # noinspection PyPep8Naming
    def cdf_normal(self, x):
        """Cumulative distribution function of standard normal distribution.

        Logic based on http://en.wikipedia.org/wiki/Normal_distribution

        :param x
        :type x: float

        :returns: phi of (x)
        :rtype: float
        """
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def fatality_rate(self, mmi):
        """Pager method to compute fatality rate.

        :param mmi: MMI
        :type mmi: float

        :returns: Fatality rate calculated as:
            lognorm.cdf(mmi, shape=Beta, scale=Theta)
        :rtype: float
        """
        theta = self.hardcoded_parameters['Theta']
        beta = self.hardcoded_parameters['Beta']
        x = math.log(mmi / theta) / beta
        return self.cdf_normal(x)

    @staticmethod
    def round_to_sum(l, r):
        """
        Round a list of numbers while maintaining the sum.

        http://stackoverflow.com/questions/15769948/
        round-a-python-list-of-numbers-and-maintain-the-sum

        :param l: array
        :type l: list(float)

        :param r: decimal place
        :type r: int

        :returns: A list of rounded numbers whose sum is equal to the
            sum of the list of input numbers.
        :rtype: list
        """
        q = 10**(-r)
        d = int((round(sum(l), r) - sum([round(x, r) for x in l])) * (10**r))
        if d == 0:
            return [round(x, r) for x in l]
        elif d in [-1, 1]:
            c, _ = max(enumerate(l), key=lambda x: math.copysign(
                1, d) * math.fmod(x[1] - 0.5*q, q))
            return [round(x, r) + q * math.copysign(1, d) if i == c else round(
                x, r) for (i, x) in enumerate(l)]
        else:
            c = [i for i, _ in heapq.nlargest(abs(d), enumerate(
                l), key=lambda x: math.copysign(1, d) * math.fmod(
                    x[1]-0.5*q, q))]
            return [round(x, r) + q * math.copysign(
                1, d) if i in c else round(x, r) for (i, x) in enumerate(l)]

    def compute_probability(self, total_fatalities):
        """Pager method compute probaility of fatality in each magnitude bin.

        (0,1), (1,10), (10,10^2), (10^2,10^3), (10^3, 10^4),
        (10^4, 10^5), (10^5, 10^6+)

        :param total_fatalities: List of total fatalities in each MMI class.
        :type total_fatalities: int, float

        :returns: Probability of fatality magnitude bin from
            lognorm.cdf(bin, shape=Zeta, scale=total_fatalities)
        :rtype: list(float)
        """
        zeta = self.hardcoded_parameters['Zeta']
        magnitude_bin = self.hardcoded_parameters['magnitude_bin']
        cprob = numpy.ones_like(magnitude_bin, dtype=float)

        if total_fatalities > 1:
            for (i, mbin) in enumerate(magnitude_bin):
                x = math.log(mbin / total_fatalities) / zeta
                cprob[i] = self.cdf_normal(x)

        cprob = numpy.append(cprob, 1.0) # 1000+
        prob = numpy.hstack((cprob[0], numpy.diff(cprob)))*100.0 # percentage
        return self.round_to_sum(prob, 0) # rounding to decimal
