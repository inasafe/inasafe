# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.common.utilities import add_to_list
from safe.impact_functions.registry import Registry


class ImpactFunctionManager(object):
    """Class for managing metadata for all impact function.

    .. versionadded:: 2.1
    """

    def __init__(self):
        """Constructor."""
        # Singleton Registry to track all the registered Impact Functions
        self.registry = Registry()

    @property
    def impact_functions(self):
        """Return all registered impact functions."""
        return self.registry.impact_functions

    def get_instance(self, class_name):
        """Return an instance of an impact function given its class name.

        .. example::

            if_manager = ImpactFunctionManager()
            if_class_name = 'FloodBuildingImpactFunction'
            if =  if_manager.get_instance(if_class_name)

        :param class_name: The name of IF class.
        :type class_name: str

        :return: Impact function instance that matches the argument.
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        return self.registry.get_instance(class_name)

    def get_class(self, class_name):
        """Return the class of an impact function given its class name.

        .. example::

            if_manager = ImpactFunctionManager()
            if_class_name = 'FloodBuildingImpactFunction'
            if_class =  if_manager.get_class(if_class_name)

        :param class_name: the name of IF class
        :type class_name: str

        :return: impact function class that matches the argument.
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        return self.registry.get_class(class_name)

    def get(self, impact_function_id):
        """Return an instance of an impact function given its ID.

        This is a preferred way to get an instance of IF. IF should have a
        unique human readable ID in their metadata.

        .. example::

            if_manager = ImpactFunctionManager()
            if_id = 'FloodBuildingImpactFunction'
            if =  if_manager.get(if_id)

        :param impact_function_id: The ID of impact function in the metadata.
        :type impact_function_id: str

        :return An Impact function instance that has matched id.
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        impact_functions = self.registry.filter_by_metadata(
            'id', impact_function_id)
        if len(impact_functions) == 0:
            raise Exception(
                'Impact function with ID: %s not found' % impact_function_id)
        elif len(impact_functions) > 1:
            raise Exception(
                'There are some Impact Functions that have the same ID: %s' %
                impact_function_id)
        return impact_functions[0].instance()

    def filter(self, hazard_metadata=None, exposure_metadata=None):
        """Get available impact functions from hazard and exposure metadata.

        Disabled impact function will not be loaded.

        .. example::

            if_manager = ImpactFunctionManager()
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
            ifs =  if_manager.filter(hazard_metadata, exposure_metadata)

        :param hazard_metadata: The metadata of the hazard.
        :type hazard_metadata: dict

        :param exposure_metadata: The metadata of the exposure.
        :type exposure_metadata: dict
        """
        return self.registry.filter(hazard_metadata, exposure_metadata)

    def filter_by_keywords(
            self, hazard_keywords=None, exposure_keywords=None):
        """Get available impact functions from hazard and exposure keywords.

        Disabled impact function will not be loaded.

        .. example::

            if_manager = ImpactFunctionManager()
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
            ifs =  if_manager.filter_by_keywords(hazard_keywords,
            exposure_keywords)

        :param hazard_keywords: The keywords of the hazard.
        :type hazard_keywords: dict

        :param exposure_keywords: The keywords of the exposure.
        :type exposure_keywords: dict
        """
        return self.registry.filter_by_keyword_string(
            hazard_keywords, exposure_keywords)

    def filter_by_metadata(self, metadata_key, metadata_value):
        """Return IF classes given its metadata key and value.

        .. example::

            if_manager = ImpactFunctionManager()
            metadata_key = 'author'
            metadata_value = 'Akbar Gumbira'
            ifs =  if_manager.filter_by_metadata(metadata_key,
            metadata_value)

        :param metadata_key: The key of the metadata e.g 'id', 'name'
        :type metadata_key: str

        :param metadata_value: The value of the metadata, e.g for the key
            'id' the value is 'FloodNativePolygonExperimentalFunction'
        :type metadata_value: str, dict

        :return: Impact Function classes match the arguments
        :rtype: list
        """
        return self.registry.filter_by_metadata(metadata_key, metadata_value)

    @staticmethod
    def get_function_id(impact_function):
        """Get the ID of the impact function.

        :param impact_function: Class of an impact function
        :type impact_function: safe.impact_functions.base.ImpactFunction

        :returns: The ID of the impact function specified in its metadata.
        :rtype: str
        """
        return impact_function.metadata().as_dict().get('id', None)

    @staticmethod
    def get_function_title(impact_function):
        """Get title of the impact function.

        :param impact_function: Class of an impact function
        :type impact_function: safe.impact_functions.base.ImpactFunction

        :returns: The title of the impact function specified in its metadata.
        :rtype: str
        """
        return impact_function.metadata().as_dict().get('title', None)

    @staticmethod
    def get_function_name(impact_function):
        """Get the human readable name of the impact function.

        :param impact_function: Class of an impact function.
        :type impact_function: safe.impact_functions.base.ImpactFunction
        """
        return impact_function.metadata().as_dict().get('name', None)

    @staticmethod
    def get_function_type(impact_function):
        """Return the impact function type.

        :param impact_function: The impact function.
        :type impact_function: safe.impact_functions.base.ImpactFunction
        """
        return impact_function.function_type()

    def get_functions_for_hazard(self, hazard):
        """Return all function metadata that has hazard in their metadata.

        .. versionadded:: 2.2

        :param hazard: Dictionary that represent the hazard
        :type hazard: dict

        :return: List of impact function metadata.
        :rtype: list
        """
        impact_functions_metadata = []
        for impact_function in self.impact_functions:
            if impact_function.metadata().has_hazard(hazard):
                impact_functions_metadata.append(
                    impact_function.metadata().as_dict())

        return impact_functions_metadata

    def purposes_for_layer(self, layer_geometry_key):
        """Get purposes of a layer geometry id.

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        """
        layer_purposes = []
        for impact_function in self.impact_functions:
            if_layer_purposes = impact_function.metadata().purposes_for_layer(
                layer_geometry_key)
            if if_layer_purposes:
                add_to_list(layer_purposes, if_layer_purposes)

        return layer_purposes

    def hazard_categories_for_layer(self, layer_geometry_key, hazard_key=None):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :param hazard_key: The hazard key
        :type hazard_key: str

        :returns: List of hazard_categories
        :rtype: list
        """
        hazard_categories = []
        for impact_function in self.impact_functions:
            if_hazard_categories = impact_function.metadata()\
                .hazard_categories_for_layer(layer_geometry_key, hazard_key)
            if if_hazard_categories:
                add_to_list(hazard_categories, if_hazard_categories)

        return hazard_categories

    def hazards_for_layer(self, layer_geometry_key, hazard_category_key=None):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :param hazard_category_key: The hazard category
        :type hazard_category_key: str

        :returns: List of hazard
        :rtype: list
        """
        hazards = []
        for impact_function in self.impact_functions:
            if_hazards = impact_function.metadata().hazards_for_layer(
                layer_geometry_key, hazard_category_key)
            if if_hazards:
                add_to_list(hazards, if_hazards)

        return hazards

    def exposures_for_layer(self, layer_geometry_key):
        """Get hazard categories form layer_geometry_key

        :param layer_geometry_key: The geometry id
        :type layer_geometry_key: str

        :returns: List of hazard
        :rtype: list
        """
        exposures = []
        for impact_function in self.impact_functions:
            if_exposures = impact_function.metadata().exposures_for_layer(
                layer_geometry_key)
            if if_exposures:
                add_to_list(exposures, if_exposures)

        return exposures

    def exposure_units_for_layer(
            self, exposure_key, layer_geometry_key, layer_mode_key):
        """Get hazard categories form layer_geometry_key

        :param exposure_key: The exposure key
        :type exposure_key: str

        :param layer_geometry_key: The geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :returns: List of exposure unit
        :rtype: list
        """
        exposure_units = []
        for impact_function in self.impact_functions:
            if_exposure_units = impact_function.metadata().\
                exposure_units_for_layer(
                    exposure_key, layer_geometry_key, layer_mode_key)
            if if_exposure_units:
                add_to_list(exposure_units, if_exposure_units)

        return exposure_units

    def continuous_hazards_units_for_layer(
            self, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get continuous hazard units.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of continuous hazard unit
        :rtype: list
        """
        continuous_hazards_units = []
        for impact_function in self.impact_functions:
            if_continuous_hazard_units = impact_function.metadata().\
                continuous_hazards_units_for_layer(
                    hazard_key, layer_geometry_key, layer_mode_key,
                    hazard_category_key)
            if if_continuous_hazard_units:
                add_to_list(
                    continuous_hazards_units, if_continuous_hazard_units)

        return continuous_hazards_units

    def vector_hazards_classifications_for_layer(
            self, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get continuous hazard units.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of vector_hazards_classifications
        :rtype: list
        """
        vector_hazards_classifications = []
        for impact_function in self.impact_functions:
            if_vector_hazards_classifications = impact_function.metadata().\
                vector_hazards_classifications_for_layer(
                    hazard_key, layer_geometry_key, layer_mode_key,
                    hazard_category_key)
            if if_vector_hazards_classifications:
                add_to_list(
                    vector_hazards_classifications,
                    if_vector_hazards_classifications)

        return vector_hazards_classifications

    def raster_hazards_classifications_for_layer(
            self, hazard_key, layer_geometry_key, layer_mode_key,
            hazard_category_key):
        """Get continuous hazard units.
        :param hazard_key: The hazard key
        :type hazard_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of raster_hazards_classifications
        :rtype: list
        """
        raster_hazards_classifications = []
        for impact_function in self.impact_functions:
            if_vector_hazards_classifications = impact_function.metadata().\
                raster_hazards_classifications_for_layer(
                    hazard_key, layer_geometry_key, layer_mode_key,
                    hazard_category_key)
            if if_vector_hazards_classifications:
                add_to_list(
                    raster_hazards_classifications,
                    if_vector_hazards_classifications)

        return raster_hazards_classifications

    def available_hazards(self, hazard_category_key, ascending=True):
        """available_hazards from hazard_category_key

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :param ascending: Sort ascending or not.
        :type ascending: bool

        :returns: List of available hazards
        :rtype: list
        """

        hazards = []
        for impact_function in self.impact_functions:
            if_hazards = impact_function.metadata(). \
                available_hazards(hazard_category_key)
            if if_hazards:
                add_to_list(hazards, if_hazards)

        # make it sorted
        if ascending and hazards:
            hazards = sorted(hazards, key=lambda k: k['key'])

        return hazards

    def available_exposures(self, ascending=True):
        """Return a list of valid available exposures

        :param ascending: Sort ascending or not.
        :type ascending: bool

        :returns: A list of exposures full metadata.
        :rtype: list
        """

        exposures = []
        for impact_function in self.impact_functions:
            if_exposures = impact_function.metadata().available_exposures()
            if if_exposures:
                add_to_list(exposures, if_exposures)

        # make it sorted
        if ascending and exposures:
            exposures = sorted(exposures, key=lambda k: k['key'])

        return exposures

    def functions_for_constraint(
            self, hazard_key, exposure_key, hazard_geometry_key=None,
            exposure_geometry_key=None, hazard_mode_key=None,
            exposure_mode_key=None):
        """Obtain all functions that match with the constraints

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param exposure_key: the exposure key
        :type exposure_key: str

        :param hazard_geometry_key: The hazard geometry key
        :type hazard_geometry_key: str

        :param exposure_geometry_key: The exposure geometry key
        :type exposure_geometry_key: str

        :param hazard_mode_key: The hazard mode key
        :type hazard_mode_key: str

        :param exposure_mode_key: The exposure mode key
        :type exposure_mode_key: str

        :returns: List of matched Impact Function
        :rtype: list
        """
        impact_functions = []
        for impact_function in self.impact_functions:
            if impact_function.metadata().is_function_for_constraint(
                    hazard_key, exposure_key, hazard_geometry_key,
                    exposure_geometry_key, hazard_mode_key, exposure_mode_key):
                impact_functions.append(impact_function.metadata().as_dict())

        return impact_functions

    def available_hazard_constraints(
            self, hazard_key, hazard_category_key):
        """Get hazard constraints for hazard_key and hazard_category_key

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of tuple of layer_mode and layer_geometry
        :rtype: list
        """
        hazard_constraints = []
        for impact_function in self.impact_functions:
            if_hazard_constraints = impact_function.metadata().\
                available_hazard_constraints(
                    hazard_key, hazard_category_key)
            if if_hazard_constraints:
                add_to_list(hazard_constraints, if_hazard_constraints)

        return hazard_constraints

    def available_exposure_constraints(self, exposure_key):
        """Get exposure constraints for exposure_key.

        :param exposure_key: The exposure key
        :type exposure_key: str

        :returns: List of tuple of layer_mode and layer_geometry
        :rtype: list
        """
        exposure_constraints = []
        for impact_function in self.impact_functions:
            if_exposure_constraints = impact_function.metadata(). \
                available_exposure_constraints(exposure_key)
            if if_exposure_constraints:
                add_to_list(exposure_constraints, if_exposure_constraints)

        return exposure_constraints

    def available_hazard_layer_modes(
            self, hazard_key, hazard_geometry_key, hazard_category_key):
        """Return all available layer_mode.

        :param hazard_key: The hazard key
        :type hazard_key: str

        :param hazard_geometry_key: The hazard geometry key
        :type hazard_geometry_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :returns: List of layer_mode
        :rtype: list
        """
        layer_modes = []
        for impact_function in self.impact_functions:
            if_hazard_layer_mode = impact_function.metadata().\
                available_hazard_layer_mode(
                    hazard_key, hazard_geometry_key, hazard_category_key)
            if if_hazard_layer_mode:
                add_to_list(layer_modes, if_hazard_layer_mode)

        return layer_modes

    def available_exposure_layer_modes(
            self, exposure_key, exposure_geometry_key):
        """Get exposure layer mode for exposure_key.

        :param exposure_key: The exposure key
        :type exposure_key: str

        :param exposure_geometry_key: The exposure geometry key
        :type exposure_geometry_key: str

        :returns: List of layer_mode
        :rtype: list
        """
        layer_modes = []
        for impact_function in self.impact_functions:
            if_exposure_layer_mode = impact_function.metadata().\
                available_exposure_layer_mode(
                    exposure_key, exposure_geometry_key)
            if if_exposure_layer_mode:
                add_to_list(layer_modes, if_exposure_layer_mode)

        return layer_modes

    def hazard_additional_keywords(
            self, layer_mode_key=None, layer_geometry_key=None,
            hazard_category_key=None, hazard_key=None):
        """Return additional_keywords for hazard.

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param hazard_category_key: The hazard category key
        :type hazard_category_key: str

        :param hazard_key: The hazard key
        :type hazard_key: str

        :returns: List of additional keywords
        :rtype: list
        """
        additional_keywords = []
        for impact_function in self.impact_functions:
            if_additional_keywords = impact_function.metadata().\
                hazard_additional_keywords(
                    layer_mode_key=layer_mode_key,
                    layer_geometry_key=layer_geometry_key,
                    hazard_category_key=hazard_category_key,
                    hazard_key=hazard_key)
            if if_additional_keywords:
                add_to_list(additional_keywords, if_additional_keywords)

        return additional_keywords

    def exposure_additional_keywords(
            self, layer_mode_key=None, layer_geometry_key=None,
            exposure_key=None):
        """Return additional_keywords for exposure.

        :param layer_mode_key: The layer mode key
        :type layer_mode_key: str

        :param layer_geometry_key: The layer geometry key
        :type layer_geometry_key: str

        :param exposure_key: The hazard key
        :type exposure_key: str

        :returns: List of additional keywords
        :rtype: list
        """
        additional_keywords = []
        for impact_function in self.impact_functions:
            if_additional_keywords = impact_function.metadata().\
                exposure_additional_keywords(
                    layer_mode_key=layer_mode_key,
                    layer_geometry_key=layer_geometry_key,
                    exposure_key=exposure_key)
            if if_additional_keywords:
                add_to_list(additional_keywords, if_additional_keywords)

        return additional_keywords
