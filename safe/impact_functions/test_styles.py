# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact Merge Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '21/02/2014'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.styles import (
    generate_categorical_color_ramp)


class StylesTest(unittest.TestCase):
    """Test impact_functions.styles module."""

    def test_generate_categorical_color_ramp(self):
        result = generate_categorical_color_ramp(5)
        expected_result_hsv = [(1.0, 0.5, 0.7),
                               (0.8, 0.5, 0.7),
                               (0.6, 0.5, 0.7),
                               (0.3999999999999999, 0.5, 0.7),
                               (0.19999999999999996, 0.5, 0.7)]
        expected_result_rgb = [(178.5, 89.25, 89.25),
                               (160.65000000000006, 89.25, 178.5),
                               (89.25, 124.95000000000003, 178.5),
                               (89.25, 178.5, 124.94999999999995),
                               (160.65, 178.5, 89.25)]
        expected_result_hex = ['#b25959',
                               '#a059b2',
                               '#597cb2',
                               '#59b27c',
                               '#a0b259']
        msg = 'I got %s. Expected result %s' % (
            result['hsv'],
            expected_result_hsv)
        self.assertEqual(result['hsv'], expected_result_hsv, msg)

        msg = 'I got %s. Expected result %s' % (
            result['rgb'],
            expected_result_rgb)
        self.assertEqual(result['rgb'], expected_result_rgb, msg)

        msg = 'I got %s. Expected result %s' % (
            result['hex'],
            expected_result_hex)
        self.assertEqual(result['hex'], expected_result_hex, msg)


if __name__ == '__main__':
    suite = unittest.makeSuite(StylesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
