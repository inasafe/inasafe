# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - ITB Earthquake
Impact Function on Population based on a Bayesian approach.

Contact : dynaryu@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'dynaryu@gmail.com'
__date__ = '09/09/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy
import os
import inspect

from safe.common.utilities import OrderedDict
from safe.impact_functions.earthquake.\
    itb_earthquake_fatality_model.impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake\
    .itb_bayesian_earthquake_fatality_model.metadata_definitions import \
    ITBBayesianFatalityMetadata


class ITBBayesianFatalityFunction(ITBFatalityFunction):
    # noinspection PyUnresolvedReferences
    """ ITB fatality model based on a Bayesian approach

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hyeuk Ryu, Geoscience Australia.

    Reference:

    An Empirical Fatality Model for Indonesia Based on a Bayesian Approach
    by W. Sengara, M. Suarjana, M.A. Yulman, H. Ghasemi, and H. Ryu
    submitted for Journal of the Geological Society

    """
    _metadata = ITBBayesianFatalityMetadata()

    def __init__(self):
        super(ITBBayesianFatalityFunction, self).__init__()
        self.hardcoded_parameters = OrderedDict([
            ('fatality_rate_file',
             "worden_berngamma_log_fat_rate_inasafe_10.csv"),
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

    def compute_fatality_rate(self):
        """Fatality rate by MMI from Bayesian approach.

        :returns: Fatality rate loaded from numpy file
        :rtype: dic
        """
        mmi_range = self.hardcoded_parameters['mmi_range']
        metadata_file_path = inspect.getfile(ITBBayesianFatalityMetadata)
        parent_directory, _ = os.path.split(metadata_file_path)
        file_ = os.path.join(
            parent_directory, self.hardcoded_parameters['fatality_rate_file'])
        fatality_ = numpy.loadtxt(file_, dtype=float, delimiter=',')
        nsims = len(fatality_)
        fatality_rate = {}
        for mmi in mmi_range[:2]:  # mmi < 4
            fatality_rate[mmi] = numpy.zeros((nsims, 1))
        for i, mmi in enumerate(mmi_range[2:]):  # mmi >= 4
            fatality_rate[mmi] = fatality_[:, i][:, numpy.newaxis]
        return fatality_rate

    def compute_probability(self, total_fatalities):
        """ Compute probaility of fatality in each magnitude bin.

        [0, 10), [10,10^2), [10^2,10^3), [10^3, 10^4), [10^4, 10^5),
        [10^5,)

        :param total_fatalities: List of total fatalities in each MMI class.
        :type total_fatalities: int, float

        :returns: Probability of fatality magnitude bin from
            lognorm.cdf(bin, shape=Zeta, scale=total_fatalities)
        :rtype: list(float) """

        magnitude_bin = self.hardcoded_parameters['magnitude_bin']
        nsamples = float(len(total_fatalities))
        cprob = numpy.ones(len(magnitude_bin) + 1)
        for j, val in enumerate(magnitude_bin):
            cprob[j] = numpy.sum(total_fatalities < val) / nsamples

        prob = numpy.hstack((cprob[0], numpy.diff(cprob))) * 100.0
        return self.round_to_sum(prob)



        fields.append(tr(
            'Fatality model is from the Population Vulnerability '
            'Pager Model.'))
