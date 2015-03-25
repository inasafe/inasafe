# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Registering all impact
functions available into the registry.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.impact_functions.earthquake.earthquake_building.impact_function import \
    EarthquakeBuildingFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_funtion import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model\
    .impact_function import PAGFatalityFunction
from safe.impact_functions.generic.classified_hazard_building\
    .impact_function import ClassifiedHazardBuildingFunction
from safe.impact_functions.generic.classified_hazard_population\
    .impact_function import ClassifiedHazardPopulationFunction
from safe.impact_functions.generic.continuous_hazard_population\
    .impact_function import ContinuousHazardPopulationFunction
from safe.impact_functions.inundation.flood_raster_osm_building_impact\
    .impact_function import FloodRasterBuildingFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation.flood_raster_road_qgis\
    .impact_function import FloodRasterRoadsExperimentalFunction
from safe.impact_functions.inundation.flood_raster_road_qgis_gdal\
    .impact_function import FloodRasterRoadsGdalFunction
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .impact_function import FloodVectorBuildingFunction
from safe.impact_functions.inundation.flood_vector_building_impact_qgis\
    .impact_function import FloodPolygonBuildingQgisFunction
from safe.impact_functions.inundation.flood_polygon_roads\
    .impact_function import FloodVectorRoadsExperimentalFunction
from safe.impact_functions.inundation.\
    flood_population_evacuation_raster_hazard.impact_function import \
    FloodEvacuationRasterHazardFunction
from safe.impact_functions.inundation\
    .flood_population_evacuation_polygon_hazard.impact_function import \
    FloodEvacuationVectorHazardFunction
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.impact_function import \
    TsunamiEvacuationFunction
from safe.impact_functions.volcanic.volcano_point_building.impact_function \
    import VolcanoPointBuildingFunction
from safe.impact_functions.volcanic.volcano_polygon_building.impact_function \
    import VolcanoPolygonBuildingFunction


def register_impact_functions():
    """Register all the impact functions available."""
    impact_function_registry = ImpactFunctionManager().registry
    # Inundation IF's
    impact_function_registry.register(FloodVectorBuildingFunction)
    impact_function_registry.register(FloodPolygonBuildingQgisFunction)
    impact_function_registry.register(FloodVectorRoadsExperimentalFunction)
    impact_function_registry.register(FloodEvacuationVectorHazardFunction)
    impact_function_registry.register(FloodEvacuationRasterHazardFunction)
    impact_function_registry.register(FloodRasterBuildingFunction)
    impact_function_registry.register(FloodRasterRoadsExperimentalFunction)
    impact_function_registry.register(FloodRasterRoadsGdalFunction)
    impact_function_registry.register(TsunamiEvacuationFunction)
    # Generic IF
    impact_function_registry.register(ClassifiedHazardBuildingFunction)
    impact_function_registry.register(ClassifiedHazardPopulationFunction)
    impact_function_registry.register(ContinuousHazardPopulationFunction)
    # Earthquake
    impact_function_registry.register(EarthquakeBuildingFunction)
    impact_function_registry.register(ITBFatalityFunction)
    impact_function_registry.register(PAGFatalityFunction)
    # Volcanic IF
    impact_function_registry.register(VolcanoPointBuildingFunction)
    impact_function_registry.register(VolcanoPolygonBuildingFunction)
