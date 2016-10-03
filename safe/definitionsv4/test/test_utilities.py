# coding=utf-8

"""Test for utilities module..
"""
import unittest

from safe.definitionsv4.utilities import purposes_for_layer


class TestDefinitionsUtilities(unittest.TestCase):
    def test_layer_purpose_for_layer(self):
        expected = ['aggregation', 'exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('polygon'))

        expected = ['exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('raster'))

        expected = ['exposure']
        self.assertListEqual(expected, purposes_for_layer('line'))


if __name__ == '__main__':
    unittest.main()
