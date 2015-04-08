# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test module for Registry**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'lana.pcfre@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '19/03/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import inspect

from safe.impact_functions import register_impact_functions
from safe.impact_functions.inundation.flood_vector_building_impact_qgis\
    .impact_function import FloodPolygonBuildingQgisFunction
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .impact_function import FloodVectorBuildingFunction
from safe.impact_functions.registry import Registry
from safe.definitions import (
    unit_wetdry,
    layer_vector_polygon,
    exposure_structure,
    unit_building_type_type,
    hazard_flood)


class TestRegistry(unittest.TestCase):

    def setUp(self):
        register_impact_functions()

    def test_register_and_clear(self):
        """TestRegistry: Test register and clear impact function."""
        registry = Registry()
        registry.clear()
        message = 'Expecting registry should be cleared. %s impact ' \
                  'functions exists instead' % len(registry.impact_functions)
        self.assertEqual(0, len(registry.impact_functions), message)

        registry.register(FloodPolygonBuildingQgisFunction)
        message = 'Expecting registry will contains 1 impact functions. %s ' \
                  'impact functions exists' % len(registry.impact_functions)
        self.assertEqual(1, len(registry.impact_functions), message)

        result = registry.get_instance('FloodPolygonBuildingQgisFunction')\
            .metadata().as_dict()['id']
        expected = 'FloodPolygonBuildingQgis'
        message = 'Expected registered impact function ID should be %s. ' \
                  'Got %s instead' % (expected, result)
        self.assertEqual(expected, result, message)

    def test_list(self):
        """TestRegistry: Test list all register IFs."""
        registry = Registry()
        impact_functions = registry.list()
        expected = [
            'Flood Vector Building Function',
            'Flood Polygon Building QGIS Function',
            'Flood Vector Roads Experimental Function',
            'Flood Evacuation Vector Hazard Function',
            'Flood Evacuation Raster Hazard Function',
            'Flood Raster Building Function',
            'Flood Raster Roads Experimental Function',
            'Flood Raster Roads GDAL Function',
            'Tsunami Evacuation Function',
            'Classified Hazard Building Function',
            'Classified Hazard Population Function',
            'Continuous Hazard Population Function',
            'Earthquake Building Function',
            'ITB Fatality Function',
            'PAG Fatality Function',
            'Volcano Point Building Impact Function',
            'Volcano Polygon Building Impact Function',
            'Volcano Polygon Population Impact Function']
        self.assertTrue(
            len(impact_functions) == len(expected) and
            all(impact_functions.count(i) == expected.count(i) for i in
                expected))

    def test_get_impact_function_instance(self):
        """TestRegistry: Test we can get an impact function instance."""
        # Getting an IF instance using its class name
        registry = Registry()
        class_name = 'FloodPolygonBuildingQgisFunction'
        impact_function = registry.get_instance(class_name)
        result = impact_function.__class__.__name__
        message = 'Expecting FloodPolygonBuildingQgisFunction. Got %s ' \
                  'instead.' % result
        self.assertEqual(class_name, result, message)

    def test_get_impact_function_class(self):
        """TestRegistry: Test we can get an impact function class."""
        # Getting an IF class using its class name
        registry = Registry()
        expected = 'FloodPolygonBuildingQgisFunction'
        impact_function = registry.get_class(expected)

        # Check that it should be a class, not an instance
        message = 'Expecting a class, not an object'
        self.assertTrue(inspect.isclass(impact_function), message)

        # Check the IF name the same
        result = impact_function.__name__
        message = 'Expecting %s. Got %s instead.' % (expected, result)
        self.assertEqual(expected, result, message)

    def test_get_impact_functions_by_metadata(self):
        """TestRegistry: Test getting the impact functions by its metadata."""
        # Test getting the impact functions by 'id'
        registry = Registry()
        impact_function_id = 'FloodPolygonBuildingQgis'
        result = registry.filter_by_metadata('id', impact_function_id)
        expected = [FloodPolygonBuildingQgisFunction]
        message = 'Expecting %s. Got %s instead' % (expected, result)
        self.assertEqual(expected, result, message)

        # Test getting the impact functions by 'name'
        impact_function_name = 'Flood Polygon Building QGIS Function'
        result = registry.filter_by_metadata('name', impact_function_name)
        expected = [FloodPolygonBuildingQgisFunction]
        message = 'Expecting %s. Got %s instead.' % (expected, result)
        self.assertEqual(expected, result, message)

    def test_filter_by_metadata(self):
        """TestRegistry: Test filtering IF by hazard and exposure metadata."""
        hazard_metadata = {
            'subcategory': hazard_flood,
            'units': unit_wetdry,
            'layer_constraints': layer_vector_polygon
        }

        exposure_metadata = {
            'subcategory': exposure_structure,
            'units': unit_building_type_type,
            'layer_constraints': layer_vector_polygon
        }

        registry = Registry()
        impact_functions = registry.filter(hazard_metadata, exposure_metadata)
        expected = [
            FloodVectorBuildingFunction,
            FloodPolygonBuildingQgisFunction]
        message = 'Expecting %s. Got %s instead' % (expected, impact_functions)
        self.assertEqual(expected, impact_functions, message)

    def test_filter_by_keywords(self):
        """TestRegistry: Test filtering IF using hazard n exposure keywords."""
        # Using keywords string
        hazard_keywords = {
            'subcategory': 'flood',
            'units': 'wetdry',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'units': 'building_type',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }
        registry = Registry()
        impact_functions = registry.filter_by_keyword_string(
            hazard_keywords, exposure_keywords)
        message = 'Registry should returns matched impact functions. ' \
                  'Nothing returned instead. Please check registered IF.'
        self.assertTrue(len(impact_functions) > 0, message)

        for impact_function in impact_functions:
            result = impact_function.metadata().as_dict()[
                'categories']['hazard']['subcategories']
            result_list = [subcat.get('id') for subcat in result]
            expected = 'flood'
            message = 'Expecting flood hazard impact functions. Got %s ' \
                      'instead' % result_list[0]
            self.assertTrue(expected in result_list, message)

            result = impact_function.metadata().as_dict()[
                'categories']['exposure']['subcategories']
            result_list = [subcat.get('id') for subcat in result]
            expected = 'structure'
            message = 'Expecting structure exposure impact functions. ' \
                      'Got %s instead' % result_list[0]
            self.assertTrue(expected in result_list, message)
