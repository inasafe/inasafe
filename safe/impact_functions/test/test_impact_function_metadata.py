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

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.test.test_registry import EXPECTED_IF
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)

# Importing IFs
# Earthquake IFs
from safe.impact_functions.earthquake.earthquake_building.impact_function \
    import EarthquakeBuildingFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model. \
    impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model. \
    impact_function import PAGFatalityFunction
from safe.impact_functions.earthquake.itb_bayesian_earthquake_fatality_model.\
    impact_function import ITBBayesianFatalityFunction

# Generic IFs
from safe.impact_functions.generic.classified_polygon_building\
    .impact_function import ClassifiedPolygonHazardBuildingFunction
from safe.impact_functions.generic.classified_polygon_population \
    .impact_function import ClassifiedPolygonHazardPopulationFunction
from safe.impact_functions.generic.classified_polygon_people\
    .impact_function import ClassifiedPolygonHazardPolygonPeopleFunction
from safe.impact_functions.generic.classified_polygon_landcover\
    .impact_function import ClassifiedPolygonHazardLandCoverFunction
from safe.impact_functions.generic.classified_raster_building \
    .impact_function import ClassifiedRasterHazardBuildingFunction
from safe.impact_functions.generic.classified_raster_population \
    .impact_function import ClassifiedRasterHazardPopulationFunction
from safe.impact_functions.generic.continuous_hazard_population \
    .impact_function import ContinuousHazardPopulationFunction

# Inundation IFs
from safe.impact_functions.inundation.flood_polygon_population\
    .impact_function import FloodEvacuationVectorHazardFunction
from safe.impact_functions.inundation.flood_polygon_roads.impact_function \
    import FloodPolygonRoadsFunction
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .impact_function import FloodRasterBuildingFunction
from safe.impact_functions.inundation.flood_raster_population.impact_function\
    import FloodEvacuationRasterHazardFunction
from safe.impact_functions.inundation.flood_raster_road\
    .impact_function import FloodRasterRoadsFunction
from safe.impact_functions.inundation.flood_vector_building_impact\
    .impact_function import FloodPolygonBuildingFunction

# Tsunami
from safe.impact_functions.inundation.tsunami_population_evacuation_raster\
    .impact_function import TsunamiEvacuationFunction
from safe.impact_functions.inundation.tsunami_raster_road\
    .impact_function import TsunamiRasterRoadsFunction
from safe.impact_functions.inundation.tsunami_raster_landcover\
    .impact_function import TsunamiRasterLandcoverFunction
from safe.impact_functions.inundation.tsunami_raster_building\
    .impact_function import TsunamiRasterBuildingFunction

# Volcanic IFs
from safe.impact_functions.volcanic.volcano_point_building.impact_function\
    import VolcanoPointBuildingFunction
from safe.impact_functions.volcanic.volcano_point_population.impact_function \
    import VolcanoPointPopulationFunction
from safe.impact_functions.volcanic.volcano_polygon_building.impact_function\
    import VolcanoPolygonBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_population\
    .impact_function import VolcanoPolygonPopulationFunction

# Volcanic Ash
from safe.impact_functions.ash.ash_raster_landcover.impact_function import \
    AshRasterLandCoverFunction
from safe.impact_functions.ash.ash_raster_population.impact_function import \
    AshRasterPopulationFunction
from safe.impact_functions.ash.ash_raster_places.impact_function import \
    AshRasterPlacesFunction

from safe.definitionsv4.layer_purposes import layer_purpose_exposure
from safe.definitionsv4.layer_modes import layer_mode_continuous
from safe.definitionsv4.fields import structure_class_field, volcano_name_field
from safe.definitionsv4.exposure import exposure_population, exposure_structure
from safe.definitionsv4.units import unit_mmi, count_exposure_unit
from safe.definitionsv4.hazard import hazard_category_multiple_event, hazard_earthquake
from safe.definitionsv4.hazard_category import hazard_category_single_event, \
    hazard_category_multiple_event
