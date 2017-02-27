# coding=utf-8

"""Definitions about earthquake."""

from safe.utilities.numerics import log_normal_cdf
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def itb_fatality_rates():
    """Indonesian Earthquake Fatality Model.

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hadi Ghasemi, Geoscience Australia.

    Reference:

    Indonesian Earthquake Building-Damage and Fatality Models and
    Post Disaster Survey Guidelines Development,
    Bali, 27-28 February 2012, 54pp.

    Algorithm:

    In this study, the same functional form as Allen (2009) is adopted
    to express fatality rate as a function of intensity (see Eq. 10 in the
    report). The Matlab built-in function (fminsearch) for  Nelder-Mead
    algorithm was used to estimate the model parameters. The objective
    function (L2G norm) that is minimised during the optimisation is the
    same as the one used by Jaiswal et al. (2010).

    The coefficients used in the indonesian model are
    x=0.62275231, y=8.03314466, zeta=2.15

    Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D., Hotovec, A. J.,
    Lin, K., and Hearne, M., 2009. An Atlas of ShakeMaps and population
    exposure catalog for earthquake loss modeling, Bull. Earthq. Eng. 7,
    701-718.

    Jaiswal, K., and Wald, D., 2010. An empirical model for global earthquake
    fatality estimation, Earthq. Spectra 26, 1017-1037.

    Caveats and limitations:

    The current model is the result of the above mentioned workshop and
    reflects the best available information. However, the current model
    has a number of issues listed below and is expected to evolve further
    over time.

    1 - The model is based on limited number of observed fatality
        rates during 4 past fatal events.

    2 - The model clearly over-predicts the fatality rates at
        intensities higher than VIII.

    3 - The model only estimates the expected fatality rate for a given
        intensity level; however the associated uncertainty for the proposed
        model is not addressed.

    4 - There are few known mistakes in developing the current model:
        - rounding MMI values to the nearest 0.5,
        - Implementing Finite-Fault models of candidate events, and
        - consistency between selected GMPEs with those in use by BMKG.
          These issues will be addressed by ITB team in the final report.

    Note: Because of these caveats, decisions should not be made solely on
    the information presented here and should always be verified by ground
    truthing and other reliable information sources.

    :returns: Fatality rate.
    :rtype: dic
    """
    # As per email discussion with Ole, Trevor, Hadi, mmi < 4 will have
    # a fatality rate of 0 - Tim
    mmi_range = range(2, 11)
    # Model coefficients
    x = 0.62275231
    y = 8.03314466
    fatality_rate = {
        mmi: 0 if mmi < 4 else 10 ** (x * mmi - y) for mmi in mmi_range}
    return fatality_rate


def pager_fatality_rates():
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

    :returns: Fatality rate calculated as:
        lognorm.cdf(mmi, shape=Beta, scale=Theta)
    :rtype: dic
    """
    # Model coefficients
    theta = 13.249
    beta = 0.151
    mmi_range = range(2, 11)
    fatality_rate = {mmi: 0 if mmi < 4 else log_normal_cdf(
        mmi, median=theta, sigma=beta) for mmi in mmi_range}
    return fatality_rate


def itb_bayesian_fatality_rates():
    """ITB fatality model based on a Bayesian approach.

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hyeuk Ryu, Geoscience Australia.

    Reference:

    An Empirical Fatality Model for Indonesia Based on a Bayesian Approach
    by W. Sengara, M. Suarjana, M.A. Yulman, H. Ghasemi, and H. Ryu
    submitted for Journal of the Geological Society

    :returns: Fatality rates as medians
        It comes worden_berngamma_log_fat_rate_inasafe_10.csv in InaSAFE 3.
    :rtype: dict
    """
    fatality_rate = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0,
        6: 3.41733122522e-05,
        7: 0.000387804494226,
        8: 0.001851451786,
        9: 0.00787294191661,
        10: 0.0314512157378,
    }
    return fatality_rate

EARTHQUAKE_FUNCTIONS = (
    {
        'key': 'itb_bayesian_fatality_rates',
        'name': tr('ITB bayesian fatality rates'),
        'description': tr(
            'ITB fatality model based on a Bayesian approach. This model was '
            'developed by Institut Teknologi Bandung (ITB) and implemented by '
            'Dr. Hyeuk Ryu, Geoscience Australia.'
        ),
        'notes': tr(
            'The ITB bayesian fatality model is based on the ITB fatality '
            'model and uses Indonesian fatality data'),
        'citations': [
            {
                'text': tr(
                    'An Empirical Fatality Model for Indonesia Based on a '
                    'Bayesian Approach by W. Sengara, M. Suarjana, '
                    'M.A. Yulman, H. Ghasemi, and H. Ryu. submitted for '
                    'Journal of the Geological Society.'),
                'link': ''
            }
        ],
        'fatality_rates': itb_bayesian_fatality_rates
    }, {
        'key': 'itb_fatality_rates',
        'name': tr('ITB fatality rates'),
        'description': tr(
            'ITB fatality model is modified from the USGS Pager model. This '
            'model was developed by Institut Teknologi Bandung (ITB) and '
            'implemented by Dr. Hadi Ghasemi, Geoscience Australia.'
        ),
        'notes': tr(
            'The ITB fatality model is based on the USGS Pager model and '
            'modified to use a different source.'),
        'citations': [
            {
                'text': tr(
                    'Indonesian Earthquake Building-Damage and Fatality '
                    'Models and Post Disaster Survey Guidelines Development, '
                    'Bali, 27-28 February 2012, 54pp.,'),
                'link': ''
            }
        ],
        'fatality_rates': itb_fatality_rates
    }, {
        'key': 'pager_fatality_rates',
        'name': tr('Pager fatality rates'),
        'description': tr(
            'USGS Pager fatality estimation model. This model was developed '
            'by Institut Teknologi Bandung (ITB) and implemented by Dr. Hyeuk '
            'Ryu, Geoscience Australia.'
        ),
        'notes': tr(
            'The USGS Pager fatality model using Indonesian country '
            'coefficients.'),
        'citations': [
            {
                'text': tr(
                    'Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). '
                    'Estimating casualties for large worldwide earthquakes '
                    'using an empirical approach. U.S. Geological Survey '
                    'Open-File Report 2009-1136.'),
                'link': u'https://pubs.usgs.gov/of/2009/1136/pdf/'
            }
        ],
        'fatality_rates': pager_fatality_rates
    }
)
