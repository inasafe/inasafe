# coding=utf-8

"""Rounding and number formatting."""

from decimal import Decimal
from math import ceil, log

from safe.definitions.units import unit_mapping, nominal_mapping
from safe.utilities.i18n import locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def format_number(
        x, use_rounding=True, is_population=False, coefficient=1):
    """Format a number according to the standards.

    :param x: A number to be formatted in a locale friendly way.
    :type x: int

    :param use_rounding: Flag to enable a rounding.
    :type use_rounding: bool

    :param is_population: Flag if the number is population. It needs to be
        used with enable_rounding.
    :type is_population: bool

    :param coefficient: Divide the result after the rounding.
    :type coefficient:float

    :returns: A locale friendly formatted string e.g. 1,000,0000.00
        representing the original x. If a ValueError exception occurs,
        x is simply returned.
    :rtype: basestring
    """
    if use_rounding:
        x = rounding(x, is_population)

    x /= coefficient

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
        use_rounding=False,
        use_population_rounding=False):
    """Tries to convert and round the number.

    Rounded using population rounding rule.

    :param number: number represented as string or float
    :type number: str, float

    :param use_rounding: flag to enable rounding
    :type use_rounding: bool

    :param use_population_rounding: flag to enable population rounding scheme
    :type use_population_rounding: bool

    :return: rounded number
    """
    decimal_number = float(number)
    rounded_number = int(ceil(decimal_number))
    if use_rounding and use_population_rounding:
        # if uses population rounding
        return rounding(rounded_number, use_population_rounding)
    elif use_rounding:
        return rounded_number

    return decimal_number


def rounding_full(number, is_population=False):
    """This function performs a rigorous rounding.

    :param number: The amount to round.
    :type number: int, float

    :param is_population: If we should use the population rounding rule, #4062.
    :type is_population: bool

    :returns: result and rounding bracket.
    :rtype: (int, int)
    """
    if number < 1000 and not is_population:
        rounding_number = 1  # See ticket #4062
    elif number < 1000 and is_population:
        rounding_number = 10
    elif number < 100000:
        rounding_number = 100
    else:
        rounding_number = 1000
    number = int(rounding_number * ceil(float(number) / rounding_number))
    return number, rounding_number


def rounding(number, is_population=False):
    """A shorthand for rounding_full(number)[0].

    :param number: The amount to round.
    :type number: int, float

    :param is_population: If we should use the population rounding rule, #4062.
    :type is_population: bool

    :returns: result and rounding bracket.
    :rtype: int
    """
    return rounding_full(number, is_population)[0]


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


def coefficient_between_units(unit_a, unit_b):
    """A helper to get the coefficient between two units.

    :param unit_a: The first unit.
    :type unit_a: safe.definitions.units

    :param unit_b: The second unit.
    :type unit_b: safe.definitions.units

    :return: The coefficient between these two units.
    :rtype: float
    """
    for mapping in unit_mapping:
        if unit_a == mapping[0] and unit_b == mapping[1]:
            return mapping[2]
        if unit_a == mapping[1] and unit_b == mapping[0]:
            return 1 / mapping[2]

    return None


def fatalities_range(number):
    """A helper to return fatalities as a range of number.

    See https://github.com/inasafe/inasafe/issues/3666#issuecomment-283565297

    :param number: The exact number. Will be converted as a range.
    :type number: int, float

    :return: The range of the number.
    :rtype: str
    """
    range_format = '{min_range} - {max_range}'
    more_than_format = '> {min_range}'
    ranges = [
        [0, 100],
        [100, 1000],
        [1000, 10000],
        [10000, 100000],
        [100000, float('inf')]
    ]
    for r in ranges:
        min_range = r[0]
        max_range = r[1]

        if max_range == float('inf'):
            return more_than_format.format(
                min_range=add_separators(min_range))
        elif min_range <= number <= max_range:
            return range_format.format(
                min_range=add_separators(min_range),
                max_range=add_separators(max_range))


def html_scientific_notation_rate(rate):
    """Helper for convert decimal rate using scientific notation.

    For example we want to show the very detail value of fatality rate
    because it might be a very small number.

    :param rate: Rate value
    :type rate: float

    :return: Rate value with html tag to show the exponent
    :rtype: str
    """
    precision = '%.3f'
    if rate * 100 > 0:
        decimal_rate = Decimal(precision % (rate * 100))
        if decimal_rate == Decimal((precision % 0)):
            decimal_rate = Decimal(str(rate * 100))
    else:
        decimal_rate = Decimal(str(rate * 100))
    if decimal_rate.as_tuple().exponent >= -3:
        rate_percentage = str(decimal_rate)
    else:
        rate = '%.2E' % decimal_rate
        html_rate = rate.split('E')
        # we use html tag to show exponent
        html_rate[1] = '10<sup>{exponent}</sup>'.format(
            exponent=html_rate[1])
        html_rate.insert(1, 'x')
        rate_percentage = ''.join(html_rate)
    return rate_percentage


def denomination(value, min_nominal=None):
    """Return the denomination of a number.

    :param value: The value.
    :type value: int

    :param min_nominal: Minimum value of denomination eg: 1000, 100.
    :type min_nominal: int

    :return: The new value and the denomination as a unit definition.
    :rtype: list(int, safe.unit.definition)
    """
    if value is None:
        return None

    if not value:
        return value, None

    if abs(value) == list(nominal_mapping.keys())[0] and not min_nominal:
        return 1 * value, nominal_mapping[list(nominal_mapping.keys())[0]]

    # we need minimum value of denomination because we don't want to show
    # '2 ones', '3 tens', etc.
    index = 0
    if min_nominal:
        index = int(ceil(log(min_nominal, 10)))

    iterator = list(zip(
        list(nominal_mapping.keys())[index:], list(nominal_mapping.keys())[index + 1:]))
    for min_value, max_value in iterator:

        if min_value <= abs(value) < max_value:
            return float(value) / min_value, nominal_mapping[min_value]
        elif abs(value) < min_value:
            return float(value), None

    max_value = list(nominal_mapping.keys())[-1]
    new_value = float(value) / max_value
    new_unit = nominal_mapping[list(nominal_mapping.keys())[-1]]
    return new_value, new_unit