from safe.definitionsv4.layer_geometry import layer_geometry_raster


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
            # Earthquake
            EarthquakeBuildingFunction(),
            ITBFatalityFunction(),
            PAGFatalityFunction(),
            ITBBayesianFatalityFunction(),

            # Generic
            ClassifiedPolygonHazardBuildingFunction(),
            ClassifiedPolygonHazardLandCoverFunction(),
            ClassifiedPolygonHazardPopulationFunction(),
            ClassifiedPolygonHazardPolygonPeopleFunction(),
            ClassifiedRasterHazardBuildingFunction(),
            ClassifiedRasterHazardPopulationFunction(),
            ContinuousHazardPopulationFunction(),

            # Inundation
            FloodEvacuationVectorHazardFunction(),
            FloodPolygonRoadsFunction(),
            FloodRasterBuildingFunction(),
            FloodEvacuationRasterHazardFunction(),
            FloodRasterRoadsFunction(),
            FloodPolygonBuildingFunction(),

            # Tsunami
            TsunamiEvacuationFunction(),
            TsunamiRasterRoadsFunction(),
            TsunamiRasterLandcoverFunction(),
            TsunamiRasterBuildingFunction(),

            # Volcanic
            VolcanoPointBuildingFunction(),
            VolcanoPointPopulationFunction(),
            VolcanoPolygonBuildingFunction(),
            VolcanoPolygonPopulationFunction(),

            # Volcanic Ash
            AshRasterLandCoverFunction(),
            AshRasterPlacesFunction(),
            AshRasterPopulationFunction()
        ]
        self.assertEqual(len(impact_functions), len(EXPECTED_IF))

        for impact_function in impact_functions:
            valid = impact_function.metadata().is_valid()
            impact_function_name = impact_function.__class__.__name__
            message = '%s is invalid because %s' % (
                impact_function_name, valid[1])
            self.assertTrue(valid[0], message)
            if valid[0]:
                # print '%s has a valid metadata.' % impact_function_name
                continue

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

    def test_get_layer_requirements(self):
        """Test for get_layer_requirements."""
        impact_function = VolcanoPolygonBuildingFunction()
        layer_req = impact_function.metadata().get_layer_requirements()
        self.assertIsNotNone(layer_req)
        self.assertIsInstance(layer_req, dict)

    def test_purposes_for_layer(self):
        """Test for purposes_for_layer."""
        impact_function = EarthquakeBuildingFunction()
        layer_purpose = impact_function.metadata().purposes_for_layer(
            'polygon')
        self.assertIsNotNone(layer_purpose)
        expected_result = [layer_purpose_exposure]
        self.assertItemsEqual(layer_purpose, expected_result)

    def test_hazard_categories_for_layer(self):
        """Test for hazard_categories_for_layer"""
        impact_function = EarthquakeBuildingFunction()
        hazard_categories = impact_function.metadata()\
            .hazard_categories_for_layer('raster')
        expected = [
            hazard_category_single_event, hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function.metadata() \
            .hazard_categories_for_layer('raster', 'earthquake')
        expected = [
            hazard_category_single_event, hazard_category_multiple_event]
        self.assertItemsEqual(hazard_categories, expected)

        hazard_categories = impact_function.metadata() \
            .hazard_categories_for_layer('polygon')
        expected = []
        self.assertItemsEqual(hazard_categories, expected)

    def test_hazards_for_layer(self):
        """Test hazards_for_layer"""
        impact_function = EarthquakeBuildingFunction()
        hazards = impact_function.metadata().hazards_for_layer(
            'raster', 'single_event')
        expected = [hazard_earthquake]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function.metadata().hazards_for_layer('raster',)
        expected = [hazard_earthquake]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function.metadata().hazards_for_layer(
            'polygon', 'single_event')
        expected = []
        self.assertItemsEqual(hazards, expected)

    def test_exposures_for_layer(self):
        """Test exposures_for_layer."""
        impact_function = EarthquakeBuildingFunction()
        exposures = impact_function.metadata().exposures_for_layer('polygon')
        expected = [exposure_structure]
        self.assertItemsEqual(exposures, expected)

        exposures = impact_function.metadata().exposures_for_layer('raster')
        expected = []
        self.assertItemsEqual(exposures, expected)

    def test_exposure_units_for_layer(self):
        """Test exposure_units_for_layer."""
        impact_function = ITBFatalityFunction()
        exposure_units = impact_function.metadata().exposure_units_for_layer(
            'population', 'raster', 'continuous')
        expected = [count_exposure_unit]
        self.assertItemsEqual(exposure_units, expected)

        exposure_units = impact_function.metadata().exposure_units_for_layer(
            'population', 'raster', 'classified')
        expected = []
        self.assertItemsEqual(exposure_units, expected)

    def test_continuous_hazards_units_for_layer(self):
        """Test continuous_hazards_units_for_layer."""
        impact_function = ITBFatalityFunction()
        continuous_hazards_units = impact_function.metadata().\
            continuous_hazards_units_for_layer(
                'earthquake', 'raster', 'continuous', 'single_event')
        expected = [unit_mmi]
        self.assertItemsEqual(continuous_hazards_units, expected)

        continuous_hazards_units = impact_function.metadata().\
            continuous_hazards_units_for_layer(
                'flood', 'raster', 'continuous', 'single_event')
        expected = []
        self.assertItemsEqual(continuous_hazards_units, expected)

    def test_available_hazards(self):
        """Test available_hazards."""
        impact_function = ITBFatalityFunction()
        hazards = impact_function.metadata().available_hazards(
            'single_event')
        expected = [hazard_earthquake]
        self.assertItemsEqual(hazards, expected)

        hazards = impact_function.metadata().available_hazards(
            'multiple_event')
        expected = [hazard_earthquake]
        self.assertItemsEqual(hazards, expected)

    def test_available_exposures(self):
        """Test available_exposure."""
        impact_function = ITBFatalityFunction()
        hazards = impact_function.metadata().available_exposures()
        expected = [exposure_population]
        self.assertItemsEqual(hazards, expected)

    def test_is_function_for_constraint(self):
        """Test for is_function_for_constraint"""
        impact_function = ITBFatalityFunction()
        result = impact_function.metadata().is_function_for_constraint(
            'earthquake',
            'population',
            'raster',
            'raster',
            'continuous',
            'continuous',
        )
        self.assertTrue(result)

        result = impact_function.metadata().is_function_for_constraint(
            'earthquake',
            'population',
            'raster',
            'raster',
            'classified',
            'continuous',
        )
        self.assertFalse(result)

    def test_available_hazard_constraints(self):
        """Test for available_hazard_constraints."""
        impact_function = ITBFatalityFunction()
        result = impact_function.metadata().available_hazard_constraints(
            'earthquake',
            'single_event'
        )
        expected = [
            (layer_mode_continuous, layer_geometry_raster)
        ]
        self.assertItemsEqual(result, expected)

    def test_available_exposure_constraints(self):
        """Test for available_exposure_constraints."""
        impact_function = ITBFatalityFunction()
        result = impact_function.metadata().available_exposure_constraints(
            'population'
        )
        expected = [
            (layer_mode_continuous, layer_geometry_raster)
        ]
        self.assertItemsEqual(result, expected)

    @unittest.skip('Test without assert.')
    def test_valid_layer_keywords(self):
        """Test for valid_layer_keywords."""
        impact_function = VolcanoPointPopulationFunction()
        layer_keywords = impact_function.metadata().valid_layer_keywords()
        from pprint import pprint
        pprint(layer_keywords)

    def test_available_hazard_layer_mode(self):
        """Test for available_hazard_layer_mode."""
        impact_function = ITBFatalityFunction()
        result = impact_function.metadata().available_hazard_layer_mode(
            'earthquake',
            'raster',
            'single_event'
        )

        expected = layer_mode_continuous
        self.assertEqual(result, expected)

    def test_available_exposure_layer_mode(self):
        """Test for available_exposure_layer_mode."""
        impact_function = ITBFatalityFunction()
        result = impact_function.metadata().available_exposure_layer_mode(
            'population',
            'raster'
        )
        expected = layer_mode_continuous
        self.assertEqual(result, expected)

    def test_hazard_additional_keywords(self):
        """Test for hazard_additional_keywords."""
        impact_function = FloodPolygonBuildingFunction()
        result = impact_function.metadata().hazard_additional_keywords(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            hazard_category_key='single_event',
            hazard_key='flood'
        )
        expected = []
        self.assertItemsEqual(result, expected)

        result = impact_function.metadata().hazard_additional_keywords(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            hazard_category_key='single_event',
        )
        expected = []
        self.assertItemsEqual(result, expected)

        impact_function = VolcanoPointBuildingFunction()
        result = impact_function.metadata().hazard_additional_keywords(
            layer_mode_key='classified',
            layer_geometry_key='point',
            hazard_category_key='multiple_event',
            hazard_key='volcano'
        )
        expected = [volcano_name_field]
        self.assertItemsEqual(result, expected)

    def test_exposure_additional_keywords(self):
        """Test for exposure_additional_keywords."""
        impact_function = FloodPolygonBuildingFunction()
        result = impact_function.metadata().exposure_additional_keywords(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = []
        self.assertItemsEqual(result, expected)

        result = impact_function.metadata().exposure_additional_keywords(
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = []
        self.assertItemsEqual(result, expected)

    def test_exposure_class_fields(self):
        """Test for exposure_class_fields."""
        impact_function = FloodPolygonBuildingFunction()
        result = impact_function.metadata().exposure_class_fields(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = [structure_class_field]
        self.assertItemsEqual(result, expected)

        result = impact_function.metadata().exposure_class_fields(
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = [structure_class_field]
        self.assertItemsEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
