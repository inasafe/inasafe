# coding=utf-8

"""Definitions about earthquake."""

import numpy

from safe.utilities.i18n import tr
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def earthquake_fatality_rate(hazard_level):
    """Earthquake fatality ratio for a given hazard level.

    It reads the QGIS QSettings to know what is the default earthquake
    function.

    :param hazard_level: The hazard level.
    :type hazard_level: int

    :return: The fatality rate.
    :rtype: float
    """
    earthquake_function = setting(
        'earthquake_function', EARTHQUAKE_FUNCTIONS[0]['key'], str)
    ratio = 0
    for model in EARTHQUAKE_FUNCTIONS:
        if model['key'] == earthquake_function:
            eq_function = model['fatality_rates']
            ratio = eq_function().get(hazard_level)
    return ratio


def itb_fatality_rates():
    """Indonesian Earthquake Fatality Model.

    :returns: Fatality rate.
    :rtype: dic
    """
    # As per email discussion with Ole, Trevor, Hadi, mmi < 4 will have
    # a fatality rate of 0 - Tim
    mmi_range = list(range(2, 11))
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
    mmi_range = list(range(2, 11))
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
        'name': tr('ITB bayesian fatality model'),
        'description': tr(
            'ITB fatality model based on a Bayesian approach. This model was '
            'developed by Institut Teknologi Bandung (ITB) and implemented by '
            'Dr. Hyeuk Ryu, Geoscience Australia.'
        ),
        'notes': [
            tr(
                'The ITB bayesian fatality model, from Institut Teknologi '
                'Bandung 2012, is based on the ITB fatality model and uses '
                'Indonesian fatality data'
            ),
        ],
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
        'name': tr('ITB fatality model'),
        'description': tr(
            'ITB fatality model is modified from the USGS Pager model. This '
            'model was developed by Institut Teknologi Bandung (ITB) and '
            'implemented by Dr. Hadi Ghasemi, Geoscience Australia.'),
        'notes': [
            tr('Algorithm:'),
            tr(
                'In this study, the same functional form as Allen (2009) is '
                'adopted to express fatality rate as a function of intensity '
                '(see Eq. 10 in the report). The Matlab built-in function '
                '(fminsearch) for  Nelder-Mead algorithm was used to estimate '
                'the model parameters. The objective function (L2G norm) '
                'that is minimised during the optimisation is the same as '
                'the one used by Jaiswal et al. (2010).'),
            tr(
                'The coefficients used in the indonesian model are '
                'x=0.62275231, y=8.03314466, zeta=2.15'),
            tr(
                'Caveats and limitations:'),
            tr(
                'The current model is the result of the above mentioned '
                'workshop and reflects the best available information. '
                'However, the current model has a number of issues listed '
                'below and is expected to evolve further over time.'),
            tr(
                '1 - The model is based on limited number of observed '
                'fatality rates during 4 past fatal events.'),
            tr(
                '2 - The model clearly over-predicts the fatality rates at '
                'intensities higher than VIII.'),
            tr(
                '3 - The model only estimates the expected fatality rate for '
                'a given intensity level; however the associated uncertainty '
                'for the proposed model is not addressed.'),
            tr(
                '4 - There are few known mistakes in developing the current '
                'model:'),
            tr(
                '- rounding MMI values to the nearest 0.5,'),
            tr(
                '- Implementing Finite-Fault models of candidate events, '
                'and'),
            tr(
                '- consistency between selected GMPEs with those in use by ',
                'BMKG. These issues will be addressed by ITB team in the '
                'final report.'),
            tr(
                'Note: Because of these caveats, decisions should not be '
                'made solely on the information presented here and should '
                'always be verified by ground truthing and other reliable '
                'information sources.')
        ],
        'citations': [
            {
                'text': tr(
                    'Indonesian Earthquake Building-Damage and Fatality '
                    'Models and Post Disaster Survey Guidelines Development, '
                    'Bali, 27-28 February 2012, 54pp.,'),
                'link': ''
            },
            {
                'text': tr(
                    'Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D., '
                    'Hotovec, A. J., Lin, K., and Hearne, M., 2009. An Atlas '
                    'of ShakeMaps and population exposure catalog for '
                    'earthquake loss modeling, Bull. Earthq. Eng. 7, 701-718. '
                    'Jaiswal, K., and Wald, D., 2010. An empirical model for '
                    'global earthquake fatality estimation, Earthq. Spectra '
                    '26, 1017-1037.'),
                'link': ''
            }
        ],
        'fatality_rates': itb_fatality_rates
    }, {
        'key': 'pager_fatality_rates',
        'name': tr('Pager fatality model'),
        'description': tr(
            'USGS Pager fatality estimation model. This model was developed '
            'by Institut Teknologi Bandung (ITB) and implemented by Dr. Hyeuk '
            'Ryu, Geoscience Australia.'
        ),
        'notes': [
            tr(
                'The USGS Population Vulnerability Pager fatality model using '
                'Indonesian country coefficients.'
            ),
        ],
        'citations': [
            {
                'text': tr(
                    'Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). '
                    'Estimating casualties for large worldwide earthquakes '
                    'using an empirical approach. U.S. Geological Survey '
                    'Open-File Report 2009-1136.'),
                'link': 'https://pubs.usgs.gov/of/2009/1136/pdf/'
            }
        ],
        'fatality_rates': pager_fatality_rates
    }
)


