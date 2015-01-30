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

from safe.metadata import (
    hazard_definition,
    exposure_definition,
    layer_raster_numeric,
    layer_vector_polygon,
    layer_vector_line,
    layer_vector_point)
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.utilities import add_to_list


class ImpactFunctionManager:
    """Class for managing metadata for all impact function.

    .. versionadded:: 2.1

    #TODO: @ismailsunni please revise the api docs here and make sure
    everything is consistent and param and param types are correct. Thanks. Tim
    """

    def __init__(self):
        """Constructor."""
        # attributes
        self.impact_functions = []
        self.load_impact_functions()

    # noinspection PyUnresolvedReferences
    def load_impact_functions(self):
        """Load all impact functions.

        Disabled impact function will not be loaded.
        """
        result = []
        impact_functions = FunctionProvider.plugins
        for impact_function in impact_functions:
            try:
                is_disabled = impact_function.Metadata.is_disabled()
                is_valid, reason = impact_function.Metadata.is_valid()
                if not is_disabled and is_valid:
                    result.append(impact_function)
                if not is_valid:
                    print impact_function, reason
            except AttributeError:
                continue
        self.impact_functions = result

    def allowed_subcategories(self, category=None):
        """Determine allowed subcategories, optionally filtered by category.

        :param category: Optional category which will be used to subset the
            allowed subcategories. If omitted, all supported subcategories will
            be returned (for both hazard and exposure). Default is None.
        :type category: str

        :returns: A list of strings is returned.
        :rtype: list
        """
        result = []
        for impact_function in self.impact_functions:
            my_allowed_subcategories = impact_function.Metadata\
                .allowed_subcategories(category)
            result = add_to_list(result, my_allowed_subcategories)
        return result

    def allowed_data_types(self, subcategory):
        """Determine allowed data types for all impact functions.

        It uses subcategory as a filter.

        Passing a subcategory is required otherwise the context of the
        data_type(s) would be ambiguous (i.e. whether they can be used as
        exposure or hazards).

        :param subcategory: Required subcategory which will be used to subset
            the allowed data_types.
        :type subcategory: str

        :returns: A list of one or more strings is returned.
        :rtype: list
        """
        result = []
        for impact_function in self.impact_functions:
            my_allowed_data_types = impact_function.Metadata \
                .allowed_data_types(subcategory)
            result = add_to_list(result, my_allowed_data_types)
        return result

    def allowed_units(self, subcategory, data_type):
        """Determine allowed units from all impact functions.


        It uses subcategory and data_type as a filter.

        .. note:: One data_type could be  used by more than one subcategory,
            so we need to explicitly pass the subcategory to this function.

        :param subcategory: Required subcategory which will be used to subset
            the allowed data_types.
        :type subcategory: str

        :param data_type: Required data_type which will be used to subset the
            allowed units.
        :type data_type: str

        :returns: A list of one or more strings is returned.
        :rtype: list
        """
        result = []
        for impact_function in self.impact_functions:
            my_allowed_units = impact_function.Metadata \
                .allowed_units(subcategory, data_type)
            result = add_to_list(result, my_allowed_units)
        return result

    def units_for_layer(self, subcategory, layer_type, data_type):
        """Get the valid units for a layer.

        Example usage::

            foo  = units_for_layer('flood', 'vector', 'polygon')
            print foo

        Would output this::

            {'Wet/Dry': ['wet','dry']}

        While passing a raster layer::

            foo  = units_for_layer('flood', 'raster', None)
            print foo

        Might return this::

            {
                'metres': None,
                'feet': None,
                'wet/dry': ['wet', 'dry'],
            }

        In the returned dictionary the keys are unit types and
        the values are the categories (if any) applicable for that unit type.

        :param subcategory: The subcategory for this layer.
        :type subcategory: str

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon
            (for vectors).
        :type data_type: str

        :returns: A dictionary as per the example above where each key
            represents a unit and each value that is not None represents a
            list of categories.
        :rtype: dict
        """
        result = []
        for impact_function in self.impact_functions:
            my_units = impact_function.Metadata \
                .units_for_layer(subcategory, layer_type, data_type)
            result = add_to_list(result, my_units)
        return result

    def categories_for_layer(self, layer_type, data_type):
        """Return a list of valid categories for a layer.

        This method is used to determine if a given layer can be used as a
        hazard, exposure or aggregation layer.

        Example usage::

            foo  = categories_for_layer('vector', 'polygon')
            print foo

        Would output this::

            ['hazard', 'exposure', 'aggregation']

        While passing a vector point layer::

            foo  = units_for_layer('vector', 'point')
            print foo

        Might return this::

            ['hazard', 'exposure']

        In the returned the values are categories (if any) applicable for that
        layer_type and data_type.

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon
            (for vectors).
        :type data_type: str

        :returns: A list as per the example above where each value represents
            a valid category.
        :rtype: list
        """
        result = []
        for impact_function in self.impact_functions:
            categories = impact_function.Metadata \
                .categories_for_layer(layer_type, data_type)
            result = add_to_list(result, categories)
        categories_definitions = []
        for category in result:
            if category == 'hazard':
                categories_definitions.append(hazard_definition)
            elif category == 'exposure':
                categories_definitions.append(exposure_definition)
            else:
                raise Exception('Unsupported categories')
        return categories_definitions

    def subcategories_for_layer(self, category, layer_type, data_type):
        """Return a list of valid subcategories for a layer.

        This method is used to determine which subcategories a given layer
        can be for.

        Example usage::

            foo  = subcategories_for_layer('vector', 'polygon', 'exposure')
            print foo

        Would output this::

            ['flood', 'landuse']

        In the returned the values are categories (if any) applicable for that
        layer_type and data_type.

        :param layer_type: The type for this layer. Valid values would be,
            'raster' or 'vector'.
        :type layer_type: str

        :param data_type: The data_type for this layer. Valid possibilities
            would be 'numeric' (for raster), point, line, polygon
            (for vectors).
        :type data_type: str

        :param category: The category for this layer. Valid possibilities
            would be 'hazard', 'exposure' and 'aggregation'.
        :type category: str


        :returns: A list as per the example above where each value represents
            a valid subcategory.
        :rtype: list
        """
        result = []
        for impact_function in self.impact_functions:
            subcategories = impact_function.Metadata \
                .subcategories_for_layer(category, layer_type, data_type)
            result = add_to_list(result, subcategories)
        return result

    def get_available_hazards(self, impact_function=None, ascending=True):
        """Return a list of valid available hazards for an impact function.

        If impact_function is None, return all available hazards

        .. versionadded:: 2.2

        :param impact_function: Impact Function object.
        :type impact_function: FunctionProvider

        :param ascending: Sort ascending or not.
        :type ascending: bool

        :returns: A list of hazard full metadata.
        :rtype: list
        """

        hazards = []
        if impact_function is None:
            for impact_function in self.impact_functions:
                add_to_list(hazards, impact_function.Metadata.get_hazards())

        else:
            # noinspection PyUnresolvedReferences
            hazards = impact_function.Metadata.get_hazards()

        # make it sorted
        if ascending:
            hazards = sorted(hazards, key=lambda k: k['id'])

        return hazards

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
            if impact_function.Metadata.has_hazard(hazard):
                impact_functions_metadata.append(
                    impact_function.Metadata.get_metadata())

        return impact_functions_metadata

    def get_functions_for_hazard_id(self, hazard_id):
        """Return all function metadata that has hazard_id in their metadata.

        .. versionadded:: 2.2

        :param hazard_id: String that represent the hazard id.
        :type hazard_id: str

        :return: List of impact function metadata.
        :rtype: list
        """
        impact_functions_metadata = []
        for impact_function in self.impact_functions:
            if impact_function.Metadata.has_hazard_id(hazard_id):
                impact_functions_metadata.append(
                    impact_function.Metadata.get_metadata())

        return impact_functions_metadata

    def get_available_exposures(self, impact_function=None, ascending=True):
        """Return a list of valid available exposures for an impact function.

        If impact_function is None, return all available exposures

        .. versionadded:: 2.2

        :param impact_function: Impact Function object.
        :type impact_function: FunctionProvider

        :param ascending: Sort ascending or not.
        :type ascending: bool

        :returns: A list of exposures full metadata.
        :rtype: list
        """

        exposures = []
        if impact_function is None:
            for impact_function in self.impact_functions:
                add_to_list(
                    exposures, impact_function.Metadata.get_exposures())

        else:
            # noinspection PyUnresolvedReferences
            exposures = impact_function.Metadata.get_exposures()

        # make it sorted
        if ascending:
            exposures = sorted(exposures, key=lambda k: k['id'])

        return exposures

    def get_functions_for_exposure(self, exposure):
        """Return all function metadata that has exposure in their metadata.

        .. versionadded:: 2.2

        :param exposure: Dictionary that represent the exposure
        :type exposure: dict

        :return: List of impact function metadata.
        :rtype: list
        """
        impact_functions_metadata = []
        for impact_function in self.impact_functions:
            if impact_function.Metadata.has_exposure(exposure):
                impact_functions_metadata.append(
                    impact_function.Metadata.get_metadata())

        return impact_functions_metadata

    def get_functions_for_exposure_id(self, exposure_id):
        """Return all function metadata that has exposure_id in their metadata.

        .. versionadded:: 2.2

        :param exposure_id: String that represent the exposure id.
        :type exposure_id: str

        :return: List of impact function metadata.
        :rtype: list
        """
        impact_functions_metadata = []
        for impact_function in self.impact_functions:
            if impact_function.Metadata.has_exposure_id(exposure_id):
                impact_functions_metadata.append(
                    impact_function.Metadata.get_metadata())

        return impact_functions_metadata

    def get_functions_for_constraint(
            self,
            hazard,
            exposure,
            hazard_constraint=None,
            exposure_constraint=None):
        """

        :param hazard:
        :param exposure:
        :param hazard_constraint:
        :param exposure_constraint:
        :return:
        """
        result = []
        if isinstance(hazard, basestring):
            hazard_functions = self.get_functions_for_hazard_id(hazard)
        else:
            hazard_functions = self.get_functions_for_hazard(hazard)

        if isinstance(exposure, basestring):
            exposure_functions = self.get_functions_for_exposure_id(exposure)
        else:
            exposure_functions = self.get_functions_for_exposure(exposure)

        for function in hazard_functions:
            if function in exposure_functions:
                constraints = function['categories']['hazard']['layer_constraints']
                if not hazard_constraint or hazard_constraint in constraints:
                    if (not exposure_constraint or exposure_constraint in
                            function['categories']['exposure']['layer_constraints']):
                        result.append(function)

        return result

    def available_functions(self, hazard_keywords, exposure_keywords):
        """Find out which impact functions match the hazard and exposure given.

        .. note:: :file:dock.py add_layer_type_to_keywords function must have
            been called first so that the keywords contain layer type
            and geometry info.

        ..versionadded:: 3.0.0

        :param hazard_keywords: Keywords accompanying the hazard layer. Only
            functions which support this hazard will be returned.
        :type hazard_keywords: dict

        :param exposure_keywords: Keywords accompanying the exposure layer.
            only functions which support this exposure will be returned.
        :type exposure_keywords: dict

        :returns: A list of impact functions (which may be empty if there are
            no valid ones matching the hazard and exposure).
        :rtype: list
        """

        if hazard_keywords['layertype'] == 'raster':
            # TODO: we need to support layer_raster_continuous and
            # TODO: layer_raster_classified rather
            hazard_constraint = layer_raster_numeric
        else:
            geometry_type = hazard_keywords['layer_geometry']
            if geometry_type == 'point':
                hazard_constraint = layer_vector_point
            elif geometry_type == 'line':
                # Currently no line hazards are supported
                # but for completeness we do this too
                hazard_constraint = layer_vector_line
            else:
                hazard_constraint = layer_vector_polygon

        if exposure_keywords['layertype'] == 'raster':
            # TODO: we need to support layer_raster_continuous and
            # TODO: layer_raster_classified rather
            exposure_constraint = layer_raster_numeric
        else:
            if geometry_type == 'point':
                exposure_constraint = layer_vector_point
            elif geometry_type == 'line':
                # Currently no line hazards are supported
                # but for completeness we do this too
                exposure_constraint = layer_vector_line
            else:
                exposure_constraint = layer_vector_polygon

        hazard = hazard_keywords['subcategory']
        exposure = exposure_keywords['subcategory']

        return self.get_functions_for_constraint(
            hazard,
            exposure,
            hazard_constraint,
            exposure_constraint
        )
