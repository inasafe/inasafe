import math
import numpy

from safe.impact_functions.earthquake.itb_earthquake_fatality_model import (
 ITBFatalityFunction)
from safe.common.utilities import ugettext as tr

from safe.common.utilities import get_defaults


class PAGFatalityFunction(ITBFatalityFunction):
    """
    Population Vulnerability Model Pager
    Loss ratio(MMI) = standard normal distrib( 1 / BETA * ln(MMI/THETA)).
    Reference:
    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.
    """

    title = tr('Die or be displaced according Pager model')
    defaults = get_defaults()
    parameters = dict(THETA=11.067, BETA=0.106,  # Model coefficients
                      # Rates of people displaced for each MMI level
                      displacement_rate={1: 0, 1.5: 0, 2: 0, 2.5: 0, 3: 0,
                                         3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0,
                                         6: 1.0, 6.5: 1.0, 7: 1.0, 7.5: 1.0,
                                         8: 1.0, 8.5: 1.0, 9: 1.0, 9.5: 1.0,
                                         10: 1.0},
                      mmi_range=numpy.arange(2, 10, 0.5),
                      step=0.25,
                      # Threshold below which layer should be transparent
                      tolerance=0.01,
                      calculate_displaced_people=True,
                      postprocessors={'Gender': {'on': True},
                          'Age': {'on': True,
                              'params':
                                  {'youth_ratio': defaults['YOUTH_RATIO'],
                                   'adult_ratio': defaults['ADULT_RATIO'],
                                   'elder_ratio': defaults['ELDER_RATIO']}}})

    def fatality_rate(self, mmi, THETA=11.067, BETA=0.106,
                        N=math.sqrt(2 * math.pi)):
        """Pager method to compute fatality rate"""

        x = math.log(mmi / THETA) / BETA
        return math.exp(-x * x / 2.0) / N
