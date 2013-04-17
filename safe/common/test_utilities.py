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
from safe.common.utilities import humanize_class


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

if __name__ == '__main__':
    suite = unittest.makeSuite(UtilitiesTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
