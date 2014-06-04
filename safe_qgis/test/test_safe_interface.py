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
import numpy
import unittest
from safe_qgis.safe_interface import (
    get_optimal_extent,
    available_functions,
    read_file_keywords,
    read_safe_layer,
    TESTDATA, HAZDATA, EXPDATA,
    BoundingBoxError)
from safe_qgis.exceptions import (
    KeywordNotFoundError,
    InsufficientOverlapError)


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

    def test_getOptimalExtent(self):
        """Optimal extent is calculated correctly
        """

        exposure_path = os.path.join(TESTDATA, 'Population_2010.asc')
        hazard_path = os.path.join(HAZDATA,
                                   'Lembang_Earthquake_Scenario.asc')

        # Expected data
        haz_metadata = {'bounding_box': (105.3000035,
                                         -8.3749994999999995,
                                         110.2914705,
                                         -5.5667784999999999),
                        'resolution': (0.0083330000000000001,
                                       0.0083330000000000001)}

        exp_metadata = {'bounding_box': (94.972335000000001,
                                         -11.009721000000001,
                                         141.0140016666665,
                                         6.0736123333332639),
                        'resolution': (0.0083333333333333003,
                                       0.0083333333333333003)}

        # Verify relevant metada is ok
        H = read_safe_layer(hazard_path)
        E = read_safe_layer(exposure_path)

        hazard_bbox = H.get_bounding_box()
        assert numpy.allclose(hazard_bbox, haz_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_bbox = E.get_bounding_box()
        assert numpy.allclose(exposure_bbox, exp_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        hazard_res = H.get_resolution()
        assert numpy.allclose(hazard_res, haz_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_res = E.get_resolution()
        assert numpy.allclose(exposure_res, exp_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        # First, do some examples that produce valid results
        ref_box = [105.3000035, -8.3749995, 110.2914705, -5.5667785]
        view_port = [94.972335, -11.009721, 141.014002, 6.073612]

        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        #testing with viewport clipping disabled
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, None)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        view_port = [105.3000035,
                     -8.3749994999999995,
                     110.2914705,
                     -5.5667784999999999]
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Very small viewport fully inside other layers
        view_port = [106.0, -6.0, 108.0, -5.8]
        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)

        assert numpy.allclose(bbox, view_port,
                              rtol=1.0e-12, atol=1.0e-12)

        # viewport that intersects hazard layer
        view_port = [107.0, -6.0, 112.0, -3.0]
        ref_box = [107, -6, 110.2914705, -5.5667785]

        bbox = get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Then one where boxes don't overlap
        view_port = [105.3, -4.3, 110.29, -2.5]
        try:
            get_optimal_extent(hazard_bbox, exposure_bbox, view_port)
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'did not overlap' in str(e), message
        else:
            message = ('Non ovelapping bounding boxes should have raised '
                         'an exception')
            raise Exception(message)

        # Try with wrong input data
        try:
            get_optimal_extent(haz_metadata, exp_metadata, view_port)
        except BoundingBoxError:
            #good this was expected
            pass
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            get_optimal_extent(None, None, view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'cannot be None' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            get_optimal_extent('aoeush', 'oeuuoe', view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Instead i got "aoeush"' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

    def test_availableFunctions(self):
        """Check we can get the available functions from the impact calculator.
        """
        myList = available_functions()
        message = 'No functions available (len=%ss)' % len(myList)
        assert len(myList) > 0, message

        # Also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        keywords1 = read_file_keywords(self.rasterShakePath)
        keywords2 = read_file_keywords(self.vectorPath)
        # We need to explicitly add the layer type to each keyword list
        keywords1['layertype'] = 'raster'
        keywords2['layertype'] = 'vector'

        myList = [keywords1, keywords2]
        myList = available_functions(myList)
        message = 'No functions available (len=%ss)' % len(myList)
        assert len(myList) > 0, message

    def test_getKeywordFromFile(self):
        """Get keyword from a filesystem file's .keyword file."""

        keyword = read_file_keywords(self.rasterShakePath, 'category')
        expected_keyword = 'hazard'
        message = 'Got: %s\n\nExpected %s\n\nDB: %s' % (
                    keyword, expected_keyword, self.rasterShakePath)
        assert keyword == 'hazard', message

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

        expected_keywords = {'category': 'hazard',
                              'subcategory': 'earthquake',
                              'source': 'USGS',
                              'unit': 'MMI',
                              'title': 'An earthquake in Padang like in 2009'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords,
                                                   keywords)
        assert keywords == expected_keywords, message

        keywords = read_file_keywords(self.rasterPopulationPath)
        expected_keywords = {'category': 'exposure',
                              'source': ('Center for International Earth '
                                         'Science Information Network '
                                         '(CIESIN)'),
                              'subcategory': 'population',
                              'datatype': 'density',
                              'title': 'People'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords,
                                                   keywords)
        assert keywords == expected_keywords, message

        keywords = read_file_keywords(self.vectorPath)
        expected_keywords = {'category': 'exposure',
                              'datatype': 'itb',
                              'subcategory': 'structure',
                              'title': 'Padang WGS84'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords,
                                                   keywords)
        assert keywords == expected_keywords, message

        #  tsunami example (one layer is UTM)
        keywords = read_file_keywords(self.rasterTsunamiPath)
        expected_keywords = {'title': 'Tsunami Max Inundation',
                              'category': 'hazard',
                              'subcategory': 'tsunami',
                              'unit': 'm'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords,
                                                   keywords)
        assert keywords == expected_keywords, message

        keywords = read_file_keywords(self.rasterExposurePath)
        expected_keywords = {'category': 'exposure',
                              'subcategory': 'structure',
                              'title': 'Tsunami Building Exposure'}
        message = 'Expected:\n%s\nGot:\n%s\n' % (expected_keywords,
                                                   keywords)
        assert keywords == expected_keywords, message


if __name__ == '__main__':
    suite = unittest.makeSuite(SafeInterfaceTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
