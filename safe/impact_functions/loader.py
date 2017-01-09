# coding=utf-8

from safe.impact_functions.impact_function_manager import ImpactFunctionManager


__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/25/16'


def register_impact_functions():
    """Register all the impact functions available."""
    impact_function_registry = ImpactFunctionManager().registry
