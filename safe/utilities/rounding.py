# coding=utf-8
"""Rounding and number formatting."""


from math import ceil

from safe.definitions.units import unit_mapping
from safe.utilities.i18n import locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def format_number(x, enable_rounding=True):
    """Format a number according to the standards.

    :param x: A number to be formatted in a locale friendly way.
    :type x: int

    :param enable_rounding: Flag to enable a population rounding.
    :type enable_rounding: bool

    :returns: A locale friendly formatted string e.g. 1,000,0000.00
        representing the original x. If a ValueError exception occurs,
        x is simply returned.
    :rtype: basestring
    """
    if enable_rounding:
        x = population_rounding(x)

    number = add_separators(x)
    return number


def add_separators(x):
    """Format integer with separator between thousands.

    :param x: A number to be formatted in a locale friendly way.
    :type x: int

    :returns: A locale friendly formatted string e.g. 1,000,0000.00
        representing the original x. If a ValueError exception occurs,
        x is simply returned.
    :rtype: basestring


    From http://
    stackoverflow.com/questions/5513615/add-thousands-separators-to-a-number

    Instead use this:
    http://docs.python.org/library/string.html#formatspec
    """
    try:
        s = '{0:,}'.format(x)
        # s = '{0:n}'.format(x)  # n means locale aware (read up on this)
    # see issue #526
    except ValueError:
        return x

    # Quick solution for the moment
    if locale() in ['id', 'fr']:
        # Replace commas with the correct thousand separator.
        s = s.replace(',', thousand_separator())
    return s


def decimal_separator():
    """Return decimal separator according to the locale.

    :return: The decimal separator.
    :rtype: basestring
    """
    lang = locale()

    if lang in ['id', 'fr']:
        return ','

    else:
        return '.'


def thousand_separator():
    """Return thousand separator according to the locale.

    :return: The thousand separator.
    :rtype: basestring
    """
    lang = locale()

    if lang in ['id']:
        return '.'

    elif lang in ['fr']:
        return ' '

    else:
        return ','


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
    if number < 1000:
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


def convert_unit(number, input_unit, expected_unit):
    """A helper to convert the unit.

    :param number: The number to update.
    :type number: int

    :param input_unit: The unit of the number.
    :type input_unit: safe.definitions.units

    :param expected_unit: The expected output unit.
    :type expected_unit: safe.definitions.units

    :return: The new number in the expected unit.
    :rtype: int
    """
    for mapping in unit_mapping:
        if input_unit == mapping[0] and expected_unit == mapping[1]:
            return number * mapping[2]
        if input_unit == mapping[1] and expected_unit == mapping[0]:
            return number / mapping[2]

    return None
