# coding=utf-8

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/25/16'


# Earthquake
from safe.impact_functions.earthquake.earthquake_building\
    .impact_function import EarthquakeBuildingFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model\
    .impact_function import PAGFatalityFunction
from safe.impact_functions.earthquake.itb_bayesian_earthquake_fatality_model\
    .impact_function import ITBBayesianFatalityFunction

# Generic
from safe.impact_functions.generic.classified_raster_building\
    .impact_function import ClassifiedRasterHazardBuildingFunction
from safe.impact_functions.generic.classified_polygon_population\
    .impact_function import ClassifiedPolygonHazardPopulationFunction
from safe.impact_functions.generic.classified_raster_population\
    .impact_function import ClassifiedRasterHazardPopulationFunction
from safe.impact_functions.generic.continuous_hazard_population\
    .impact_function import ContinuousHazardPopulationFunction
from safe.impact_functions.generic.classified_polygon_building\
    .impact_function import ClassifiedPolygonHazardBuildingFunction
from safe.impact_functions.generic.classified_polygon_people\
    .impact_function import ClassifiedPolygonHazardPolygonPeopleFunction
from safe.impact_functions.generic.classified_polygon_landcover\
    .impact_function import ClassifiedPolygonHazardLandCoverFunction

# Inundation
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .impact_function import FloodRasterBuildingFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_raster_road\
    .impact_function import FloodRasterRoadsFunction
from safe.impact_functions.inundation.flood_vector_building_impact\
    .impact_function import FloodPolygonBuildingFunction
from safe.impact_functions.inundation.flood_polygon_roads\
    .impact_function import FloodPolygonRoadsFunction
from safe.impact_functions.inundation.flood_raster_population.impact_function\
    import FloodEvacuationRasterHazardFunction
from safe.impact_functions.inundation.flood_polygon_population\
    .impact_function import FloodEvacuationVectorHazardFunction
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.impact_function import \
    TsunamiEvacuationFunction
from safe.impact_functions.inundation.tsunami_raster_building.impact_function \
    import TsunamiRasterBuildingFunction
from safe.impact_functions.inundation.tsunami_raster_road.impact_function \
    import TsunamiRasterRoadsFunction
from safe.impact_functions.inundation.tsunami_raster_landcover.impact_function\
    import TsunamiRasterLandcoverFunction

# Volcanic
from safe.impact_functions.volcanic.volcano_point_building.impact_function \
    import VolcanoPointBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_building.impact_function \
    import VolcanoPolygonBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_population\
    .impact_function import VolcanoPolygonPopulationFunction
from safe.impact_functions.volcanic.volcano_point_population\
    .impact_function import VolcanoPointPopulationFunction

# Volcanic Ash
from safe.impact_functions.ash.ash_raster_landcover.impact_function import \
    AshRasterLandcoverFunction


def register_impact_functions():
    """Register all the impact functions available."""
    impact_function_registry = ImpactFunctionManager().registry

    # Earthquake
    impact_function_registry.register(EarthquakeBuildingFunction)
    impact_function_registry.register(ITBFatalityFunction)
    impact_function_registry.register(PAGFatalityFunction)
    # Added in 3.3
    impact_function_registry.register(ITBBayesianFatalityFunction)

    # Generic IF's
    impact_function_registry.register(ClassifiedRasterHazardBuildingFunction)
    impact_function_registry.register(ClassifiedRasterHazardPopulationFunction)
    impact_function_registry.register(ContinuousHazardPopulationFunction)
    impact_function_registry.register(
        ClassifiedPolygonHazardPopulationFunction)
    impact_function_registry.register(ClassifiedPolygonHazardBuildingFunction)
    # Added in 3.3
    impact_function_registry.register(
        ClassifiedPolygonHazardPolygonPeopleFunction)
    # Added in 3.4
    impact_function_registry.register(ClassifiedPolygonHazardLandCoverFunction)

    # Inundation IF's
    impact_function_registry.register(FloodPolygonBuildingFunction)
    impact_function_registry.register(FloodPolygonRoadsFunction)
    impact_function_registry.register(FloodEvacuationVectorHazardFunction)
    impact_function_registry.register(FloodEvacuationRasterHazardFunction)
    impact_function_registry.register(FloodRasterBuildingFunction)
    impact_function_registry.register(FloodRasterRoadsFunction)
    impact_function_registry.register(TsunamiEvacuationFunction)
    # Added in 3.3
    impact_function_registry.register(TsunamiRasterBuildingFunction)
    impact_function_registry.register(TsunamiRasterRoadsFunction)
    # Added in 3.4
    impact_function_registry.register(TsunamiRasterLandcoverFunction)

    # Volcanic IF's
    impact_function_registry.register(VolcanoPointBuildingFunction)
    impact_function_registry.register(VolcanoPolygonBuildingFunction)
    impact_function_registry.register(VolcanoPointPopulationFunction)
    impact_function_registry.register(VolcanoPolygonPopulationFunction)

    # Volcanic Ash IF's
    # Added in 3.4
    impact_function_registry.register(AshRasterLandcoverFunction)
