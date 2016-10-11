# coding=utf-8

# Earthquake
from safe.impact_functions.earthquake.earthquake_building\
    .impact_function import EarthquakeBuildingFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_function import ITBFatalityFunction
from safe.impact_functions.earthquake.pager_earthquake_fatality_model\
    .impact_function import PAGFatalityFunction
from safe.impact_functions.earthquake.itb_bayesian_earthquake_fatality_model\
    .impact_function import ITBBayesianFatalityFunction

from safe.impact_functions.impact_function_manager import ImpactFunctionManager


__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/25/16'


def register_impact_functions():
    """Register all the impact functions available."""
    impact_function_registry = ImpactFunctionManager().registry

    # Earthquake
    impact_function_registry.register(EarthquakeBuildingFunction)
    impact_function_registry.register(ITBFatalityFunction)
    impact_function_registry.register(PAGFatalityFunction)
    # Added in 3.3
    impact_function_registry.register(ITBBayesianFatalityFunction)
