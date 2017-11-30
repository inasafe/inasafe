# coding=utf-8

import logging
import unittest

from safe.definitions.units import (
    unit_millimetres, unit_metres, unit_kilometres, unit_knots)
from safe.utilities.rounding import (
    rounding_full,
    denomination,
    add_separators,
    convert_unit,
    fatalities_range,
)
from safe.utilities.i18n import locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class TestCore(unittest.TestCase):

    """Tests for rounding."""

    def test_rounding_population(self):
        """Test for rounding population function."""
        self.assertEqual(rounding_full(989, True)[0], 990)
        self.assertEqual(rounding_full(991, True)[0], 1000)
        self.assertEqual(rounding_full(8888, True)[0], 8900)
        self.assertEqual(rounding_full(9888888, True)[0], 9889000)

    def test_rounding_not_population(self):
        """Test for rounding not population numbers function."""
        self.assertEqual(rounding_full(989, False)[0], 989)
        self.assertEqual(rounding_full(991, False)[0], 991)
        self.assertEqual(rounding_full(8888, False)[0], 8900)
        self.assertEqual(rounding_full(9888888, False)[0], 9889000)

    def test_format_int(self):
        """Test formatting integer."""
        lang = locale()

        number = 10000000
        formatted_int = add_separators(number)
        if lang == 'id':
            expected_str = '10.000.000'
        else:
            expected_str = '10,000,000'
        self.assertEqual(expected_str, formatted_int)

        number = 1234
        formatted_int = add_separators(number)
        if lang == 'id':
            expected_str = '1.234'
        else:
            expected_str = '1,234'
        self.assertEqual(expected_str, formatted_int)

    def test_convert_unit(self):
        """Test we can convert a unit."""
        self.assertEqual(1000, convert_unit(1, unit_kilometres, unit_metres))
        self.assertEqual(0.001, convert_unit(1, unit_metres, unit_kilometres))
        self.assertEqual(
            1000000, convert_unit(1, unit_kilometres, unit_millimetres))
        self.assertIsNone(convert_unit(1, unit_kilometres, unit_knots))

    def test_fatalities_range(self):
        """Test we can create a fatality range."""
        self.assertEqual('0 - 100', fatalities_range(0))
        self.assertEqual('0 - 100', fatalities_range(50))
        self.assertEqual('0 - 100', fatalities_range(100))
        self.assertEqual('1,000 - 10,000', fatalities_range(8000))
        self.assertEqual('10,000 - 100,000', fatalities_range(18000))
        self.assertEqual('> 100,000', fatalities_range(101000))

    def test_denomination(self):
        """Test name number."""
        result = denomination(None)
        for item in result:
            self.assertIsNone(item)

        result = denomination(-11)
        self.assertEqual(-1.1, result[0])
        self.assertEqual('unit_tens', result[1]['key'])

        result = denomination(-1)
        self.assertEqual(-1, result[0])
        self.assertEqual('unit_ones', result[1]['key'])

        result = denomination(1)
        self.assertEqual(1, result[0])
        self.assertEqual('unit_ones', result[1]['key'])

        result = denomination(11)
        self.assertEqual(1.1, result[0])
        self.assertEqual('unit_tens', result[1]['key'])

        result = denomination(99)
        self.assertEqual(9.9, result[0])
        self.assertEqual('unit_tens', result[1]['key'])

        result = denomination(100)
        self.assertEqual(1, result[0])
        self.assertEqual('unit_hundreds', result[1]['key'])

        result = denomination(101)
        self.assertEqual(1.01, result[0])
        self.assertEqual('unit_hundreds', result[1]['key'])

        result = denomination(1001)
        self.assertEqual(1.001, result[0])
        self.assertEqual('unit_thousand', result[1]['key'])

        result = denomination(10000)
        self.assertEqual(10, result[0])
        self.assertEqual('unit_thousand', result[1]['key'])

        result = denomination(101000)
        self.assertEqual(101, result[0])
        self.assertEqual('unit_thousand', result[1]['key'])

        result = denomination(100000000000000)
        self.assertEqual(100.0, result[0])
        self.assertEqual('unit_trillion', result[1]['key'])

        # test denomination with minimal value parameter

        result = denomination(1, 1000)
        self.assertEqual(1, result[0])
        self.assertIsNone(result[1])

        result = denomination(100, 1000)
        self.assertEqual(100, result[0])
        self.assertIsNone(result[1])

        result = denomination(1000, 1000)
        self.assertEqual(1, result[0])
        self.assertEqual('unit_thousand', result[1]['key'])


if __name__ == '__main__':
    unittest.main()
