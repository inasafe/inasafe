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

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.metadata import hazard_definition, exposure_definition
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.utilities import add_to_list


class ImpactFunctionManager:
    """Class for managing metadata for all impact function.

    .. versionadded:: 2.1
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
                if not is_disabled:
                    result.append(impact_function)
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
            my_categories = impact_function.Metadata \
                .categories_for_layer(layer_type, data_type)
            result = add_to_list(result, my_categories)
        categories_definitions = []
        for my_category in result:
            if my_category == 'hazard':
                categories_definitions.append(hazard_definition)
            elif my_category == 'exposure':
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
            my_subcategories = impact_function.Metadata \
                .subcategories_for_layer(category, layer_type, data_type)
            result = add_to_list(result, my_subcategories)
        return result
