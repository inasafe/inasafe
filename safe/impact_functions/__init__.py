# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Registering all impact
functions available into the registry.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.impact_functions.registry import Registry
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .impact_function import FloodVectorBuildingImpactFunction
from safe.impact_functions.inundation.flood_vector_building_impact_qgis\
    .impact_function import FloodNativePolygonExperimentalFunction


def register_impact_functions():
    """Register all the impact functions available."""
    impact_function_registry = Registry()
    impact_function_registry.register(FloodVectorBuildingImpactFunction)
    impact_function_registry.register(FloodNativePolygonExperimentalFunction)
