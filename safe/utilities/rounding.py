from math import ceil

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def round_affected_number(
        number,
        enable_rounding=False,
        use_population_rounding=False):
    """Tries to convert and round the number.

    Rounded using population rounding rule.

    :param number: number represented as string or float
    :type number: str, float

    :param enable_rounding: flag to enable rounding
    :type enable_rounding: bool

    :param use_population_rounding: flag to enable population rounding scheme
    :type use_population_rounding: bool

    :return: rounded number
    """
    decimal_number = float(number)
    rounded_number = int(ceil(decimal_number))
    if enable_rounding and use_population_rounding:
        # if uses population rounding
        return population_rounding(rounded_number)
    elif enable_rounding:
        return rounded_number

    return decimal_number


def population_rounding_full(number):
    """This function performs a rigorous population rounding.

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: (int, int)
    """
    if number < 10:
        rounding = 1
    elif number < 1000:
        rounding = 10
    elif number < 100000:
        rounding = 100
    else:
        rounding = 1000
    number = int(rounding * ceil(1.0 * number / rounding))
    return number, rounding


def population_rounding(number):
    """A shorthand for population_rounding_full(number)[0].

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: int
    """
    return population_rounding_full(number)[0]
