"""
Basic plugin framework based on::
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""

from safe.impact_functions.registry import Registry
from safe.impact_functions.inundation.flood_vector_osm_building_impact\
    .impact_function import FloodVectorBuildingImpactFunction
from safe.impact_functions.inundation.flood_building_impact_qgis\
    .impact_function import \
    FloodNativePolygonExperimentalFunction


def load_plugins():
    """Iterate through each plugin dir loading all plugins."""
    impact_function_registry = Registry()
    impact_function_registry.register(FloodVectorBuildingImpactFunction)
    impact_function_registry.register(FloodNativePolygonExperimentalFunction)


load_plugins()


from safe.impact_functions.core import get_plugins  # FIXME: Deprecate
from safe.impact_functions.core import get_plugin
from safe.impact_functions.core import get_function_title
