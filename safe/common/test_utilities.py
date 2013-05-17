"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Utilities Tests implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__version__ = '1.1.1'
__revision__ = '$Format:%H$'
__date__ = '17/04/20113'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
from utilities import (
    get_significant_decimal,
    humanize_class,
    format_decimal,
    create_classes,
    create_label)


def print_class(my_array, my_result_class, my_expected):
    """Print my_array, my_result, my_expected in nice format
    """
    print 'Original Array'
    for i in xrange(len(my_array[1:])):
        print my_array[i], ' - ', my_array[i + 1]
    print 'Classes result'
    for result in my_result_class:
        print result[0], ' - ', result[1]
    print 'Expect result'
    for expect in my_expected:
        print expect[0], ' - ', expect[1]


class UtilitiesTest(unittest.TestCase):
    def test_humanize_class(self):
        """Test humanize class
        First class interval < 1
        Interval > 1
        """
        my_array = [0.1, 1.2, 2.3, 3.4, 4.5]
        my_result_class = humanize_class(my_array)
        my_expected_class = [('0', '0.1'),
                             ('0.1', '1.2'),
                             ('1.2', '2.3'),
                             ('2.3', '3.4'),
                             ('3.4', '4.5')]
        print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
        assert my_result_class == my_expected_class, my_msg

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
        print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
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
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
        print_class(my_array, my_result_class, my_expected_class)
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
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
        print_class(my_array, my_result_class, my_expected_class)
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
        print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
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
        print_class(my_array, my_result_class, my_expected_class)
        my_msg = 'got: ' + str(my_result_class)
        my_msg += ' expect: ' + str(my_expected_class)
        assert my_result_class == my_expected_class, my_msg

    def test_get_significant_decimal(self):
        """Test Get Significatn Decimal
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
        interval = 0.9912
        my_number = 10
        my_result = format_decimal(interval, my_number)
        print my_result
        assert my_result == '10', 'Format decimal is not valid %s' % my_result
        my_number = 10.0121034435
        my_result = format_decimal(interval, my_number)
        print my_result
        assert my_result == '10.012', \
            'Format decimal is not valid %s' % my_result
        my_number = float('nan')
        my_result = format_decimal(interval, my_number)
        print my_result
        assert my_result == 'nan', \
            'Format decimal is not valid %s' % my_result

    def test_create_classes(self):
        """Test create_classes.
        """
        my_list = [0, 1, 4, 2, 9, 2, float('nan')]
        num_classes = 2
        my_expected = [4.5, 9]
        my_result = create_classes(my_list, num_classes)
        assert my_result == my_expected, ' %s is not same with %s' % (
            my_result, my_expected)

        my_list = [1, 4, 2, 9, 2, float('nan')]
        num_classes = 2
        my_expected = [1, 9]
        my_result = create_classes(my_list, num_classes)
        assert my_result == my_expected, ' %s is not same with %s' % (
            my_result, my_expected)

    def test_create_label(self):
        """Test create label.
        """
        my_tuple = ('1', '2')
        my_extra_label = 'Low damage'
        my_result = create_label(my_tuple)
        my_expected = '[1 - 2]'
        assert my_result == my_expected, ' %s is not same with %s' % (
            my_result, my_expected)
        my_result = create_label(my_tuple, my_extra_label)
        my_expected = '[1 - 2] Low damage'
        assert my_result == my_expected, ' %s is not same with %s' % (
            my_result, my_expected)


if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
