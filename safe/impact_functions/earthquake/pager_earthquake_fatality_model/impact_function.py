# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - PAGER Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae, dynaryu@gmail.com'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy

from safe.common.utilities import OrderedDict
from safe.gis.numerics import log_normal_cdf
from safe.impact_functions.earthquake.\
    itb_earthquake_fatality_model.impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake\
    .pager_earthquake_fatality_model.metadata_definitions import \
    PAGFatalityMetadata
from safe.utilities.i18n import tr


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
            ('Zeta', 1.641),  # Model coefficients
            # Rates of people displaced for each MMI level
            # FIXME: should be independent from fatality model - Hyeuk
            ('displacement_rate', {
                2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 1.0,
                7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0}),
            ('mmi_range', range(2, 11)),
            ('step', 0.5),
            # Threshold below which layer should be transparent
            ('tolerance', 0.01),
            ('calculate_displaced_people', True),
            ('magnitude_bin', numpy.power(10, range(1, 6), dtype=float))
        ])

    def notes(self):
        """Notes and caveats for the IF report.

        :returns: List containing notes.
        :rtype: list
        """
        fields = [
            tr(
                'Fatality model is from the Population Vulnerability '
                'Pager Model.'),
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def compute_fatality_rate(self):
        """Pager method to compute fatality rate.

        :returns: Fatality rate calculated as:
            lognorm.cdf(mmi, shape=Beta, scale=Theta)
        :rtype: dic
        """
        mmi_range = self.hardcoded_parameters['mmi_range']
        theta = self.hardcoded_parameters['Theta']
        beta = self.hardcoded_parameters['Beta']
        fatality_rate = {mmi: 0 if mmi < 4 else log_normal_cdf(
            mmi, median=theta, sigma=beta) for mmi in mmi_range}
        return fatality_rate

    def compute_probability(self, total_fatalities):
        """Pager method compute probaility of fatality in each magnitude bin.

        [0, 10), [10,10^2), [10^2,10^3), [10^3, 10^4), [10^4, 10^5),
        [10^5,)

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
            cprob = log_normal_cdf(
                magnitude_bin, median=total_fatalities, sigma=zeta)

        cprob = numpy.append(cprob, 1.0)
        prob = numpy.hstack((cprob[0], numpy.diff(cprob))) * 100.0
        return self.round_to_sum(prob)
