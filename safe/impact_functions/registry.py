# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact Function Registry.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com, akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '01/03/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.common.utilities import is_subset, convert_to_list, project_list


class Registry(object):
    """A simple registry for keeping track of all impact functions.

    We will use a singleton pattern to ensure that there is only
    one canonical registry. The registry can be used by impact functions
    to register themselves and their GUID's.

    To get the impact functions, please do not use directly from this Registry,
    but rather user ImpactFunctionManager.
    """

    _instance = None
    _impact_functions = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Registry, cls).__new__(cls, *args, **kwargs)
            cls._impact_functions = []
        return cls._instance

    @property
    def impact_functions(self):
        """Return all registered impact functions."""
        return self._impact_functions

    @classmethod
    def register(cls, impact_function):
        """Register an impact function to the Registry.

        Impact Function that will be registered has to have a unique id that
        is not registered yet.

        :param impact_function: The impact function to register.
        :type impact_function: ImpactFunction.
        """
        is_disabled = impact_function.metadata().is_disabled()
        is_valid, reason = impact_function.metadata().is_valid()
        impact_function_id = impact_function.metadata().as_dict()['id']
        if not is_disabled and is_valid and impact_function not in \
                cls._impact_functions:
            id_unique = cls.filter_by_metadata('id', impact_function_id) == []
            if id_unique:
                cls._impact_functions.append(impact_function)
            else:
                raise Exception('Impact Function with ID %s is already '
                                'registered' % impact_function_id)

    @classmethod
    def clear(cls):
        """Remove all registered impact functions in the registry."""
        cls._impact_functions = []

    @classmethod
    def list(cls):
        """List of all registered impact functions by their name."""
        return [
            impact_function.metadata().as_dict()['name'] for impact_function in
            cls._impact_functions]

    @classmethod
    def get_instance(cls, name):
        """Return an instance of impact function given its class name.

        :param name: the name of IF class
        :type name: str

        :return: impact function instance
        :rtype: safe.impact_functions.base.ImpactFunction.instance()
        """
        return cls.get_class(name).instance()

    @classmethod
    def get_class(cls, name):
        """Return the class of an impact function given its class name.

        :param name: The class name of the IF.
        :type name: str

        :return: impact function class
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        for impact_function in cls._impact_functions:
            if impact_function.__name__ == name:
                return impact_function
        raise Exception('Impact function with the class name %s not found' %
                        name)

    @classmethod
    def filter_by_metadata(cls, metadata_key, metadata_value):
        """Return IF classes given its metadata key and value.

        :param metadata_key: The key of the metadata e.g 'id', 'name'
        :type metadata_key: str

        :param metadata_value: The value of the metadata, e.g for the key
            'id' the value is 'FloodNativePolygonExperimentalFunction'
        :type metadata_value: str, dict

        :return: impact function classes
        :rtype: list
        """
        impact_functions = []
        for impact_function in cls._impact_functions:
            if_metadata = impact_function.metadata().as_dict()
            if metadata_key in if_metadata:
                if if_metadata[metadata_key] == metadata_value:
                    impact_functions.append(impact_function)

        return impact_functions

    @classmethod
    def filter(cls, hazard_metadata=None, exposure_metadata=None):
        """Filter impact function given the hazard and exposure metadata.

        :param hazard_metadata: Dictionary represent hazard keywords
        :type hazard_metadata: dict

        :param exposure_metadata: Dictionary represent exposure keywords
        :type exposure_metadata: dict

        :returns: List of impact functions.
        :rtype: list

        """
        if hazard_metadata is None and exposure_metadata is None:
            return cls._impact_functions

        impact_functions = cls._impact_functions
        impact_functions = cls.filter_by_hazard(
            impact_functions, hazard_metadata)
        impact_functions = cls.filter_by_exposure(
            impact_functions, exposure_metadata)

        return impact_functions

    @staticmethod
    def filter_by_hazard(impact_functions, hazard_keywords):
        """Filter impact function by hazard_keywords.

        :param impact_functions: List of impact functions.
        :type impact_functions: list

        :param hazard_keywords: Dictionary represent hazard keywords.
        :type hazard_keywords: dict

        :returns: List of impact functions.
        :rtype: list
        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_hazard_keywords = impact_function.metadata().as_dict()[
                'categories']['hazard']
            subcategories = if_hazard_keywords['subcategories']
            units = if_hazard_keywords['units']
            layer_constraints = if_hazard_keywords['layer_constraints']

            if not is_subset(hazard_keywords['subcategory'], subcategories):
                continue
            if not is_subset(hazard_keywords['units'], units):
                continue
            if not is_subset(
                    hazard_keywords['layer_constraints'], layer_constraints):
                continue
            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions

    @staticmethod
    def filter_by_exposure(impact_functions, exposure_keywords):
        """Filter impact function by exposure_keywords.

        :param impact_functions: List of impact functions
        :type impact_functions: list

        :param exposure_keywords: Dictionary represent exposure keywords
        :type exposure_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_exposure_keywords = impact_function.metadata().as_dict()[
                'categories']['exposure']
            subcategory = if_exposure_keywords['subcategories']
            units = if_exposure_keywords['units']
            layer_constraints = if_exposure_keywords['layer_constraints']

            if not is_subset(exposure_keywords['subcategory'], subcategory):
                continue
            if not is_subset(exposure_keywords['units'], units):
                continue
            if not is_subset(
                    exposure_keywords['layer_constraints'], layer_constraints):
                continue
            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions

    @classmethod
    def filter_by_keyword_string(
            cls, hazard_keywords=None, exposure_keywords=None):
        """Get available impact functions from hazard and exposure keywords.

        Disabled impact function will not be loaded.

        :param hazard_keywords: The keywords of the hazard.
        :type hazard_keywords: dict

        :param exposure_keywords: The keywords of the exposure.
        :type exposure_keywords: dict
        """
        if hazard_keywords is None and exposure_keywords is None:
            return cls._impact_functions

        impact_functions = []
        categories = []
        keywords = {}
        if hazard_keywords is not None:
            categories.append('hazard')
            keywords['hazard'] = hazard_keywords
        if exposure_keywords is not None:
            categories.append('exposure')
            keywords['exposure'] = exposure_keywords

        for impact_function in cls._impact_functions:
            requirement_met = True
            for category in categories:
                f_category = impact_function.metadata().as_dict()[
                    'categories'][category]

                subcategories = f_category['subcategories']
                subcategories = project_list(
                    convert_to_list(subcategories), 'id')

                units = f_category['units']
                units = project_list(convert_to_list(units), 'id')

                layer_constraints = convert_to_list(
                    f_category['layer_constraints'])

                layer_types = project_list(layer_constraints, 'layer_type')
                data_types = project_list(layer_constraints, 'data_type')

                keyword = keywords[category]
                if keyword.get('subcategory') not in subcategories:
                    requirement_met = False
                    continue
                if (len(units) > 0 and keyword.get('unit') is not None and
                        keyword.get('unit') not in units):
                    requirement_met = False
                    continue
                if keyword.get('layer_type') not in layer_types:
                    requirement_met = False
                    continue
                if keyword.get('data_type') not in data_types:
                    requirement_met = False
                    continue

            if requirement_met and impact_function not in impact_functions:
                impact_functions.append(impact_function)

        return impact_functions
