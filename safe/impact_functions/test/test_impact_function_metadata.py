# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Metadata**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '17/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)

from safe.impact_functions.volcanic.volcano_point_building.impact_function\
    import VolcanoPointBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_building.impact_function\
    import VolcanoPolygonBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_population\
    .impact_function import VolcanoPolygonPopulationFunction
from safe.impact_functions.generic.classified_hazard_building \
    .impact_function import ClassifiedHazardBuildingFunction
from safe.impact_functions.generic.classified_hazard_population \
    .impact_function import ClassifiedHazardPopulationFunction
from safe.impact_functions.generic.continuous_hazard_population \
    .impact_function import ContinuousHazardPopulationFunction
from safe.impact_functions.earthquake.earthquake_building.impact_function \
    import EarthquakeBuildingFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model.\
    impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model. \
    impact_function import PAGFatalityFunction
from safe.impact_functions.inundation.flood_polygon_roads.impact_function\
    import FloodVectorRoadsExperimentalFunction
from safe.impact_functions.inundation.\
    flood_population_evacuation_polygon_hazard.impact_function \
    import FloodEvacuationVectorHazardFunction
from safe.impact_functions.inundation. \
    flood_population_evacuation_raster_hazard.impact_function \
    import FloodEvacuationRasterHazardFunction
from safe.impact_functions.inundation.flood_raster_osm_building_impact \
    .impact_function import FloodRasterBuildingFunction
from safe.impact_functions.inundation.flood_raster_road_qgis.impact_function \
    import FloodRasterRoadsExperimentalFunction
from safe.impact_functions.inundation.flood_raster_road_qgis_gdal \
    .impact_function import FloodRasterRoadsGdalFunction
from safe.impact_functions.inundation.flood_vector_building_impact_qgis \
    .impact_function import FloodPolygonBuildingQgisFunction
from safe.impact_functions.inundation.flood_vector_osm_building_impact. \
    impact_function import FloodVectorBuildingFunction
from safe.impact_functions.inundation.tsunami_population_evacuation_raster. \
    impact_function import TsunamiEvacuationFunction
from safe.definitions import (
    unit_metres_depth,
    unit_feet_depth,
    unit_mmi,
    exposure_structure,
    hazard_earthquake,
    unit_building_type_type,
    layer_raster_continuous,
    layer_vector_polygon,
    layer_vector_point,
    hazard_all,
    unit_building_generic,
    hazard_flood,
    hazard_tsunami)

from safe.new_definitions import (
    layer_purpose_exposure,
    hazard_category_hazard_scenario
)


