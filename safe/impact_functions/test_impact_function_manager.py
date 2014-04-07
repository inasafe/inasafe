# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.metadata import (
    unit_wetdry,
    unit_metres_depth,
    unit_feet_depth,
    exposure_definition,
    exposure_population,
    exposure_road,
    exposure_structure,
    hazard_all,
    hazard_definition,
    hazard_earthquake,
    hazard_flood,
    hazard_tsunami,
    hazard_volcano,
    unit_building_type_type,
    unit_people_per_pixel,
    unit_mmi,
    unit_mmi_depth
)


class TestImpactFunctionManager(unittest.TestCase):
    """Test for ImpactFunctionManager.

    .. versionadded:: 2.1
    """

    flood_OSM_building_hazard_units = [
        unit_wetdry, unit_metres_depth, unit_feet_depth]

    def test_init(self):
        """Test initialize ImpactFunctionManager."""
        ifm = ImpactFunctionManager()
        expected_result = 12
        result = len(ifm.impact_functions)
        msg = ('I expect %s but I got %s, please check the number of current '
               'enabled impact functions' % (expected_result, result))
        assert result == expected_result, msg

    def test_allowed_subcategories(self):
        """Test allowed_subcategories API."""
        ifm = ImpactFunctionManager()
        result = ifm.allowed_subcategories()
        result = [x['id'] for x in result]
        expected_result = [
            exposure_structure,
            hazard_earthquake,
            exposure_population,
            hazard_all,
            hazard_flood,
            hazard_tsunami,
            exposure_road,
            hazard_volcano
        ]
        expected_result = [x['id'] for x in expected_result]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

    def test_allowed_data_types(self):
        """Test allowed_data_types API."""
        ifm = ImpactFunctionManager()
        result = ifm.allowed_data_types('flood')
        expected_result = ['polygon', 'numeric']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.allowed_data_types('volcano')
        expected_result = ['point', 'polygon']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.allowed_data_types('structure')
        expected_result = ['polygon']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.allowed_data_types('earthquake')
        expected_result = ['polygon', 'numeric']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.allowed_data_types('tsunami')
        expected_result = ['polygon', 'numeric']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.allowed_data_types('population')
        expected_result = ['numeric']
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

    def test_allowed_units(self):
        """Test allowed_units API."""
        ifm = ImpactFunctionManager()
        result = ifm.allowed_units('structure', 'polygon')
        expected_result = [unit_building_type_type]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.allowed_units('structure', 'raster')
        expected_result = []
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.allowed_units('flood', 'numeric')
        expected_result = self.flood_OSM_building_hazard_units
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.allowed_units('earthquake', 'numeric')
        result = [x['id'] for x in result]
        expected_result = [unit_mmi_depth, unit_mmi]
        expected_result = [x['id'] for x in expected_result]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

    def test_units_for_layer(self):
        """Test units_for_layer API."""
        ifm = ImpactFunctionManager()

        result = ifm.units_for_layer(
            subcategory='flood', layer_type='raster', data_type='numeric')
        expected_result = self.flood_OSM_building_hazard_units
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.units_for_layer(
            subcategory='volcano', layer_type='raster', data_type='numeric')
        expected_result = []
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.units_for_layer(
            subcategory='population', layer_type='raster', data_type='numeric')
        expected_result = [unit_people_per_pixel]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

    def test_categories_for_layer(self):
        """Test categories_for_layer API."""
        ifm = ImpactFunctionManager()

        result = ifm.categories_for_layer(
            layer_type='raster', data_type='numeric')
        expected_result = [hazard_definition, exposure_definition]
        result = [x['id'] for x in result]
        expected_result = [x['id'] for x in expected_result]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.categories_for_layer(
            layer_type='vector', data_type='line')
        expected_result = [exposure_definition]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.categories_for_layer(
            layer_type='vector', data_type='polygon')
        expected_result = [exposure_definition, hazard_definition]
        result = [x['id'] for x in result]
        expected_result = [x['id'] for x in expected_result]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert set(result) == set(expected_result), msg

        result = ifm.categories_for_layer(
            layer_type='vector', data_type='point')
        expected_result = [hazard_definition]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.categories_for_layer(
            layer_type='raster', data_type='line')
        expected_result = []
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

    def test_subcategories_for_layer(self):
        """Test subcategories_for_layer API."""
        ifm = ImpactFunctionManager()

        result = ifm.subcategories_for_layer(
            category='hazard', layer_type='raster', data_type='numeric')
        expected_result = [
            hazard_earthquake, hazard_all, hazard_flood, hazard_tsunami]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.subcategories_for_layer(
            category='hazard', layer_type='vector', data_type='point')
        expected_result = [hazard_volcano]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.subcategories_for_layer(
            category='hazard', layer_type='vector', data_type='polygon')
        expected_result = [
            hazard_earthquake, hazard_flood, hazard_tsunami, hazard_volcano]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.subcategories_for_layer(
            category='exposure', layer_type='raster', data_type='numeric')
        expected_result = [exposure_population]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.subcategories_for_layer(
            category='exposure', layer_type='vector', data_type='line')
        expected_result = [exposure_road]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

        result = ifm.subcategories_for_layer(
            category='exposure', layer_type='vector', data_type='polygon')
        expected_result = [exposure_structure]
        msg = ('I expect %s but I got %s.' % (expected_result, result))
        assert result == expected_result, msg

if __name__ == '__main__':
    unittest.main()
