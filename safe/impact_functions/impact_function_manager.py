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


from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.utilities import add_to_list


class ImpactFunctionManager:
    """Class for managing all impact function
    """

    def __init__(self):
        """Constructor
        """
        # attributes
        self.impact_functions = []
        self.load_impact_functions()

    def load_impact_functions(self):
        """Method to load all impact functions. It will not load impact
        function which disabled
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
        """Get the list of allowed subcategories for a given category from
        all impact functions

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
        """Get the list of allowed data types for a subcategory from all
        impact functions

        Passing a subcategory is required otherwise the context of the
        data_type (s) would be ambiguous (i.e. whether they can be used as
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
        """Get the list of allowed units for a subcategory and data_type from
        all impact functions

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