# noinspection PyUnresolvedReferences
class TestImpactFunctionMetadata(unittest.TestCase):
    """Test for ImpactFunctionMetadata.

    .. versionadded:: 2.1
    """
    def test_init(self):
        """Test init base class."""
        ifm = ImpactFunctionMetadata()
        with self.assertRaises(NotImplementedError):
            ifm.as_dict()
            ifm.allowed_data_types('flood')

    def test_is_valid(self):
        """Test is_valid."""
        impact_functions = [
            VolcanoPointBuildingFunction(),
            VolcanoPolygonBuildingFunction(),
            VolcanoPolygonPopulationFunction(),
            ClassifiedHazardBuildingFunction(),
            ClassifiedHazardPopulationFunction(),
            ContinuousHazardPopulationFunction(),
            EarthquakeBuildingFunction(),
            ITBFatalityFunction(),
            PAGFatalityFunction(),
            FloodVectorRoadsExperimentalFunction(),
            FloodEvacuationVectorHazardFunction(),
            FloodEvacuationRasterHazardFunction(),
            FloodRasterBuildingFunction(),
            FloodRasterRoadsExperimentalFunction(),
            FloodRasterRoadsGdalFunction(),
            FloodPolygonBuildingQgisFunction(),
            FloodVectorBuildingFunction(),
            TsunamiEvacuationFunction()
        ]
        for impact_function in impact_functions:
            valid = impact_function.metadata().is_valid()
            impact_function_name = impact_function.__class__.__name__
            message = '%s is invalid because %s' % (
                impact_function_name, valid[1])
            self.assertTrue(valid[0], message)
            if valid[0]:
                print '%s has a valid metadata.' % impact_function_name

    def test_is_subset(self):
        """Test for is_subset function."""
        assert ImpactFunctionMetadata.is_subset('a', ['a'])
        assert ImpactFunctionMetadata.is_subset('a', ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset(['a'], ['a', 'b'])
        assert ImpactFunctionMetadata.is_subset('a', 'a')
        assert not ImpactFunctionMetadata.is_subset('a', 'ab')
        assert not ImpactFunctionMetadata.is_subset(['a', 'c'], ['a', 'b'])

    def test_inner_class(self):
        """Test call inner class."""
        impact_function = EarthquakeBuildingFunction()
        # call from an object
        metadata = impact_function.metadata()
        metadata_dictionary = metadata.as_dict()
        assert isinstance(metadata_dictionary, dict), 'I did not got a dict'
        # call from the class
        metadata = impact_function.metadata()
        metadata_dictionary = metadata.as_dict()
        assert isinstance(metadata_dictionary, dict), 'I did not got a dict'

    @unittest.skip('Until updated the API')
    def test_allowed_data_types(self):
        """Test for allowed_data_types API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().allowed_data_types('structure')
        expected_result = ['polygon', 'point']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.metadata().allowed_data_types('earthquake')
        expected_result = ['continuous']
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_allowed_units(self):
        """Test for allowed_units API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata() .allowed_units(
            'structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.metadata() .allowed_units(
            'structure', 'continuous')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction
        result = impact_function.metadata().allowed_units(
            'structure', 'polygon')
        expected_result = [unit_building_type_type, unit_building_generic]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

        result = impact_function.metadata()\
            .allowed_units('flood', 'continuous')
        expected_result = [unit_metres_depth, unit_feet_depth]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_allowed_layer_constraints(self):
        """Test for allowed_layer_constraints API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().allowed_layer_constraints()
        expected_result = [layer_raster_continuous, layer_vector_polygon,
                           layer_vector_point]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.metadata().allowed_layer_constraints(
            'hazard')
        expected_result = [layer_raster_continuous]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.metadata().allowed_layer_constraints(
            'exposure')
        expected_result = [layer_vector_polygon, layer_vector_point]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_units_for_layer(self):
        """Test for units_for_layer API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().units_for_layer(
            subcategory='earthquake',
            layer_type='raster',
            data_type='continuous')
        expected_result = [unit_mmi]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.metadata().units_for_layer(
            subcategory='flood', layer_type='raster', data_type='continuous')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.metadata().units_for_layer(
            subcategory='earthquake',
            layer_type='vector',
            data_type='continuous')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        result = impact_function.metadata().units_for_layer(
            subcategory='earthquake', layer_type='raster', data_type='polygon')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = ContinuousHazardPopulationFunction()
        result = impact_function.metadata().units_for_layer(
            subcategory='flood', layer_type='raster', data_type='continuous')
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_get_hazards(self):
        """Test for get_hazards API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().get_hazards()
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().get_hazards()
        expected_result = [hazard_flood, hazard_tsunami]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_has_hazard(self):
        """Test for has_hazard API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().has_hazard(hazard_earthquake)
        expected_result = True
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().has_hazard(hazard_earthquake)
        expected_result = False
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_has_hazard_id(self):
        """Test for has_hazard_id API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().has_hazard_id(
            hazard_earthquake['id'])
        expected_result = True
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().has_hazard_id(
            hazard_earthquake['id'])
        expected_result = False
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_get_exposures(self):
        """Test for get_exposures API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().get_exposures()
        expected_result = [exposure_structure]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().get_exposures()
        expected_result = []
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertNotEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_has_exposure(self):
        """Test for has_exposure API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().has_exposure(exposure_structure)
        expected_result = True
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().has_exposure(exposure_structure)
        expected_result = True
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_has_exposure_id(self):
        """Test for has_exposure_id API."""
        impact_function = EarthquakeBuildingFunction()
        result = impact_function.metadata().has_exposure_id(
            exposure_structure['id'])
        expected_result = True
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

        impact_function = FloodRasterBuildingFunction()
        result = impact_function.metadata().has_exposure_id(
            hazard_earthquake['id'])
        expected_result = False
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    @unittest.skip('Until updated the API')
    def test_get_hazard_layer_constraint(self):
        """Test for get_hazard_layer_constraint."""
        impact_function = FloodRasterBuildingFunction()
        expected_layer_constraint = [layer_raster_continuous]
        layer_constraints \
            = impact_function.metadata().get_hazard_layer_constraint()
        message = 'Expected %s but got %s' % (
            expected_layer_constraint, layer_constraints)
        self.assertItemsEqual(
            expected_layer_constraint, layer_constraints, message)

    @unittest.skip('Until updated the API')
    def test_get_exposure_layer_constraint(self):
        """Test for get_exposure_layer_constraint."""
        impact_function = FloodRasterBuildingFunction()
        expected_layer_constraint = [
            layer_vector_polygon,
            layer_vector_point
        ]
        layer_constraints \
            = impact_function.metadata().get_exposure_layer_constraint()
        message = 'Expected %s but got %s' % (
            expected_layer_constraint, layer_constraints)
        self.assertItemsEqual(
            expected_layer_constraint, layer_constraints, message)

    def test_get_layer_requirements(self):
        """Test for get_layer_requirements."""
        impact_function = VolcanoPolygonBuildingFunction()
        layer_req = impact_function.metadata().get_layer_requirements()
        self.assertIsNotNone(layer_req)
        self.assertIsInstance(layer_req, dict)

    def test_purposes_for_layer(self):
        """Test for purposes_for_layer."""
        impact_function = EarthquakeBuildingFunction()
        layer_purpose = impact_function.metadata().purposes_for_layer('polygon')
        self.assertIsNotNone(layer_purpose)
        expected_result = [layer_purpose_exposure]
        self.assertItemsEqual(layer_purpose, expected_result)

    def test_hazard_categories_for_layer(self):
        """Test for hazard_categories_for_layer"""
        impact_function = EarthquakeBuildingFunction()
        hazard_categories = impact_function.metadata()\
            .hazard_categories_for_layer('raster')
        expected = [hazard_category_hazard_scenario]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function.metadata() \
            .hazard_categories_for_layer('polygon')
        expected = []
        self.assertItemsEqual(hazard_categories, expected)

if __name__ == '__main__':
    unittest.main()
