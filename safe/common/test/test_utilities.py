# coding=utf-8

"""Test for Common Utilities."""


import unittest
import os

from qgis.core import QgsCoordinateReferenceSystem

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app
from safe.common.utilities import (
    get_significant_decimal,
    humanize_class,
    format_decimal,
    create_label,
    get_utm_epsg,
    temp_dir,
    log_file_path,
    romanise,
    humanize_file_size,
    add_to_list,
    color_ramp)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)


def print_class(array, result_class, expected_result):
    """Print array, result_class, expected_result in nice format.

    :param array: The original array.
    :type array: list

    :param result_class: The class result.
    :type result_class: list

    :param expected_result: The expected result.
    :type expected_result: list

    """
    print('Original Array')
    for i in range(len(array[1:])):
        print((array[i], ' - ', array[i + 1]))
    print('Classes result')
    for result in result_class:
        print((result[0], ' - ', result[1]))
    print('Expect result')
    for expect in expected_result:
        print((expect[0], ' - ', expect[1]))


class TestUtilities(unittest.TestCase):

    def test_humanize_class(self):
        """Test humanize class
        First class interval < 1
        Interval > 1
        """
        array = [0.1, 1.2, 2.3, 3.4, 4.5]
        result_class = humanize_class(array)
        expected_class = [
            ('0', '0.1'),
            ('0.1', '1.2'),
            ('1.2', '2.3'),
            ('2.3', '3.4'),
            ('3.4', '4.5')
        ]
        # print_class(array, result_class, expected_class)
        self.assertEqual(result_class, expected_class)

    def test_humanize_class2(self):
        """Test humanize class 2
        First class interval > 1
        Interval > 1
        """
        my_array = [1.1, 5754.1, 11507.1]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '1'),
                             ('1', '5,754'),
                             ('5,754', '11,507')]
        # print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: %s expect: %s' % (my_result_class, my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_humanize_class3(self):
        """Test humanize class 3
        First class interval < 1
        Interval < 1
        """
        my_array = [0.1, 0.5, 0.9]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '0.1'),
                             ('0.1', '0.5'),
                             ('0.5', '0.9')]
        my_msg = 'got: %s expect: %s' % (my_result_class, my_expected_class)
        # print_class(my_array, my_result_class, my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_humanize_class4(self):
        """Test humanize class 4
        First class interval > 1
        Interval < 1
        """
        my_array = [7.1, 7.5, 7.9]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '7.1'),
                             ('7.1', '7.5'),
                             ('7.5', '7.9')]
        my_msg = 'got: %s expect: %s' % (my_result_class, my_expected_class)
        # print_class(my_array, my_result_class, my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_humanize_class5(self):
        """Test humanize class 5
        First class interval < 1
        Interval > 1
        """
        my_array = [6.1, 7.2, 8.3, 9.4, 10.5]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '6'),
                             ('6', '7'),
                             ('7', '8'),
                             ('8', '9'),
                             ('9', '11')]
        # print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: %s expect: %s' % (my_result_class, my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_humanize_class6(self):
        """Test humanize class 5
            First class interval < 1
            Interval > 1
            """
        my_array = [0, 6.1, 7.2, 8.3, 9.4, 10.5]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '6'),
                             ('6', '7'),
                             ('7', '8'),
                             ('8', '9'),
                             ('9', '11')]
        # print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: %s expect: %s' % (my_result_class, my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_get_significant_decimal(self):
        """Test Get Significant Decimal
        """
        my_decimal = 10.1212
        my_result = get_significant_decimal(my_decimal)
        assert my_result == 10.121, 'Decimal point not valid %s' % my_result
        my_decimal = float('nan')
        my_result = get_significant_decimal(my_decimal)
        assert my_result != my_result, 'Decimal point not valid %s' % my_result
        my_decimal = 0.00001212343434
        my_result = get_significant_decimal(my_decimal)
        assert my_result != 0.0000121, 'Decimal point not valid %s' % my_result

    def test_format_decimal(self):
        """Test Format Decimal
        """
        os.environ['LANG'] = 'en'
        interval = 0.9912
        my_number = 10
        my_result = format_decimal(interval, my_number)
        # print my_result
        assert my_result == '10', 'Format decimal is not valid %s' % my_result
        my_number = 10.0121034435
        my_result = format_decimal(interval, my_number)
        # print my_result
        assert my_result == '10.012', \
            'Format decimal is not valid %s' % my_result
        my_number = float('nan')
        my_result = format_decimal(interval, my_number)
        # print my_result
        assert my_result == 'nan', \
            'Format decimal is not valid %s' % my_result

        my_number = float('10000.09')
        my_result = format_decimal(interval, my_number)
        # print my_result
        assert my_result == '10,000.09', \
            'Format decimal is not valid %s' % my_result

    def test_create_label(self):
        """Test create label.
        """
        the_tuple = ('1', '2')
        extra_label = 'Low damage'
        result = create_label(the_tuple)
        expected = '[1 - 2]'
        self.assertEqual(result, expected)
        result = create_label(the_tuple, extra_label)
        expected = '[1 - 2] Low damage'
        self.assertEqual(result, expected)

    def test_get_utm_epsg(self):
        """Test we can get correct epsg code."""
        # North semisphere in geographic coordinates:
        self.assertEqual(get_utm_epsg(-178, 10), 32601)
        self.assertEqual(get_utm_epsg(178, 20), 32660)
        self.assertEqual(get_utm_epsg(-3, 30), 32630)
        # South semisphere in geographic coordinates:
        self.assertEqual(get_utm_epsg(-178, -10), 32701)
        self.assertEqual(get_utm_epsg(178, -20), 32760)
        self.assertEqual(get_utm_epsg(-3, -30), 32730)

        # North semisphere not in geographic coordinates:
        epsg = QgsCoordinateReferenceSystem('EPSG:2154')
        self.assertEqual(get_utm_epsg(573593, 6330659, epsg), 32631)

    def test_log_file_path(self):
        """Test the log_file_path returns correct path."""
        log_temp_dir = temp_dir('logs')
        actual_path = os.path.join(log_temp_dir, 'inasafe.log')
        self.assertEqual(actual_path, log_file_path())

    def test_romanise(self):
        """Test we can convert MMI values to float."""
        values = list(range(2, 10))
        expected_result = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        result = []
        for value in values:
            result.append(romanise(value))
        self.assertEqual(result, expected_result)

    def test_humanize_size(self):
        """Test we can convert size values to human readable size."""
        values = [1023, 1024, 1048575, 1048576, 1604321.28]
        expected_result = [
            '1023.0 bytes', '1.0 KB', '1024.0 KB', '1.0 MB', '1.5 MB']

        result = []
        for value in values:
            result.append(humanize_file_size(value))
        self.assertEqual(result, expected_result, )

    def test_add_to_list(self):
        """Test for add_to_list function
        """
        list_original = ['a', 'b', ['a'], {'a': 'b'}]
        list_a = ['a', 'b', ['a'], {'a': 'b'}]
        # add same immutable element
        list_b = add_to_list(list_a, 'b')
        assert list_b == list_original
        # add list
        list_b = add_to_list(list_a, ['a'])
        assert list_b == list_original
        # add same mutable element
        list_b = add_to_list(list_a, {'a': 'b'})
        assert list_b == list_original
        # add new mutable element
        list_b = add_to_list(list_a, 'c')
        assert len(list_b) == (len(list_original) + 1)
        assert list_b[-1] == 'c'

    def test_color_ramp(self):
        """Test for color_ramp function."""
        number_of_colours = 1
        expected_colors = ['#ff0000']
        colors = color_ramp(number_of_colours)
        self.assertEqual(colors, expected_colors)

        number_of_colours = 2
        expected_colors = ['#ff0000', '#00ff00']
        colors = color_ramp(number_of_colours)
        self.assertEqual(colors, expected_colors)

        number_of_colours = 3
        expected_colors = ['#ff0000', '#feff00', '#00ff00']
        colors = color_ramp(number_of_colours)
        self.assertEqual(colors, expected_colors)

        number_of_colours = 4
        expected_colors = ['#ff0000', '#ffaa00', '#a9ff00', '#00ff00']
        colors = color_ramp(number_of_colours)
        self.assertEqual(colors, expected_colors)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestUtilities)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
