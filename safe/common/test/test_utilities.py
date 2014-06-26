# coding=utf-8
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
__date__ = '05/05/2014'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
import os
from safe.common.utilities import (
    get_significant_decimal,
    humanize_class,
    format_decimal,
    create_classes,
    create_label,
    get_thousand_separator,
    get_decimal_separator,
    get_utm_epsg,
    get_non_conflicting_attribute_name,
    temp_dir,
    log_file_path,
    romanise)


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

        my_number = float('10000.09')
        my_result = format_decimal(interval, my_number)
        print my_result
        assert my_result == '10,000.09', \
            'Format decimal is not valid %s' % my_result

    def test_separator(self):
        """Test decimal and thousand separator
        """
        os.environ['LANG'] = 'en'
        assert ',' == get_thousand_separator()
        assert '.' == get_decimal_separator()
        os.environ['LANG'] = 'id'
        assert '.' == get_thousand_separator()
        assert ',' == get_decimal_separator()

    def test_create_classes(self):
        """Test create_classes.
        """
        # Normal case
        class_list = [0, 1, 4, 2, 9, 2, float('nan')]
        num_classes = 2
        expected_classes = [1.0, 9.0]
        result = create_classes(class_list, num_classes)
        message = '%s is not same with %s' % (result, expected_classes)
        self.assertEqual(result, expected_classes, message)

        # There's only 1 value
        class_list = [6]
        num_classes = 3
        expected_classes = [2.0, 4.0, 6.0]
        result = create_classes(class_list, num_classes)
        message = '%s is not same with %s' % (result, expected_classes)
        self.assertEqual(result, expected_classes, message)

        # Max value <= 1.0
        class_list = [0.1, 0.3, 0.9]
        num_classes = 3
        expected_classes = [0.3, 0.6, 0.9]
        result = create_classes(class_list, num_classes)
        message = '%s is not same with %s' % (result, expected_classes)
        self.assertEqual(result, expected_classes, message)

        # There are only 2 values
        class_list = [2, 6]
        num_classes = 3
        expected_classes = [1.0, 3.5, 6.0]
        result = create_classes(class_list, num_classes)
        message = '%s is not same with %s' % (result, expected_classes)
        self.assertEqual(result, expected_classes, message)

        # Another 2 values
        class_list = [2.5, 6]
        num_classes = 3
        expected_classes = [2.0, 4.0, 6.0]
        result = create_classes(class_list, num_classes)
        message = '%s is not same with %s' % (result, expected_classes)
        self.assertEqual(result, expected_classes, message)

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

    def test_get_utm_epsg(self):
        """Test we can get correct epsg code"""
        # North semisphere
        self.assertEqual(get_utm_epsg(-178, 10), 32601)
        self.assertEqual(get_utm_epsg(178, 20), 32660)
        self.assertEqual(get_utm_epsg(-3, 30), 32630)
        # South semisphere:
        self.assertEqual(get_utm_epsg(-178, -10), 32701)
        self.assertEqual(get_utm_epsg(178, -20), 32760)
        self.assertEqual(get_utm_epsg(-3, -30), 32730)

    def test_get_non_conflicting_attribute_name(self):
        """Test we can get a non conflicting attribute name."""
        default_name = 'population'
        attribute_names = ['POPULATION', 'id', 'location', 'latitude']
        non_conflicting_attribute_name = get_non_conflicting_attribute_name(
            default_name, attribute_names)
        expected_result = 'populati_1'
        message = 'The expected result should be %s, but it gives %s' % (
            expected_result, non_conflicting_attribute_name)
        self.assertEqual(
            expected_result, non_conflicting_attribute_name, message)

    def test_log_file_path(self):
        """Test the log_file_path returns correct path."""
        log_temp_dir = temp_dir('logs')
        actual_path = os.path.join(log_temp_dir, 'inasafe.log')
        message = 'Actual log path: %s, I got %s' % (
            actual_path, log_file_path())
        self.assertEqual(actual_path, log_file_path(), message)

    def test_romanise(self):
        """Test we can convert MMI values to float."""
        values = range(2, 10)
        expected_result = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        result = []
        for value in values:
            result.append(romanise(value))
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
