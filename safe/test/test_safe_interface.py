# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**SAFE Interface test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '04/04/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.common.testing import TESTDATA, HAZDATA, EXPDATA
from safe_qgis.safe_interface import (
    available_functions,
    read_file_keywords)
from safe.exceptions import (
    KeywordNotFoundError)


class SafeInterfaceTest(unittest.TestCase):
    """Test the SAFE API Wrapper"""

    def setUp(self):
        """Setup test before each unit"""
        self.vectorPath = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.rasterShakePath = os.path.join(HAZDATA,
                                            'Shakemap_Padang_2009.asc')
        self.rasterTsunamiPath = os.path.join(
            TESTDATA, 'tsunami_max_inundation_depth_utm56s.tif')
        self.rasterExposurePath = os.path.join(TESTDATA,
                                               'tsunami_building_exposure.shp')

        self.rasterPopulationPath = os.path.join(EXPDATA, 'glp10ag.asc')

    def test_available_functions(self):
        """Check we can get the available functions from the impact calculator.
        """
        functions = available_functions()
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

        # Also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        keywords1 = read_file_keywords(self.rasterShakePath)
        keywords2 = read_file_keywords(self.vectorPath)
        # We need to explicitly add the layer type to each keyword list
        keywords1['layertype'] = 'raster'
        keywords2['layertype'] = 'vector'

        functions = [keywords1, keywords2]
        functions = available_functions(functions)
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

    def test_get_keyword_from_file(self):
        """Get keyword from a filesystem file's .keyword file."""

        keyword = read_file_keywords(self.rasterShakePath, 'category')
        expected_keyword = 'hazard'
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
            keyword, expected_keyword, self.rasterShakePath)
        self.assertEqual(keyword, 'hazard', message)

        # Test we get an exception if keyword is not found
        try:
            _ = read_file_keywords(self.rasterShakePath,
                                   'boguskeyword')
        except KeywordNotFoundError:
            pass  # this is good
        except Exception, e:
            message = ('Request for bogus keyword raised incorrect '
                       'exception type: \n %s') % str(e)
            assert(), message

        keywords = read_file_keywords(self.rasterShakePath)

        expected_keywords = {
            'category': 'hazard',
            'subcategory': 'earthquake',
            'source': 'USGS',
            'unit': 'MMI',
            'title': 'An earthquake in Padang like in 2009'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(self.rasterPopulationPath)
        expected_keywords = {
            'category': 'exposure',
            'source': ('Center for International Earth Science Information '
                       'Network (CIESIN)'),
            'subcategory': 'population',
            'datatype': 'density',
            'title': 'People'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(self.vectorPath)
        expected_keywords = {
            'category': 'exposure',
            'datatype': 'itb',
            'subcategory': 'structure',
            'title': 'Padang WGS84'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        #  tsunami example (one layer is UTM)
        keywords = read_file_keywords(self.rasterTsunamiPath)
        expected_keywords = {
            'title': 'Tsunami Max Inundation',
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'm'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)

        keywords = read_file_keywords(self.rasterExposurePath)
        expected_keywords = {
            'category': 'exposure',
            'subcategory': 'structure',
            'title': 'Tsunami Building Exposure'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords, keywords)
        self.assertEqual(keywords, expected_keywords, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(SafeInterfaceTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