def normal_cdf(x, mu=0, sigma=1):
    """Cumulative Normal Distribution Function.

    :param x: scalar or array of real numbers.
    :type x: numpy.ndarray, float

    :param mu: Mean value. Default 0.
    :type mu: float, numpy.ndarray

    :param sigma: Standard deviation. Default 1.
    :type sigma: float

    :returns: An approximation of the cdf of the normal.
    :rtype: numpy.ndarray

    Note:
        CDF of the normal distribution is defined as
        \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

        Source: http://en.wikipedia.org/wiki/Normal_distribution
    """
    arg = (x - mu) / (sigma * numpy.sqrt(2))
    res = (1 + erf(arg)) / 2
    return res


def log_normal_cdf(x, median=1, sigma=1):
    """Cumulative Log Normal Distribution Function.

    :param x: scalar or array of real numbers.
    :type x: numpy.ndarray, float

    :param median: Median (exp(mean of log(x)). Default 1.
    :type median: float

    :param sigma: Log normal standard deviation. Default 1.
    :type sigma: float

    :returns: An approximation of the cdf of the normal.
    :rtype: numpy.ndarray

    .. note::
        CDF of the normal distribution is defined as
        \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

        Source: http://en.wikipedia.org/wiki/Normal_distribution
    """
    return normal_cdf(numpy.log(x), mu=numpy.log(median), sigma=sigma)


# noinspection PyUnresolvedReferences
def erf(z):
    """Approximation to ERF.

    :param z: Input array or scalar to perform erf on.
    :type z: numpy.ndarray, float

    :returns: The approximate error.
    :rtype: numpy.ndarray, float

    Note:
        from:
        http://www.cs.princeton.edu/introcs/21function/ErrorFunction.java.html
        Implements the Gauss error function.
        erf(z) = 2 / sqrt(pi) * integral(exp(-t*t), t = 0..z)

        Fractional error in math formula less than 1.2 * 10 ^ -7.
        although subject to catastrophic cancellation when z in very close to 0
        from Chebyshev fitting formula for erf(z) from Numerical Recipes, 6.2

        Source:
        http://stackoverflow.com/questions/457408/
        is-there-an-easily-available-implementation-of-erf-for-python
    """
    # Input check
    try:
        len(z)
    except TypeError:
        scalar = True
        z = [z]
    else:
        scalar = False

    z = numpy.array(z)

    # Begin algorithm
    t = 1.0 / (1.0 + 0.5 * numpy.abs(z))

    # Use Horner's method
    ans = 1 - t * numpy.exp(
        -z * z - 1.26551223 + t * (
            1.00002368 + t * (0.37409196 + t * (
                0.09678418 + t * (
                    -0.18628806 + t * (
                        0.27886807 + t * (
                            -1.13520398 + t * (
                                1.48851587 + t * (
                                    -0.82215223 + t * 0.17087277)))))))))

    neg = (z < 0.0)  # Mask for negative input values
    ans[neg] = -ans[neg]

    if scalar:
        return ans[0]
    else:
        return ans


def current_earthquake_model_name():
    """Human friendly name for the currently active earthquake fatality model.

    :returns: Name of the current EQ fatality model as defined in users
        settings.
    """
    default_earthquake_function = setting(
        'earthquake_function', EARTHQUAKE_FUNCTIONS[0]['key'], str)
    current_function = None
    for model in EARTHQUAKE_FUNCTIONS:
        if model['key'] == default_earthquake_function:
            current_function = model['name']
    return current_function
